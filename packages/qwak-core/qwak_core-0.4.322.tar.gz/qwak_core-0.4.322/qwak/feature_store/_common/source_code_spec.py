from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from _qwak_proto.qwak.feature_store.v1.common.source_code.source_code_pb2 import (
    SourceCodeSpec as ProtoSourceCodeSpec,
    SourceCodeArtifact as ProtoSourceCodeArtifact,
    ZipArtifact as ProtoZipArtifact,
)
from qwak.exceptions import QwakException


class SourceCodeArtifact(ABC):
    @abstractmethod
    def _to_proto(self) -> ProtoSourceCodeArtifact:
        pass


@dataclass
class ZipArtifact(SourceCodeArtifact):
    artifact_path: str
    main_file: str

    @classmethod
    def _from_proto(cls, proto: ProtoSourceCodeArtifact) -> "ZipArtifact":
        artifact_type: str = proto.WhichOneof("type")
        if artifact_type != "zip_artifact":
            raise QwakException(f"Instead of `zip_artifact` got: {artifact_type}")

        return cls(
            artifact_path=proto.zip_artifact.path,
            main_file=proto.zip_artifact.main_file,
        )

    def _to_proto(self) -> ProtoSourceCodeArtifact:
        return ProtoSourceCodeArtifact(
            zip_artifact=ProtoZipArtifact(
                path=self.artifact_path, main_file=self.main_file
            )
        )


@dataclass
class SourceCodeSpec:
    artifact: Optional[SourceCodeArtifact] = field(default=None)

    @classmethod
    def _from_proto(cls, proto: ProtoSourceCodeSpec) -> "SourceCodeSpec":
        artifact_type: str = proto.artifact.WhichOneof("type")
        if artifact_type == "zip_artifact":
            return cls(artifact=ZipArtifact._from_proto(proto.artifact))

        return cls(artifact=None)

    def _to_proto(self) -> ProtoSourceCodeSpec:
        if self.artifact:
            return ProtoSourceCodeSpec(artifact=self.artifact._to_proto())
        return ProtoSourceCodeSpec()
