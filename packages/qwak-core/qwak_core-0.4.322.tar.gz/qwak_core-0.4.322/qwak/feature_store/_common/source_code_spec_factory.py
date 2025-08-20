import os
from pathlib import Path
from typing import Optional

from qwak.exceptions import QwakException
from qwak.feature_store._common import packaging
from qwak.feature_store._common.source_code_spec import SourceCodeSpec, ZipArtifact


class SourceCodeSpecFactory:
    @staticmethod
    def _upload_source_code_dir(main_entity_path: Path, presign_url: str):
        zip_location: Optional[Path] = None
        try:
            zip_location = packaging.zip_source_code_dir(base_path=main_entity_path)
            with open(zip_location, "rb") as zip_file:
                packaging.put_presigned_url(
                    presign_url=presign_url,
                    content=zip_file.read(),
                    content_type="application/octet-stream",
                )
        except Exception as e:
            raise QwakException("Got an error while trying to upload file.") from e
        finally:
            if zip_location:
                os.remove(zip_location)

    @staticmethod
    def get_zip_source_code_spec(
        main_entity_path: Path, presign_url: str
    ) -> SourceCodeSpec:
        """
        Zips and upload the artifact,
        the main "entity" relative path is set as the main_entity_path
        """
        SourceCodeSpecFactory._upload_source_code_dir(
            main_entity_path=main_entity_path, presign_url=presign_url
        )

        parent_base_path = (
            main_entity_path.parent if main_entity_path.is_file() else main_entity_path
        )

        return SourceCodeSpec(
            artifact=ZipArtifact(
                artifact_path=presign_url,
                main_file=str(
                    Path(parent_base_path.name) / Path(main_entity_path.name)
                ),
            )
        )
