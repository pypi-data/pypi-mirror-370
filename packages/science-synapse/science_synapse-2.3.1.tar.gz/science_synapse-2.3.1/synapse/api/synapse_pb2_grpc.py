"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from ..api import app_pb2 as api_dot_app__pb2
from ..api import device_pb2 as api_dot_device__pb2
from ..api import files_pb2 as api_dot_files__pb2
from ..api import logging_pb2 as api_dot_logging__pb2
from ..api import query_pb2 as api_dot_query__pb2
from ..api import status_pb2 as api_dot_status__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
GRPC_GENERATED_VERSION = '1.71.2'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in api/synapse_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class SynapseDeviceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Info = channel.unary_unary('/synapse.SynapseDevice/Info', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=api_dot_device__pb2.DeviceInfo.FromString, _registered_method=True)
        self.Configure = channel.unary_unary('/synapse.SynapseDevice/Configure', request_serializer=api_dot_device__pb2.DeviceConfiguration.SerializeToString, response_deserializer=api_dot_status__pb2.Status.FromString, _registered_method=True)
        self.Start = channel.unary_unary('/synapse.SynapseDevice/Start', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=api_dot_status__pb2.Status.FromString, _registered_method=True)
        self.Stop = channel.unary_unary('/synapse.SynapseDevice/Stop', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=api_dot_status__pb2.Status.FromString, _registered_method=True)
        self.Query = channel.unary_unary('/synapse.SynapseDevice/Query', request_serializer=api_dot_query__pb2.QueryRequest.SerializeToString, response_deserializer=api_dot_query__pb2.QueryResponse.FromString, _registered_method=True)
        self.StreamQuery = channel.unary_stream('/synapse.SynapseDevice/StreamQuery', request_serializer=api_dot_query__pb2.StreamQueryRequest.SerializeToString, response_deserializer=api_dot_query__pb2.StreamQueryResponse.FromString, _registered_method=True)
        self.DeployApp = channel.stream_stream('/synapse.SynapseDevice/DeployApp', request_serializer=api_dot_app__pb2.AppPackageChunk.SerializeToString, response_deserializer=api_dot_app__pb2.AppDeployResponse.FromString, _registered_method=True)
        self.ListFiles = channel.unary_unary('/synapse.SynapseDevice/ListFiles', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=api_dot_files__pb2.ListFilesResponse.FromString, _registered_method=True)
        self.WriteFile = channel.unary_unary('/synapse.SynapseDevice/WriteFile', request_serializer=api_dot_files__pb2.WriteFileRequest.SerializeToString, response_deserializer=api_dot_files__pb2.WriteFileResponse.FromString, _registered_method=True)
        self.ReadFile = channel.unary_stream('/synapse.SynapseDevice/ReadFile', request_serializer=api_dot_files__pb2.ReadFileRequest.SerializeToString, response_deserializer=api_dot_files__pb2.ReadFileResponse.FromString, _registered_method=True)
        self.DeleteFile = channel.unary_unary('/synapse.SynapseDevice/DeleteFile', request_serializer=api_dot_files__pb2.DeleteFileRequest.SerializeToString, response_deserializer=api_dot_files__pb2.DeleteFileResponse.FromString, _registered_method=True)
        self.GetLogs = channel.unary_unary('/synapse.SynapseDevice/GetLogs', request_serializer=api_dot_logging__pb2.LogQueryRequest.SerializeToString, response_deserializer=api_dot_logging__pb2.LogQueryResponse.FromString, _registered_method=True)
        self.TailLogs = channel.unary_stream('/synapse.SynapseDevice/TailLogs', request_serializer=api_dot_logging__pb2.TailLogsRequest.SerializeToString, response_deserializer=api_dot_logging__pb2.LogEntry.FromString, _registered_method=True)
        self.UpdateDeviceSettings = channel.unary_unary('/synapse.SynapseDevice/UpdateDeviceSettings', request_serializer=api_dot_device__pb2.UpdateDeviceSettingsRequest.SerializeToString, response_deserializer=api_dot_device__pb2.UpdateDeviceSettingsResponse.FromString, _registered_method=True)

class SynapseDeviceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Info(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Configure(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Start(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Stop(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Query(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StreamQuery(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeployApp(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListFiles(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLogs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TailLogs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateDeviceSettings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_SynapseDeviceServicer_to_server(servicer, server):
    rpc_method_handlers = {'Info': grpc.unary_unary_rpc_method_handler(servicer.Info, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=api_dot_device__pb2.DeviceInfo.SerializeToString), 'Configure': grpc.unary_unary_rpc_method_handler(servicer.Configure, request_deserializer=api_dot_device__pb2.DeviceConfiguration.FromString, response_serializer=api_dot_status__pb2.Status.SerializeToString), 'Start': grpc.unary_unary_rpc_method_handler(servicer.Start, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=api_dot_status__pb2.Status.SerializeToString), 'Stop': grpc.unary_unary_rpc_method_handler(servicer.Stop, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=api_dot_status__pb2.Status.SerializeToString), 'Query': grpc.unary_unary_rpc_method_handler(servicer.Query, request_deserializer=api_dot_query__pb2.QueryRequest.FromString, response_serializer=api_dot_query__pb2.QueryResponse.SerializeToString), 'StreamQuery': grpc.unary_stream_rpc_method_handler(servicer.StreamQuery, request_deserializer=api_dot_query__pb2.StreamQueryRequest.FromString, response_serializer=api_dot_query__pb2.StreamQueryResponse.SerializeToString), 'DeployApp': grpc.stream_stream_rpc_method_handler(servicer.DeployApp, request_deserializer=api_dot_app__pb2.AppPackageChunk.FromString, response_serializer=api_dot_app__pb2.AppDeployResponse.SerializeToString), 'ListFiles': grpc.unary_unary_rpc_method_handler(servicer.ListFiles, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=api_dot_files__pb2.ListFilesResponse.SerializeToString), 'WriteFile': grpc.unary_unary_rpc_method_handler(servicer.WriteFile, request_deserializer=api_dot_files__pb2.WriteFileRequest.FromString, response_serializer=api_dot_files__pb2.WriteFileResponse.SerializeToString), 'ReadFile': grpc.unary_stream_rpc_method_handler(servicer.ReadFile, request_deserializer=api_dot_files__pb2.ReadFileRequest.FromString, response_serializer=api_dot_files__pb2.ReadFileResponse.SerializeToString), 'DeleteFile': grpc.unary_unary_rpc_method_handler(servicer.DeleteFile, request_deserializer=api_dot_files__pb2.DeleteFileRequest.FromString, response_serializer=api_dot_files__pb2.DeleteFileResponse.SerializeToString), 'GetLogs': grpc.unary_unary_rpc_method_handler(servicer.GetLogs, request_deserializer=api_dot_logging__pb2.LogQueryRequest.FromString, response_serializer=api_dot_logging__pb2.LogQueryResponse.SerializeToString), 'TailLogs': grpc.unary_stream_rpc_method_handler(servicer.TailLogs, request_deserializer=api_dot_logging__pb2.TailLogsRequest.FromString, response_serializer=api_dot_logging__pb2.LogEntry.SerializeToString), 'UpdateDeviceSettings': grpc.unary_unary_rpc_method_handler(servicer.UpdateDeviceSettings, request_deserializer=api_dot_device__pb2.UpdateDeviceSettingsRequest.FromString, response_serializer=api_dot_device__pb2.UpdateDeviceSettingsResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('synapse.SynapseDevice', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('synapse.SynapseDevice', rpc_method_handlers)

class SynapseDevice(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Info(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/Info', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, api_dot_device__pb2.DeviceInfo.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Configure(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/Configure', api_dot_device__pb2.DeviceConfiguration.SerializeToString, api_dot_status__pb2.Status.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Start(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/Start', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, api_dot_status__pb2.Status.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Stop(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/Stop', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, api_dot_status__pb2.Status.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Query(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/Query', api_dot_query__pb2.QueryRequest.SerializeToString, api_dot_query__pb2.QueryResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def StreamQuery(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/synapse.SynapseDevice/StreamQuery', api_dot_query__pb2.StreamQueryRequest.SerializeToString, api_dot_query__pb2.StreamQueryResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DeployApp(request_iterator, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/synapse.SynapseDevice/DeployApp', api_dot_app__pb2.AppPackageChunk.SerializeToString, api_dot_app__pb2.AppDeployResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ListFiles(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/ListFiles', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, api_dot_files__pb2.ListFilesResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def WriteFile(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/WriteFile', api_dot_files__pb2.WriteFileRequest.SerializeToString, api_dot_files__pb2.WriteFileResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ReadFile(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/synapse.SynapseDevice/ReadFile', api_dot_files__pb2.ReadFileRequest.SerializeToString, api_dot_files__pb2.ReadFileResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def DeleteFile(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/DeleteFile', api_dot_files__pb2.DeleteFileRequest.SerializeToString, api_dot_files__pb2.DeleteFileResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetLogs(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/GetLogs', api_dot_logging__pb2.LogQueryRequest.SerializeToString, api_dot_logging__pb2.LogQueryResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def TailLogs(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/synapse.SynapseDevice/TailLogs', api_dot_logging__pb2.TailLogsRequest.SerializeToString, api_dot_logging__pb2.LogEntry.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateDeviceSettings(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/synapse.SynapseDevice/UpdateDeviceSettings', api_dot_device__pb2.UpdateDeviceSettingsRequest.SerializeToString, api_dot_device__pb2.UpdateDeviceSettingsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)