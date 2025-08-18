from typing import List

from frogml._proto.jfml.model_version.v1.artifact_pb2 import (
    Artifact as ArtifactProto,
    Checksums as ChecksumsProto,
)
from frogml._proto.jfml.model_version.v1.model_version_framework_pb2 import (
    ModelVersionFramework,
    CatboostFramework,
    HuggingFaceFramework,
    OnnxFramework,
    PythonPickleFramework,
    PytorchFramework,
    ScikitLearnFramework,
)
from frogml.sdk.model_version.constants import (
    CATBOOST_SERIALIZED_TYPE,
    HUGGINGFACE_FRAMEWORK_FORMAT,
    ONNX_FRAMEWORK_FORMAT,
    PYTHON_FRAMEWORK_FORMAT,
    PYTORCH_FRAMEWORK_FORMAT,
    SCIKIT_LEARN_FRAMEWORK_FORMAT,
)
from frogml.storage.models.entity_manifest import Artifact


class ProtoUtils:
    @staticmethod
    def model_framework_from_file_format(
        serialization_format: str, framework_version: str = ""
    ) -> ModelVersionFramework:
        framework_to_define: dict = {"version": framework_version}
        stripped_and_lowered_format = serialization_format.strip().lower()

        if stripped_and_lowered_format == CATBOOST_SERIALIZED_TYPE:
            framework_to_define["catboost"] = CatboostFramework()
        elif stripped_and_lowered_format == HUGGINGFACE_FRAMEWORK_FORMAT:
            framework_to_define["hugging_face"] = HuggingFaceFramework()
        elif stripped_and_lowered_format == ONNX_FRAMEWORK_FORMAT:
            framework_to_define["onnx"] = OnnxFramework()
        elif stripped_and_lowered_format == PYTHON_FRAMEWORK_FORMAT:
            framework_to_define["python_pickle"] = PythonPickleFramework()
        elif stripped_and_lowered_format == PYTORCH_FRAMEWORK_FORMAT:
            framework_to_define["pytorch"] = PytorchFramework()
        elif stripped_and_lowered_format == SCIKIT_LEARN_FRAMEWORK_FORMAT:
            framework_to_define["scikit_learn"] = ScikitLearnFramework()
        else:
            raise ValueError(f"Format {serialization_format} is not supported yet")

        return ModelVersionFramework(**framework_to_define)

    @staticmethod
    def convert_artifacts_to_artifacts_proto(
        artifacts: List[Artifact],
    ) -> List[ArtifactProto]:
        return [
            ArtifactProto(
                artifact_path=artifact.artifact_path,
                size=artifact.size,
                checksums=ChecksumsProto(sha2=artifact.checksums.sha2),
            )
            for artifact in artifacts
        ]
