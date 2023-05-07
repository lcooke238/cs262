# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import file_pb2 as file__pb2


class ClientHandlerStub(object):
    """The ClientHandler service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListUsers = channel.unary_unary(
                '/ClientHandler/ListUsers',
                request_serializer=file__pb2.ListRequest.SerializeToString,
                response_deserializer=file__pb2.ListReply.FromString,
                )
        self.Login = channel.unary_unary(
                '/ClientHandler/Login',
                request_serializer=file__pb2.LoginRequest.SerializeToString,
                response_deserializer=file__pb2.LoginReply.FromString,
                )
        self.List = channel.unary_unary(
                '/ClientHandler/List',
                request_serializer=file__pb2.ListRequest.SerializeToString,
                response_deserializer=file__pb2.ListReply.FromString,
                )
        self.Delete = channel.unary_unary(
                '/ClientHandler/Delete',
                request_serializer=file__pb2.DeleteRequest.SerializeToString,
                response_deserializer=file__pb2.DeleteReply.FromString,
                )
        self.Check = channel.unary_unary(
                '/ClientHandler/Check',
                request_serializer=file__pb2.CheckRequest.SerializeToString,
                response_deserializer=file__pb2.CheckReply.FromString,
                )
        self.Upload = channel.stream_unary(
                '/ClientHandler/Upload',
                request_serializer=file__pb2.UploadRequest.SerializeToString,
                response_deserializer=file__pb2.UploadReply.FromString,
                )
        self.Sync = channel.unary_stream(
                '/ClientHandler/Sync',
                request_serializer=file__pb2.SyncRequest.SerializeToString,
                response_deserializer=file__pb2.SyncReply.FromString,
                )
        self.GetBackups = channel.unary_unary(
                '/ClientHandler/GetBackups',
                request_serializer=file__pb2.BackupRequest.SerializeToString,
                response_deserializer=file__pb2.BackupReply.FromString,
                )
        self.UploadAddNew = channel.unary_unary(
                '/ClientHandler/UploadAddNew',
                request_serializer=file__pb2.UploadAddNewRequest.SerializeToString,
                response_deserializer=file__pb2.Empty.FromString,
                )
        self.UploadRemoveOld = channel.unary_unary(
                '/ClientHandler/UploadRemoveOld',
                request_serializer=file__pb2.UploadRemoveOldRequest.SerializeToString,
                response_deserializer=file__pb2.Empty.FromString,
                )
        self.UploadHelper = channel.unary_unary(
                '/ClientHandler/UploadHelper',
                request_serializer=file__pb2.UploadHelperRequest.SerializeToString,
                response_deserializer=file__pb2.Empty.FromString,
                )
        self.DeleteHelper = channel.unary_unary(
                '/ClientHandler/DeleteHelper',
                request_serializer=file__pb2.DeleteRequest.SerializeToString,
                response_deserializer=file__pb2.Empty.FromString,
                )
        self.CheckClock = channel.unary_unary(
                '/ClientHandler/CheckClock',
                request_serializer=file__pb2.Empty.SerializeToString,
                response_deserializer=file__pb2.Clock.FromString,
                )
        self.PullData = channel.unary_unary(
                '/ClientHandler/PullData',
                request_serializer=file__pb2.Empty.SerializeToString,
                response_deserializer=file__pb2.Data.FromString,
                )
        self.Move = channel.unary_unary(
                '/ClientHandler/Move',
                request_serializer=file__pb2.MoveRequest.SerializeToString,
                response_deserializer=file__pb2.MoveReply.FromString,
                )


class ClientHandlerServicer(object):
    """The ClientHandler service definition.
    """

    def ListUsers(self, request, context):
        """Lists users
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Requests to Login
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """Lists files available to user
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Attempts to delete account
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Check(self, request, context):
        """Checks a file
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Upload(self, request_iterator, context):
        """Attempts to upload a file
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Sync(self, request, context):
        """Attempts to sync files
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBackups(self, request, context):
        """Creates backup chain
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadAddNew(self, request, context):
        """Methods to be used by ServerWorkers
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadRemoveOld(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadHelper(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteHelper(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckClock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PullData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Move(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ClientHandlerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ListUsers': grpc.unary_unary_rpc_method_handler(
                    servicer.ListUsers,
                    request_deserializer=file__pb2.ListRequest.FromString,
                    response_serializer=file__pb2.ListReply.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=file__pb2.LoginRequest.FromString,
                    response_serializer=file__pb2.LoginReply.SerializeToString,
            ),
            'List': grpc.unary_unary_rpc_method_handler(
                    servicer.List,
                    request_deserializer=file__pb2.ListRequest.FromString,
                    response_serializer=file__pb2.ListReply.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=file__pb2.DeleteRequest.FromString,
                    response_serializer=file__pb2.DeleteReply.SerializeToString,
            ),
            'Check': grpc.unary_unary_rpc_method_handler(
                    servicer.Check,
                    request_deserializer=file__pb2.CheckRequest.FromString,
                    response_serializer=file__pb2.CheckReply.SerializeToString,
            ),
            'Upload': grpc.stream_unary_rpc_method_handler(
                    servicer.Upload,
                    request_deserializer=file__pb2.UploadRequest.FromString,
                    response_serializer=file__pb2.UploadReply.SerializeToString,
            ),
            'Sync': grpc.unary_stream_rpc_method_handler(
                    servicer.Sync,
                    request_deserializer=file__pb2.SyncRequest.FromString,
                    response_serializer=file__pb2.SyncReply.SerializeToString,
            ),
            'GetBackups': grpc.unary_unary_rpc_method_handler(
                    servicer.GetBackups,
                    request_deserializer=file__pb2.BackupRequest.FromString,
                    response_serializer=file__pb2.BackupReply.SerializeToString,
            ),
            'UploadAddNew': grpc.unary_unary_rpc_method_handler(
                    servicer.UploadAddNew,
                    request_deserializer=file__pb2.UploadAddNewRequest.FromString,
                    response_serializer=file__pb2.Empty.SerializeToString,
            ),
            'UploadRemoveOld': grpc.unary_unary_rpc_method_handler(
                    servicer.UploadRemoveOld,
                    request_deserializer=file__pb2.UploadRemoveOldRequest.FromString,
                    response_serializer=file__pb2.Empty.SerializeToString,
            ),
            'UploadHelper': grpc.unary_unary_rpc_method_handler(
                    servicer.UploadHelper,
                    request_deserializer=file__pb2.UploadHelperRequest.FromString,
                    response_serializer=file__pb2.Empty.SerializeToString,
            ),
            'DeleteHelper': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteHelper,
                    request_deserializer=file__pb2.DeleteRequest.FromString,
                    response_serializer=file__pb2.Empty.SerializeToString,
            ),
            'CheckClock': grpc.unary_unary_rpc_method_handler(
                    servicer.CheckClock,
                    request_deserializer=file__pb2.Empty.FromString,
                    response_serializer=file__pb2.Clock.SerializeToString,
            ),
            'PullData': grpc.unary_unary_rpc_method_handler(
                    servicer.PullData,
                    request_deserializer=file__pb2.Empty.FromString,
                    response_serializer=file__pb2.Data.SerializeToString,
            ),
            'Move': grpc.unary_unary_rpc_method_handler(
                    servicer.Move,
                    request_deserializer=file__pb2.MoveRequest.FromString,
                    response_serializer=file__pb2.MoveReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ClientHandler', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ClientHandler(object):
    """The ClientHandler service definition.
    """

    @staticmethod
    def ListUsers(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/ListUsers',
            file__pb2.ListRequest.SerializeToString,
            file__pb2.ListReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/Login',
            file__pb2.LoginRequest.SerializeToString,
            file__pb2.LoginReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/List',
            file__pb2.ListRequest.SerializeToString,
            file__pb2.ListReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/Delete',
            file__pb2.DeleteRequest.SerializeToString,
            file__pb2.DeleteReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Check(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/Check',
            file__pb2.CheckRequest.SerializeToString,
            file__pb2.CheckReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Upload(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/ClientHandler/Upload',
            file__pb2.UploadRequest.SerializeToString,
            file__pb2.UploadReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Sync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ClientHandler/Sync',
            file__pb2.SyncRequest.SerializeToString,
            file__pb2.SyncReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetBackups(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/GetBackups',
            file__pb2.BackupRequest.SerializeToString,
            file__pb2.BackupReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UploadAddNew(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/UploadAddNew',
            file__pb2.UploadAddNewRequest.SerializeToString,
            file__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UploadRemoveOld(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/UploadRemoveOld',
            file__pb2.UploadRemoveOldRequest.SerializeToString,
            file__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UploadHelper(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/UploadHelper',
            file__pb2.UploadHelperRequest.SerializeToString,
            file__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteHelper(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/DeleteHelper',
            file__pb2.DeleteRequest.SerializeToString,
            file__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CheckClock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/CheckClock',
            file__pb2.Empty.SerializeToString,
            file__pb2.Clock.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PullData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/PullData',
            file__pb2.Empty.SerializeToString,
            file__pb2.Data.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Move(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ClientHandler/Move',
            file__pb2.MoveRequest.SerializeToString,
            file__pb2.MoveReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
