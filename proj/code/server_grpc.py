from concurrent import futures
import logging

import grpc
import file_pb2
import file_pb2_grpc
import threading
import sqlite3
import os
from queue import Queue, SimpleQueue

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

EMPTY = file_pb2.Empty()

# Size of chunks to stream (must match client_grpc.py)
CHUNK_SIZE = 1024 * 10

# ADJUSTABLE PARAMETERS BELOW:

# set to true to wipe messages/users database on next run
RESET_DB = False

# set server address
BASE_PORT = 50051


class ClientHandler(file_pb2_grpc.ClientHandlerServicer):
    def __init__(self, backups):
        self.backups = backups

    # get backup servers
    def GetBackups(self, request, context):
        response = file_pb2.BackupReply(status=0, errormessage="")
        for backup in self.backups:
            response.serverinfo.append(file_pb2.ServerInfo(host=backup["host"], port=backup["port"]))
        return response

    # logs a user in
    def Login(self, request, context):
        return file_pb2.LoginReply(status=SUCCESS,
                                   errormessage=NO_ERROR,
                                   user=request.user)

    # lists files available to you
    def List(self, request, context):
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()

            # no real way for this to fail so just set as SUCCESS
            files = file_pb2.ListReply(status=SUCCESS,
                                       errormessage="")

            # pull available files according to current user token
            files_available = cur.execute("""
                                          SELECT filename
                                          FROM files
                                          WHERE id IN
                                          (
                                              SELECT file_id
                                              FROM ownership
                                              WHERE username = ?
                                          )
                                          """,
                                            (request.user, )).fetchall()
            for file in files_available:
                files.files.append(file[0])

            return files

    # deletes a user from the database
    def Delete(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # remove all ownerships related to this user
                cur.execute("""
                            DELETE FROM ownership
                            WHERE username = ?""",
                            (request.user, ))
                con.commit()

                # forget about all files which nobody owns
                cur.execute("""
                            DELETE FROM files
                            WHERE id NOT IN
                            (
                                SELECT file_id
                                FROM ownership
                            )
                            """)
                con.commit()

                # Write changes to backups
                worker = ServerWorker(self.backups)
                worker.delete_helper(request.user)

        return file_pb2.DeleteReply(status=SUCCESS,
                                    errormessage=NO_ERROR,
                                    user=request.user)

    def Check(self, request, context):
        return file_pb2.CheckReply(status=SUCCESS, errormessage="", sendupdate=True)

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

        # Standardize file paths:
        unsafe_src = os.path.join(filepath, filename)
        safe_src = unsafe_src.replace("\\", "/")
        safe_path = filepath.replace("\\", "/")

        # Update databse
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # Find occurences of file in database right now
                info = cur.execute("""
                                   SELECT id, COUNT(id)
                                   FROM files
                                   WHERE src = ?""",
                            (safe_src, )).fetchall()

                # If it doesn't exist (never been uploaded before)
                if not info[0][0]:
                    print("hitting wrong case")
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

                    # Write change to backups
                    worker = ServerWorker(self.backups)
                    worker.upload_add_new(user, id)

                # If it did exist, make sure to clean out super old versions
                else:
                    id, count = info[0]
                    # Remove oldest version if at capacity
                    if count and count >= 3:
                        # TODO: Check if this is deleting oldest or newest
                        cur.execute("""DELETE FROM files WHERE src = ?
                                        AND clock IN (
                                            SELECT clock
                                            FROM files
                                            WHERE src = ?
                                            LIMIT ?
                                        )""", (safe_src, safe_src, count - 2, ))
                        con.commit()

                        # Write change to backups
                        worker = ServerWorker(self.backups)
                        worker.upload_remove_old(safe_src, count - 2)

                clock = cur.execute("SELECT current_clock FROM server_clock").fetchone()[0]
                meta = file_pb2.Metadata(
                    clock=clock,
                    user=user,
                    hash=hash,
                    MAC=MAC,
                    filename=filename,
                    filepath=safe_path
                )

                # Upload file
                cur.execute("INSERT INTO files (id, filename, filepath, src, file, MAC, hash, clock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (id, filename, safe_path, safe_src, file, MAC, hash, clock, ))
                con.commit()

                # Update clock
                cur.execute("UPDATE server_clock SET current_clock = ((SELECT current_clock FROM server_clock) + 1)")
                con.commit()

                # Write changes to backups
                worker = ServerWorker(self.backups)
                worker.upload_helper(id, meta, safe_src, file)

        return file_pb2.UploadReply(status=SUCCESS, errormessage=NO_ERROR, success=True)

    def __latest_ver(self, md, files):
        latest_hash = None
        latest_clock = -1
        found = False
        for file in files:
            filename, filepath, file, MAC, hash, clock = file
            if not(filename == md.filename and filepath == md.filepath):
                continue
            else:
                if clock > latest_clock:
                    latest_clock = clock
                    latest_hash = hash
                if hash == md.hash:
                    found = True

        # If latest version is local version, return latest
        if md.hash == latest_hash:
            return True

        # If otherwise found but not latest, we have an old version
        if found:
            return False

        # Otherwise we have a very old version, or a new version?
        return False

    # pulls messages from server to client

    # Logic sketch
    # For each piece of client data (their file)
    # Check version of local file against online files
    # If exists but not latest, should pull
    # If exists and is latest, skip to next

    # If there's a file they don't have, pull latest version!

    def Sync(self, request, context):
        print("\n\n--- attempt sync ---")
        user = request.user
        md_stream = request.metadata
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()

                # Pulling file ids that they have access to
                file_ids = cur.execute("SELECT file_id FROM ownership WHERE username = ?",
                                         (user, )).fetchall()
                print(f"file_ids {file_ids}")

                # Extracting ids from tuples
                file_ids = list(map(lambda x: x[0], file_ids))

                # Slightly odd fix to Python not allowing single element tuples
                file_ids.append(-1)
                file_ids.append(-2)

                # Pull all file information that they have access to
                # A little bit weird but need this tuple syntax for IN queries
                query = "SELECT filename, filepath, file, MAC, hash, clock FROM files WHERE id IN {}".format(tuple(file_ids))
                files = cur.execute(query).fetchall()

                # Going to keep track of up-to-date local files. This will allow us to pull files
                # That they don't have stored locally
                # Again pulling trick that there must be at least two items in tuple to behave nicely
                synced_local_files = []
                if md_stream:
                    for md in md_stream:
                        if self.__latest_ver(md, files):
                            # Update array
                            synced_local_files.append(os.path.join(md.filepath, md.filename).replace("\\", "/"))
 
                synced_local_files.append("1")
                synced_local_files.append("0")

                # Attempting to get all the files I need to pull
                print(f"Synced local files: {synced_local_files}")
                query = """ SELECT filename, filepath, src, file, MAC, hash, clock
                            FROM files
                            WHERE src NOT IN {}
                            AND (id, clock) IN
                            (
                                SELECT id, MAX(clock)
                                FROM files
                                GROUP BY id
                            )
                            AND id IN {}""".format(tuple(synced_local_files), tuple(file_ids), )
                try:
                    to_pull_files = cur.execute(query).fetchall()
                except Exception as e:
                    print(e)
                if to_pull_files:
                    print(f"To pull: {to_pull_files}")
                else:
                    print("Nothing to pull")

                send_queue = Queue()
                if not(to_pull_files):
                    send_queue.put(file_pb2.SyncReply(will_receive=False))

                for file in to_pull_files:
                    filename, filepath, src, file, MAC, hash, clock = file

                    send_queue.put(file_pb2.SyncReply(meta=file_pb2.Metadata(
                        clock=clock,
                        user=user,
                        hash=hash,
                        MAC=MAC,
                        filename=filename,
                        filepath=filepath
                    )))

                    # Yield metadata for file
                    for i in range(0, len(file), CHUNK_SIZE):
                        end = i + CHUNK_SIZE if i + CHUNK_SIZE < len(file) else len(file)
                        send_queue.put(file_pb2.SyncReply(file=file[i:end]))
                send_queue.put(None)
                return iter(send_queue.get, None)

                # https://stackoverflow.com/questions/43075449/split-binary-string-into-31bit-strings

    def UploadAddNew(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO ownership (username, file_id, permissions) VALUES (?, ?, ?)",
                                (request.user, request.id, OWNER))
                con.commit()
        return EMPTY

    def UploadRemoveOld(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("""
                            DELETE FROM files WHERE src = ?
                            AND clock IN
                            (
                                SELECT clock
                                FROM files
                                WHERE src = ?
                                LIMIT ?
                            )""", (request.src, request.src, request.count_minus_2, ))
                con.commit()
        return EMPTY

    def UploadHelper(self, request, context):
        print("IN UploadHelper")
        print(request)
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO files (id, filename, filepath, src, file, MAC, hash, clock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (request.id,
                             request.meta.filename,
                             request.meta.filepath,
                             request.src,
                             request.file,
                             request.meta.MAC,
                             request.meta.hash,
                             request.meta.clock, ))
                con.commit()
                cur.execute("UPDATE server_clock SET current_clock = ((SELECT current_clock FROM server_clock) + 1)")
                con.commit()
        return EMPTY

    def DeleteHelper(self, request, context):
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("""
                            DELETE FROM ownership
                            WHERE username = ?""",
                            (request.user, ))
                con.commit()
                cur.execute("""
                            DELETE FROM files
                            WHERE id NOT IN
                            (
                                SELECT file_id
                                FROM ownership
                            )
                            """)
                con.commit()
        return EMPTY

    def CheckClock(self, request, context):
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()
            clock = cur.execute("SELECT current_clock FROM server_clock").fetchall()[0][0]
            return file_pb2.Clock(clock=clock)

    def PullData(self, request, context):
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()
            clock = cur.execute("SELECT current_clock FROM server_clock").fetchall()[0][0]
            response = file_pb2.Data(clock=file_pb2.Clock(clock=clock))

            files = cur.execute("SELECT * FROM files").fetchall()
            for file in files:
                file_info = file_pb2.File(id=file[0],
                                          filename=file[1],
                                          filepath=file[2],
                                          src=file[3],
                                          file=file[4],
                                          MAC=file[5],
                                          hash=file[6],
                                          clock=file[7])
                response.files.append(file_info)

            ownerships = cur.execute("SELECT * FROM ownership").fetchall()
            for ownership in ownerships:
                ownership_info = file_pb2.Ownership(username=ownership[1],
                                                    file_id=ownership[2],
                                                    permissions=ownership[3])
                response.ownerships.append(ownership_info)

            return response

# class to duplicate adjustments to databases across all backups
# only apply to commands with SQL writes, so login/list/sync/etc. don't need these
class ServerWorker():
    def __init__(self, backups):
        self.backups = backups

    def upload_add_new(self, user, id):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = file_pb2_grpc.ClientHandlerStub(channel)
                stub.UploadAddNew(file_pb2.UploadAddNewRequest(user=user, id=id))
                channel.close()
            except Exception as e:
                logging.error(e)
                continue

    def upload_remove_old(self, src, count_minus_2):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = file_pb2_grpc.ClientHandlerStub(channel)
                stub.UploadRemoveOld(file_pb2.UploadRemoveOldRequest(src=src, count_minus_2=count_minus_2))
                channel.close()
            except Exception as e:
                logging.error(e)
                continue

    def upload_helper(self, id, meta, src, file):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = file_pb2_grpc.ClientHandlerStub(channel)
                stub.UploadHelper(file_pb2.UploadHelperRequest(id=id, meta=meta, src=src, file=bytes(file)))
                channel.close()
            except Exception as e:
                logging.error(e)
                continue

    def delete_helper(self, user):
        for backup in self.backups:
            try:
                channel = grpc.insecure_channel(backup["host"] + ":" + backup["port"])
                stub = file_pb2_grpc.ClientHandlerStub(channel)
                stub.DeleteHelper(file_pb2.DeleteRequest(user=user))
                channel.close()
            except Exception as e:
                logging.error(e)
                continue

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
    cur.execute("""CREATE TABLE IF NOT EXISTS server_clock
                (
                    current_clock INTEGER
                )""")
    con.commit()

    # Ensure we have a clock
    clock_check = cur.execute("""SELECT * FROM server_clock""").fetchall()
    if len(clock_check) == 0: 
        with lock:
            cur.execute("INSERT INTO server_clock (current_clock) VALUES (0)")
            con.commit()

    # clear database if desired
    if RESET_DB:
        cur.execute("DELETE FROM files")
        con.commit()
        cur.execute("DELETE FROM ownership")
        con.commit()

# Call to set up backups
def setup():
    global DATABASE_PATH

    # Give the server an id
    while True:
        id_input = input("Give this server an id (0-100): ")
        try:
            id = int(id_input)
            if id <= 100 and id >= 0:
                DATABASE_PATH = f"../data/server_{id}.db"
                break
        except:
            print("Provide a numerical input between 0 and 100 inclusive!")

    # Get number of backups
    while True:
        num_backups_input = input("Number of backup servers?: ")
        try:
            num_backups = int(num_backups_input)
            if (0 <= num_backups and num_backups <= 10):
                break
        except:
            print("Provide a numerical input between 0 and 10 inclusive!")

    # Setting up backups
    backups = []
    other_servers = []
    for i in range(num_backups):
        while True:
            try:
                backup_host = input(f"Backup Server #{i + 1} IP (default 127.0.0.1): ")
                backup_id = input(f"Backup Server #{i + 1} ID: ")
                if not backup_host:
                    backup_host = "127.0.0.1"
                backup_port = int(backup_id) + BASE_PORT
                if (BASE_PORT <= backup_port and backup_port <= BASE_PORT + 100):
                    backup_port = str(backup_port)
                    break
            except:
                print("Provide a numerical input for backup ID between 0 and 100 inclusive!")
        if int(backup_port) > BASE_PORT + id:
            backups.append({"host": backup_host, "port": backup_port})
        other_servers.append({"host": backup_host, "port": backup_port})
    backups.reverse()
    other_servers.reverse()
    return id, backups, other_servers

# pull most recent server data from backups
def restore_data(other_servers):
    best_server = None
    best_port = None
    with lock:
        with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()
            my_clock = cur.execute("SELECT current_clock FROM server_clock").fetchall()[0][0]
            best_clock = my_clock
    for server in other_servers:
        channel = grpc.insecure_channel(server["host"] + ":" + server["port"])
        stub = file_pb2_grpc.ClientHandlerStub(channel)
        response = stub.CheckClock(file_pb2.Empty())
        channel.close()
        if response.clock > best_clock:
            best_clock = response.clock
            best_server = server["host"]
            best_port = server["port"]
    if best_server and best_port:
        channel = grpc.insecure_channel(best_server + ":" + best_port)
        stub = file_pb2_grpc.ClientHandlerStub(channel)
        response = stub.PullData(file_pb2.Empty())
        channel.close()
        with lock:
            with sqlite3.connect(DATABASE_PATH) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM files")
                con.commit()
                cur.execute("DELETE FROM ownership")
                con.commit()
                for file in response.files:
                    cur.execute("INSERT INTO files (id, filename, filepath, src, file, MAC, hash, clock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (file.id, file.filename, file.filepath, file.src, file.file, file.MAC, file.hash, file.clock, ))
                    con.commit()
                for ownership in response.ownerships:
                    cur.execute("INSERT INTO ownership (username, file_id, permissions) VALUES (?, ?, ?)",
                                (ownership.username, ownership.file_id, ownership.permissions, ))
                    con.commit()
                cur.execute("UPDATE server_clock SET current_clock = ?", (response.clock.clock, ))

# runs the server logic
def serve():
    # initialize logs
    logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.DEBUG)

    # setup backups; this changes DATABASE_PATH
    id, backups, other_servers = setup()
    port = str(BASE_PORT + id)

    # initialize database
    init_db()

    # run server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_ClientHandlerServicer_to_server(ClientHandler(backups), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("server started, listening on " + port)

    input("Hit enter when all servers are up to sync the latest data across all replicas")
    restore_data(other_servers)

    # shut down nicely
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    serve()
