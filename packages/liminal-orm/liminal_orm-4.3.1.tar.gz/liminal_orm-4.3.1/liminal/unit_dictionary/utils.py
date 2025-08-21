import json
from functools import lru_cache

from liminal.connection.benchling_service import BenchlingService


@lru_cache(maxsize=1)
def get_unit_name_to_id_map(benchling_service: BenchlingService) -> dict[str, str]:
    response = benchling_service.api.get_response(
        url="/api/v2-alpha/unit-types?pageSize=50"
    )
    unit_types = json.loads(response.content)["unitTypes"]
    all_unit_types_flattened = {}
    for unit_type in unit_types:
        for unit in unit_type["units"]:
            all_unit_types_flattened[unit["name"]] = unit["id"]
    return all_unit_types_flattened


def get_unit_id_from_name(benchling_service: BenchlingService, unit_name: str) -> str:
    unit_id = get_unit_name_to_id_map(benchling_service).get(unit_name)
    if unit_id is None:
        raise ValueError(
            f"Unit {unit_name} not found in Benchling Unit Dictionary. Please check the field definition or your Unit Dictionary."
        )
    return unit_id


@lru_cache(maxsize=1)
def get_unit_id_to_name_map(benchling_service: BenchlingService) -> dict[str, str]:
    response = benchling_service.api.get_response(
        url="/api/v2-alpha/unit-types?pageSize=50"
    )
    unit_types = json.loads(response.content)["unitTypes"]
    all_unit_types_flattened = {}
    for unit_type in unit_types:
        for unit in unit_type["units"]:
            all_unit_types_flattened[unit["id"]] = unit["name"]
    return all_unit_types_flattened


def get_unit_name_from_id(benchling_service: BenchlingService, unit_id: str) -> str:
    unit_name = get_unit_id_to_name_map(benchling_service).get(unit_id)
    if unit_name is None:
        raise ValueError(
            f"Unit {unit_id} not found in Benchling Unit Dictionary. Please check the field definition or your Unit Dictionary."
        )
    return unit_name
