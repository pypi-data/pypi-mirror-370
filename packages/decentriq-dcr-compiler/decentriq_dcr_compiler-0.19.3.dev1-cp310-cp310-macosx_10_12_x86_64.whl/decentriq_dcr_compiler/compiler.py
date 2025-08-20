from dataclasses import dataclass
from typing import List
from enum import Enum

from .schemas import (
    DataScienceDataRoom,
    DataScienceCommit,
    DataLab,
    CreateDataLab,
    RequirementList,
    EnclaveSpecification,
    ConsumerRequirements,
)
from . import _ddc_py  # type: ignore


@dataclass
class DataScienceDataRoomCompileOutput:
    data_room: bytes
    commits: List[bytes]
    datascience_data_room_encoded: bytes
    compile_context: _ddc_py.PyCommitCompileContext


def compile_data_science_data_room(
    input: DataScienceDataRoom,
) -> DataScienceDataRoomCompileOutput:
    compile_output = _ddc_py.compile_data_science_data_room(input.model_dump_json())
    return DataScienceDataRoomCompileOutput(
        data_room=bytes(compile_output.data_room),
        commits=[bytes(commit) for commit in compile_output.commits],
        datascience_data_room_encoded=bytes(compile_output.high_level),
        compile_context=compile_output.commit_context,
    )


def verify_data_room(
    data_room: bytes, commits: List[bytes], high_level: bytes
) -> DataScienceDataRoom:
    result = _ddc_py.verify_data_room(data_room, commits, high_level)
    parsed = DataScienceDataRoom.model_validate_json(result)
    return parsed


def upgrade_data_science_data_room_to_latest(
    input: DataScienceDataRoom,
) -> DataScienceDataRoom:
    result = _ddc_py.upgrade_data_science_data_room_to_latest(input.model_dump_json())
    parsed = DataScienceDataRoom.model_validate_json(result)
    return parsed


@dataclass
class DataScienceCommitCompileOutput:
    commit: bytes
    datascience_commit_encoded: bytes
    compile_context: _ddc_py.PyCommitCompileContext


def compile_data_science_commit(
    input: DataScienceCommit,
    context: _ddc_py.PyCommitCompileContext,
) -> DataScienceCommitCompileOutput:
    compile_output = _ddc_py.compile_data_science_commit(
        input.model_dump_json(), context
    )
    return DataScienceCommitCompileOutput(
        commit=compile_output.commit,
        datascience_commit_encoded=compile_output.high_level,
        compile_context=compile_output.commit_context,
    )


def verify_configuration_commit(
    low_level: bytes,
    high_level: bytes,
    context: _ddc_py.PyCommitCompileContext,
) -> DataScienceCommit:
    result = _ddc_py.verify_configuration_commit(low_level, high_level, context)
    parsed = DataScienceCommit.model_validate_json(result)
    return parsed


def compile_data_lab(
    input: DataLab,
) -> bytes:
    return _ddc_py.compile_data_lab_serialized(input.model_dump_json())


class DataLabNode(Enum):
    Users = 1
    Segments = 2
    Demographics = 3
    Embeddings = 4
    Statistics = 5


def get_data_lab_node_id(input: DataLabNode, feature_flags: List[str]) -> str:
    if input == DataLabNode.Users:
        node_type = _ddc_py.DataLabNode.Users
    elif input == DataLabNode.Segments:
        node_type = _ddc_py.DataLabNode.Segments
    elif input == DataLabNode.Demographics:
        node_type = _ddc_py.DataLabNode.Demographics
    elif input == DataLabNode.Embeddings:
        node_type = _ddc_py.DataLabNode.Embeddings
    elif input == DataLabNode.Statistics:
        node_type = _ddc_py.DataLabNode.Statistics
    return _ddc_py.get_data_lab_node_id(node_type, feature_flags)


def get_data_lab_validation_node_id(input: DataLabNode, feature_flags: List[str]) -> str:
    if input == DataLabNode.Users:
        node_type = _ddc_py.DataLabNode.Users
    elif input == DataLabNode.Segments:
        node_type = _ddc_py.DataLabNode.Segments
    elif input == DataLabNode.Demographics:
        node_type = _ddc_py.DataLabNode.Demographics
    elif input == DataLabNode.Embeddings:
        node_type = _ddc_py.DataLabNode.Embeddings
    elif input == DataLabNode.Statistics:
        node_type = _ddc_py.DataLabNode.Statistics
    return _ddc_py.get_data_lab_validation_node_id(node_type, feature_flags)


def create_data_lab(
    input: CreateDataLab,
) -> DataLab:
    response = _ddc_py.create_data_lab_serialized(input.model_dump_json())
    data_lab = DataLab.model_validate_json(response)
    return data_lab


def get_consumed_datasets(lm_dcr_json: str) -> RequirementList:
    req_list_serialized = (
        _ddc_py.get_lookalike_media_data_room_consumed_datasets_serialized(lm_dcr_json)
    )
    return RequirementList.model_validate_json(req_list_serialized)


def update_data_lab_enclave_specifications(
    data_lab: DataLab,
    driver_spec: EnclaveSpecification,
    python_spec: EnclaveSpecification,
    root_certificate_pem: str,
) -> DataLab:
    result = _ddc_py.update_data_lab_enclave_specifications_serialized(
        data_lab.model_dump_json(),
        driver_spec.model_dump_json(),
        python_spec.model_dump_json(),
        root_certificate_pem,
    )
    return DataLab.model_validate_json(result)


def get_data_lab_features(
    data_lab: DataLab,
) -> List[str]:
    return _ddc_py.get_data_lab_features_serialized(data_lab.model_dump_json())


def get_lookalike_media_node_names_from_data_lab_data_type(input: str) -> str:
    return _ddc_py.get_lookalike_media_node_names_from_data_lab_data_type(input)
