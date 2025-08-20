from dataclasses import dataclass
from typing import List

from .schemas import *
from . import _ddc_py  # type: ignore


def upgrade_ab_media_dcr_to_latest(
    input: AbMediaDcr,
) -> AbMediaDcr:
    result = _ddc_py.upgrade_ab_media_dcr_to_latest(
        input.model_dump_json(by_alias=True)
    )
    parsed = AbMediaDcr.parse_raw(result)
    return parsed


def compile_ab_media_dcr(dcr: AbMediaDcr):
    return _ddc_py.compile_ab_media_dcr_serialized(dcr.model_dump_json(by_alias=True))


def create_ab_media_dcr(args: CreateAbMediaDcr) -> AbMediaDcr:
    response = _ddc_py.create_ab_media_dcr_serialized(args.json())
    return AbMediaDcr.parse_raw(response)


def is_data_lab_compatible_with_ab_media_dcr_serialized(
    data_lab_serialized: DataLab,
    dcr_serialized: str,
) -> bool:
    return _ddc_py.is_data_lab_compatible_with_ab_media_dcr_serialized(
        data_lab_serialized, dcr_serialized
    )


def get_ab_media_dcr_features_serialized(dcr_serialized: str):
    return _ddc_py.get_ab_media_dcr_features_serialized(dcr_serialized)


def get_ab_media_dcr_requirements(dcr: AbMediaDcr) -> ConsumerRequirements:
    serialised_requirements = _ddc_py.get_ab_media_data_room_requirements_serialized(
        dcr.model_dump_json(by_alias=True)
    )
    return ConsumerRequirements.model_validate_json(serialised_requirements)


def compile_ab_media_request(
    request: AbMediaRequest, user_auth_serialized: bytes
) -> bytes:
    return _ddc_py.compile_ab_media_request_serialized(
        request.json(), user_auth_serialized
    )


def decompile_ab_media_response(request: AbMediaRequest, response_serialized: bytes):
    response = _ddc_py.decompile_ab_media_response_serialized(
        request.json(), response_serialized
    )
    parsed = AbMediaResponse.parse_raw(response)
    return parsed


def get_parameter_payloads(
    target_ref: str, audiences: List[Audience6]
) -> ParameterPayloads:
    audiences = [a.model_dump_json(by_alias=True) for a in audiences]
    parameter_payloads: ParameterPayloads = _ddc_py.get_parameter_payloads(
        target_ref, audiences
    )
    return parameter_payloads


def get_dependencies(
    target_ref: str, audiences: List[Audience6]
) -> List[str]:
    audiences = [a.model_dump_json(by_alias=True) for a in audiences]
    audience_ids = _ddc_py.get_audience_dependencies(target_ref, audiences)
    return audience_ids


def does_audience_depend_on_lookalike_audience(
    target_ref: str, audiences: List[Audience6]
) -> bool:
    audiences = [a.model_dump_json(by_alias=True) for a in audiences]
    return _ddc_py.does_audience_depend_on_lookalike_audience(target_ref, audiences)
