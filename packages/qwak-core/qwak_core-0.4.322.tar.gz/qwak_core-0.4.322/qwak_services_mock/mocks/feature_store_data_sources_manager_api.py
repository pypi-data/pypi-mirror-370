import time
import uuid

import grpc
from _qwak_proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSource,
    DataSourceDefinition,
)
from _qwak_proto.qwak.feature_store.sources.data_source_service_pb2 import (
    CreateDataSourceResponse,
    CreateDataSourceUploadURLRequest,
    CreateDataSourceUploadURLResponse,
    GetDataSourceByIdRequest,
    GetDataSourceByIdResponse,
    GetDataSourceByNameResponse,
)
from _qwak_proto.qwak.feature_store.sources.data_source_service_pb2_grpc import (
    DataSourceServiceServicer,
)


class DataSourceServiceMock(DataSourceServiceServicer):
    def __init__(self):
        self._data_sources_spec = {}
        self._data_source_id_to_name = {}

    def CreateDataSource(self, request, context):
        data_source_type = request.data_source_spec.WhichOneof("type")
        data_source_id = str(uuid.uuid4())

        ds_name = (
            request.data_source_spec.batch_source.name
            if data_source_type == "batch_source"
            else request.data_source_spec.stream_source.name
        )

        self._data_sources_spec[ds_name] = request.data_source_spec
        self._data_source_id_to_name[data_source_id] = ds_name

        return CreateDataSourceResponse(
            data_source=DataSource(
                data_source_definition=DataSourceDefinition(
                    data_source_id=data_source_id,
                    data_source_spec=request.data_source_spec,
                ),
                metadata=None,
                feature_sets=[],
            )
        )

    def GetDataSourceByName(self, request, context):
        if request.data_source_name not in self._data_sources_spec:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return GetDataSourceByNameResponse()

        return GetDataSourceByNameResponse(
            data_source=DataSource(
                data_source_definition=DataSourceDefinition(
                    data_source_id="123",
                    data_source_spec=self._data_sources_spec[request.data_source_name],
                ),
                metadata=None,
                feature_sets=[],
            )
        )

    def GetDataSourceById(self, request: GetDataSourceByIdRequest, context):
        if request.data_source_id not in self._data_source_id_to_name:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return GetDataSourceByIdResponse()

        data_source_name = self._data_source_id_to_name[request.data_source_id]
        data_source_spec = self._data_sources_spec[data_source_name]

        return GetDataSourceByIdResponse(
            data_source=DataSource(
                data_source_definition=DataSourceDefinition(
                    data_source_id=request.data_source_id,
                    data_source_spec=data_source_spec,
                ),
                metadata=None,
                feature_sets=[],
            )
        )

    def CreateDataSourceUploadURL(
        self, request: CreateDataSourceUploadURLRequest, context
    ):
        return CreateDataSourceUploadURLResponse(
            upload_url=f"https://data_source_artifacts.s3.amazonaws.com/{request.data_source_name}_{request.object_name}"
        )

    def CreateDataSourceUploadURLV1(
        self, request: CreateDataSourceUploadURLRequest, context
    ):
        return CreateDataSourceUploadURLResponse(
            upload_url=f"https://data_source_artifacts.s3.amazonaws.com/{request.data_source_name}_{request.object_name}_{int(time.time() * 1000)}"
        )
