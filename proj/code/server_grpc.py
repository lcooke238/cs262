from concurrent import futures
import logging

import grpc
import file_pb2
import file_pb2_grpc
import threading
import sqlite3

# 3 uses serialized mode - can be used safely by multiple threads with no restriction
# Documentation/ and only answers seem to differ about this, so implementing a lock anyway
sqlite3.threadsafety = 3

lock = threading.Lock()

LOG_PATH = "../logs/server_grpc.log"
DATABASE_PATH = "../data/server.db"

# statuses
SUCCESS = 0
FAILURE = 1
SUCCESS_WITH_DATA = 2

# Database constants
OWNER = 10
EDITOR = 11

# error messages
NO_ERROR = ""
ERROR_DIFF_MACHINE = "user already logged in on different machine"
ERROR_NOT_LOGGED_IN = "user not currently logged in"
ERROR_DNE = "user does not exist :("

# ADJUSTABLE PARAMETERS BELOW:

# set to true to wipe messages/users database on next run
RESET_DB = False

# set server address
PORT = "50051"


class ClientHandler(file_pb2_grpc.ClientHandlerServicer):

    # logs a user in
    def Login(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # check whether already logged in
                logged_in = cur.execute("SELECT id FROM users WHERE username = ?",
                                        (request.user, )).fetchall()

                # user doesn't exist (returned empty list)
                if not logged_in:
                    cur.execute("INSERT INTO users (username) VALUES (?)",
                                (request.user, ))
                    con.commit()
                    return file_pb2.LoginReply(status=SUCCESS,
                                               errormessage=NO_ERROR,
                                               user=request.user)

                # User already existed
                return file_pb2.LoginReply(status=SUCCESS,
                                            errormessage=NO_ERROR,
                                            user=request.user)

    # logs a user out
    def Logout(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # they should be logged in to be able to run this,
                # but just checking to avoid errors
                logged_in = cur.execute("SELECT username FROM users WHERE user = ?",
                                        (request.user, )).fetchall()

                if logged_in and logged_in[0]:
                    cur.execute("UPDATE users SET online = FALSE WHERE user = ?",
                                (request.user, ))
                    con.commit()
                    return file_pb2.LogoutReply(status=SUCCESS,
                                                errormessage=NO_ERROR,
                                                user=request.user)

                return file_pb2.LogoutReply(status=FAILURE,
                                            errormessage=ERROR_NOT_LOGGED_IN,
                                            user=request.user)

    # deletes a user from the database
    def Delete(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # they should be logged in to be able to run this,
                # but just checking to avoid errors
                # logged_in = cur.execute("SELECT online FROM users WHERE user = ?",
                #                         (request.user, )).fetchall()

                # if logged_in:
                cur.execute("DELETE FROM users WHERE username = ?",
                            (request.user, ))
                con.commit()

                return file_pb2.DeleteReply(status=SUCCESS,
                                            errormessage=NO_ERROR,
                                            user=request.user)

    def Check(self, request, context):
        return file_pb2.CheckReply(status=SUCCESS, errormessage="", sendupdate=True)

    # def check_previous_version(user, filename, hash):
    #     with sqlite3.connect(DATABASE_PATH) as con:
    #             cur = con.cursor()
    #             cur.execute("SELECT user_id FROM ")

    # def Sync(self, request, context):


    def Upload(self, request_iterator, context):
        # Creating byte array to reconstruct file
        file = bytearray()
        for request in request_iterator:
            # Pull meta information from header packet
            if request.HasField("meta"):
                user = request.meta.user
                clock = request.meta.clock
                filename = request.meta.filename
                filepath = request.meta.filepath
                hash = request.meta.hash
                MAC = request.meta.MAC

            # Rebuild file
            if request.HasField("file"):
                file.extend(request.file)
        
        # Update databse
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # Upload file
                cur.execute("INSERT INTO files (filename, filepath, src, file, MAC, hash, clock) VALUES (?, ?, ?, ?, ?, ?)",
                            (filename, filepath, filepath + filename, file, MAC, hash, clock, ))
                con.commit()

                # Find file ID
                # TODO: Add ORDER ASC by clock or similar and use fetchone() to pull latest
                id = cur.execute("SELECT id FROM files WHERE filename = ? AND filepath = ? AND MAC = ? AND hash = ?",
                                 (filename, filepath, MAC, hash, )).fetchall()

                # Update ownership table
                cur.execute("INSERT INTO ownership (username, file_id, permissions) VALUES (?, ?, ?)",
                             (user, id[0][0], OWNER))
                con.commit()
                
        return file_pb2.UploadReply(status=SUCCESS, errormessage=NO_ERROR, success=True)

    # Lists users in the database using SQL wildcard syntax
    def ListUsers(self, request, context):
        wildcard = request.args.strip()
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()

            # no real way for this to fail so just set as SUCCESS
            user_list = file_pb2.ListReply(status=SUCCESS,
                                           wildcard=wildcard,
                                           errormessage="")

            # pull users according to SQL wildcard
            matched_users = cur.execute("SELECT user FROM users WHERE user LIKE ?",
                                        (wildcard, )).fetchall()
            for user in matched_users:
                user_list.user.append(user[0])

            return user_list

    # sends a message from one client to another
    def Send(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # check whether the name they gave to send to is valid user
                target_check = cur.execute("SELECT user FROM users WHERE user = ?",
                                           (request.user, ))
                if not target_check:
                    return file_pb2.SendReply(status=FAILURE,
                                              errormessage=ERROR_DNE,
                                              user=request.user,
                                              message=request.message,
                                              target=request.target)

                # put message into database
                cur.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)",
                            (request.user, request.message, request.target, ))
                con.commit()
                return file_pb2.SendReply(status=SUCCESS,
                                          errormessage=NO_ERROR,
                                          user=request.user,
                                          message=request.message,
                                          target=request.target)

    def file_match(self, client_file, files):
        latest_hash = None
        latest_clock = -1
        found = False
        for file in files:
            filename, filepath, file, MAC, hash, clock = file
            if not(filename == client_file.filename and filepath == client_file.filepath):
                continue
            else:
                if clock > latest_clock:
                    latest_clock = clock
                    latest_hash = hash
                if hash == client_file.hash:
                    found = True     
        # If latest version is local version, return latest   
        if client_file.hash == latest_hash:
            return "latest"
    
        # If otherwise found but not latest, we have an old version
        if found:
            return "outdated"
        
        # Otherwise we have a very old version, or a new version?
        return "outdated"
        
            

    # pulls messages from server to client
    def Sync(self, request, context):
        user = request.user
        md = request.metadata
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # Pulling file ids that they have access to
                file_ids = cur.execute("SELECT file_id FROM ownership WHERE username = ?",
                                         (request.user, )).fetchall()

                # Extracting ids from tuples
                file_ids = list(map(lambda x: x[0], file_ids))

                # Pull all file information that they have access to
                files = cur.execute("SELECT filename, filepath, file, MAC, hash, clock FROM files WHERE id IN ?",
                                     (file_ids, )).fetchall()

                # Going to keep track of up-to-date local files. This will allow us to pull files
                # That they don't have stored locally
                synced_local_files = []
                for client_file in md:
                    status = self.file_match(client_file, files) 
                    if status == "latest":
                        # Update array
                        synced_local_files.append(client_file.filepath + client_file.filename)
                    # TODO: Patrick do I need any other cases here? If I don't have the latest file,
                    # I should always just be pulling right? Also could do with a logic check on my helper function

                to_pull_files = cur.execute("""SELECT filename, filepath, file, MAC, hash, clock FROM files 
                                            WHERE id IN ? 
                                            AND NOT  filepath + filename IN ?
                                            GROUP BY """,
                                     (file_ids, synced_local_files, )).fetchall()



                # For each piece of client data (their file)
                # CHeck version of local file against online files
                # If exists but not latest, should pull
                # If exists and is latest, skip to next

                # If there's a file they don't have, pull latest version!


                # for md in request.metadata:
                #     if md.filename in files ...

                yield None


# takes the lock and sets all users offline
# def set_all_offline():
#     with lock:
#         with sqlite3.connect(DATABASE_PATH) as con:
#             cur = con.cursor()
#             cur.execute("UPDATE users SET online = FALSE")
#             con.commit()


# initializes database
def init_db():
    con = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cur = con.cursor()

    # create databases if necessary

    # File table, which stores all file information
    cur.execute("""CREATE TABLE IF NOT EXISTS files 
                (
                    id INTEGER PRIMARY KEY,
                    filename VARCHAR(100),
                    filepath VARCHAR(100),
                    src VARCHAR(200),
                    file BLOB,
                    MAC INTEGER,
                    hash BINARY,
                    clock INTEGER
                )""")
    con.commit()

    # Ownership table to associate users with files, allow shared ownership
    cur.execute("""CREATE TABLE IF NOT EXISTS ownership 
                (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(100),
                    file_id INTEGER,
                    permissions INTEGER
                )""")
    con.commit()

    # Server clock system
    cur.execute("""CREATE TABLE IF NOT EXISTS clock (
                    clock INTEGER
                )""")
    con.commit()
    
    # Ensure we have a clock
    clock_check = cur.execute("""SELECT * FROM clock""").fetchall()
    if len(clock_check) == 0: 
        with lock:
            cur.execute("INSERT INTO clock (clock) VALUES (0)")
            con.commit()

    # clear database if desired
    if RESET_DB:
        cur.execute("DELETE FROM files")
        con.commit()
        cur.execute("DELETE FROM ownership")
        con.commit()


# runs the server logic
def serve():
    # initialize logs
    logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

    # handling any weird crashes to ensure users can still log in
    # set_all_offline()

    # initialize database
    init_db()

    # run server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_ClientHandlerServicer_to_server(ClientHandler(), server)
    server.add_insecure_port('[::]:' + PORT)
    server.start()
    print("server started, listening on " + PORT)

    # shut down nicely
    try:
        server.wait_for_termination()
        # set_all_offline()
    except KeyboardInterrupt:
        pass
        # set_all_offline()


if __name__ == '__main__':
    serve()