# Example use cases for Scenario endpoints
from typing import Optional, Dict, Any

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    ScenarioUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_scenarios(
    client: AttackIQRestClient,
    limit: Optional[int] = 10,
    filter_params: Optional[Dict[str, Any]] = None,
) -> int:
    """Lists scenarios with optional filtering."""
    filter_params = filter_params or {}
    logger.info(f"Listing up to {limit} scenarios with params: {filter_params}")
    count = 0
    try:
        for scenario in ScenarioUtils.list_scenarios(client, params=filter_params, limit=limit):
            count += 1
            logger.info(f"Scenario {count}: ID={scenario.get('id')}, Name={scenario.get('name')}")
        logger.info(f"Total scenarios listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}")
    return count


def save_scenario_copy(
    client: AttackIQRestClient,
    scenario_id: str,
    new_name: str,
    model_json: Optional[Dict[str, Any]] = None,
    fork_template: bool = True,
) -> Optional[Dict[str, Any]]:
    """Creates a copy of an existing scenario with potentially updated model data.

    Args:
        client: The API client to use
        scenario_id: ID of the scenario to copy
        new_name: Name for the new scenario
        model_json: Optional modified model JSON for the new scenario
        fork_template: Whether to create a new scenario template (True) or reuse the existing one (False)

    Returns:
        The newly created scenario data if successful, None otherwise
    """
    logger.info(f"Creating a copy of scenario {scenario_id} with name '{new_name}'")
    try:
        copy_data = {
            "name": new_name,
            "fork_template": fork_template,
        }
        if model_json:
            copy_data["model_json"] = model_json

        new_scenario = ScenarioUtils.save_copy(client, scenario_id, copy_data)
        if new_scenario:
            logger.info(f"Successfully created scenario copy with ID: {new_scenario.get('id')}")
            return new_scenario
        else:
            logger.error("Failed to create scenario copy")
    except Exception as e:
        logger.error(f"Error creating scenario copy: {e}")
    return None


def delete_scenario_use_case(client: AttackIQRestClient, scenario_id: str):
    """Deletes a specific scenario by its ID."""
    logger.info(f"--- Attempting to delete scenario: {scenario_id} ---")
    try:
        success = ScenarioUtils.delete_scenario(client, scenario_id)
        if success:
            logger.info(f"Successfully initiated deletion of scenario: {scenario_id}")
        else:
            logger.error(f"Failed to initiate deletion of scenario: {scenario_id}")
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {e}")


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)

    logger.info("--- Testing Scenario Listing ---")
    # Example: List all scenarios with names containing "Mimikatz"
    list_scenarios(client, limit=5, filter_params={"search": "Mimikatz"})

    logger.info("--- Testing Scenario Copy ---")
    scenario_id_to_copy = "5417db5e-569f-4660-86ae-9ea7b73452c5"  # Replace with your actual Scenario ID

    scenario = ScenarioUtils.get_scenario(client, scenario_id_to_copy)
    if not scenario:
        logger.error(f"Scenario {scenario_id_to_copy} not found")
        return
    old_name = scenario.get("name")
    old_model_json = scenario.get("model_json")
    old_model_json["domain"] = "example.com"

    new_scenario_name = f"aiq_platform_api created {old_name}"
    new_scenario = save_scenario_copy(
        client,
        scenario_id=scenario_id_to_copy,
        new_name=new_scenario_name,
        model_json=old_model_json,
    )
    if new_scenario:
        new_scenario_id = new_scenario.get("id")
        logger.info(f"New scenario created: {new_scenario.get('name')} ({new_scenario_id})")
        if new_scenario_id:
            logger.info(f"--- Proceeding to delete the created scenario: {new_scenario_id} ---")
            delete_scenario_use_case(client, new_scenario_id)
        else:
            logger.warning("Could not get ID of newly created scenario, skipping deletion.")


if __name__ == "__main__":
    main()
