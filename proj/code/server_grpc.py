from concurrent import futures
import logging

import grpc
import file_pb2
import file_pb2_grpc
import threading
import sqlite3
import os
from queue import Queue, SimpleQueue

# TODO: should probably be using os.path.normpath (actually no I think this does opposite of what I want)
# To get normalized path formatting between Windows and Mac

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


    def Upload(self, request_iterator, context):
        # Creating byte array to reconstruct file
        file = bytearray()
        for request in request_iterator:
            # Pull meta information from header packet
            if request.HasField("meta"):
                user = request.meta.user
                # clock = request.meta.clock
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

                # Find occurences of file in database right now
                info = cur.execute("SELECT id, COUNT(id) FROM files WHERE src = ?", 
                            (os.path.join(filepath, filename), )).fetchall()
                
                # If it doesn't exist (never been uploaded before)
                if not info[0][0]:
                    # Create a new id
                    prev_id = cur.execute("SELECT MAX(id) FROM files").fetchone()[0]
                    if prev_id:
                        id = prev_id + 1
                    else:
                        id = 1

                    # Update ownership table
                    cur.execute("INSERT INTO ownership (username, file_id, permissions) VALUES (?, ?, ?)",
                                    (user, id, OWNER))
                    con.commit()
                
                # If it did exist, make sure to clean out super old versions
                else:
                    id, count = info[0]
                    # Remove oldest version if at capacity
                    if count and count == 3:
                        cur.execute("DELETE FROM files WHERE src = ? ORDER BY clock LIMIT 1",
                                    (os.path.join(filepath, filename), ))
                        con.commit()

                clock = cur.execute("SELECT clock FROM clock").fetchone()[0]
                print(clock)

                # Upload file
                cur.execute("INSERT INTO files (id, filename, filepath, src, file, MAC, hash, clock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (id, filename, filepath, os.path.join(filepath, filename), file, MAC, hash, clock, ))
                con.commit()

                # Update clock
                cur.execute("UPDATE clock SET clock = ((SELECT clock FROM clock) + 1)")
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
            print(filename, client_file.filename, filepath, client_file.filepath)
            if not(filename == client_file.filename and filepath == client_file.filepath):
                continue
            else:
                # So we have a problem here right now
                if clock > latest_clock:
                    latest_clock = clock
                    latest_hash = hash
                if hash == client_file.hash:
                    print("Match!")
                    found = True
        print("Mismatch here somehow, don't even know how that's possible")
        print(client_file.hash, latest_hash)     
        # If latest version is local version, return latest   
        if client_file.hash == latest_hash:
            print("returned latest")
            return "latest"
    
        # If otherwise found but not latest, we have an old version
        if found:
            return "outdated"
        
        # Otherwise we have a very old version, or a new version?
        return "outdated"
        
            

    # pulls messages from server to client

    # Logic sketch
    # For each piece of client data (their file)
    # Check version of local file against online files
    # If exists but not latest, should pull
    # If exists and is latest, skip to next

    # If there's a file they don't have, pull latest version!

    def Sync(self, request, context):
        print("attempt sync")
        user = request.user
        md = request.metadata
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # Pulling file ids that they have access to
                file_ids = cur.execute("SELECT file_id FROM ownership WHERE username = ?",
                                         (request.user, )).fetchall()
                print(f"file_ids {file_ids}")

                # Extracting ids from tuples
                file_ids = list(map(lambda x: x[0], file_ids))

                # Slightly odd fix to Python not allowing single element tuples
                file_ids.append(-1)

                # Pull all file information that they have access to
                # A little bit weird but need this tuple syntax for IN queries
                query = "SELECT filename, filepath, file, MAC, hash, clock FROM files WHERE id IN {}".format(tuple(file_ids))
                files = cur.execute(query).fetchall()

                # Going to keep track of up-to-date local files. This will allow us to pull files
                # That they don't have stored locally
                # Again pulling trick that there must be at least two items in tuple to behave nicely
                synced_local_files = [-2, -1]
                if md:
                    for client_file in md:
                        # TODO: This isn't working as intended
                        print(f"client_file: {client_file}")
                        status = self.file_match(client_file, files) 
                        if status == "latest":
                            # Update array
                            synced_local_files.append(os.path.join(client_file.filepath, client_file.filename))
                    # TODO: Patrick do I need any other cases here? If I don't have the latest file,
                    # I should always just be pulling right? Also could do with a logic check on my helper function


                # Attempting to get all the files I need to pull
                # TODO: Think this is gonna have an error with the file path, might be ok though, just think
                # this isn't Mac-Windows compatible (i.e. will work if all Windows or all Mac, but otherwise problems)
                print(f"Synced local files: {synced_local_files}")
                query = """ SELECT filename, filepath, file, MAC, hash, clock 
                            FROM files 
                            WHERE (id, clock) IN 
                            ( 
                                SELECT id, MAX(clock)
                                FROM files
                                GROUP BY id
                            )
                            AND id IN {}
                            AND src NOT IN {}""".format(tuple(file_ids), tuple(synced_local_files))
                # Broke something here WHY
                to_pull_files = cur.execute(query).fetchall()
                print(f"To pull: {to_pull_files}")
                send_queue = Queue()
                if not(to_pull_files):
                    send_queue.put(file_pb2.SyncReply(will_receive=False))

                for file in to_pull_files:
                    filename, filepath, file, MAC, hash, clock = file
                    
                    
                    send_queue.put(file_pb2.SyncReply(meta=file_pb2.Metadata(
                        clock=clock,
                        user=user,
                        hash=hash,
                        MAC=MAC,
                        filename=filename,
                        filepath=filepath
                    )))

                    # Yield metadata for file

                    chunk_size = 10 * 1024 # 10KB
                    for i in range(0, len(file), chunk_size):
                        end = i + chunk_size if i + chunk_size < len(file) else len(file) -1
                        send_queue.put(file_pb2.SyncReply(file=file[i:end]))
                send_queue.put(None)
                return iter(send_queue.get, None)
                                            

                # https://stackoverflow.com/questions/43075449/split-binary-string-into-31bit-strings


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
                    id INTEGER,
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