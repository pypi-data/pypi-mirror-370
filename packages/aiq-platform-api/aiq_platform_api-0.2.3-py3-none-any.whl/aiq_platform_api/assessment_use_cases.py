# Example notebook: https://colab.research.google.com/drive/1XpDkCMb1myskcQOILK6XaaF1g0a_8666?usp=sharing
import os
from typing import Optional, Dict, Any, List

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    AssessmentUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_assessments(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """List assessments with basic information."""
    logger.info(f"Listing up to {limit} assessments")
    count = 0

    for assessment in AssessmentUtils.get_assessments(client, limit=limit):
        count += 1
        logger.info(f"Assessment {count}:")
        logger.info(f"  ID: {assessment.get('id', 'N/A')}")
        logger.info(f"  Name: {assessment.get('name', 'N/A')}")
        logger.info(f"  Status: {assessment.get('status', 'N/A')}")
        logger.info("---")

    logger.info(f"Total assessments listed: {count}")
    return count


def get_assessment_by_id(client: AttackIQRestClient, assessment_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about an assessment by ID."""
    logger.info(f"Getting assessment with ID: {assessment_id}")
    assessment = AssessmentUtils.get_assessment_by_id(client, assessment_id)

    if assessment:
        logger.info(f"Assessment Name: {assessment.get('name')}")
        logger.info(f"Is Attack Graph: {assessment.get('is_attack_graph')}")  # Add more fields as needed

    return assessment


def list_assessment_runs(client: AttackIQRestClient, assessment_id: str, limit: Optional[int] = 10):
    """List recent runs for an assessment."""
    logger.info(f"Listing up to {limit} runs for assessment {assessment_id}")
    count = 0

    for run in AssessmentUtils.list_assessment_runs(client, assessment_id, limit=limit):
        count += 1
        logger.info(f"Run {count}:")
        logger.info(f"  ID: {run.get('id', 'N/A')}")
        logger.info(f"  Created: {run.get('created_at', 'N/A')}")
        logger.info(f"  Scenario Jobs In Progress: {run.get('scenario_jobs_in_progress', 'N/A')}")
        logger.info(f"  Integration Jobs In Progress: {run.get('integration_jobs_in_progress', 'N/A')}")
        logger.info("---")

    return count


def run_and_monitor_assessment(
    client: AttackIQRestClient,
    assessment_id: str,
    timeout: int = 600,
    check_interval: int = 10,
) -> Optional[str]:
    """Run an assessment and wait for it to complete."""
    logger.info(f"Running assessment {assessment_id} and monitoring completion")

    try:
        # Start the assessment
        run_id = AssessmentUtils.run_assessment(client, assessment_id)
        logger.info(f"Assessment started with run ID: {run_id}")

        # Wait for completion
        without_detection = True
        completed = AssessmentUtils.wait_for_run_completion(
            client, assessment_id, run_id, timeout, check_interval, without_detection
        )

        if completed:
            logger.info(f"Assessment run {run_id} completed successfully")
            return run_id
        else:
            logger.warning(f"Assessment run {run_id} did not complete within {timeout} seconds")
            return None

    except Exception as e:
        logger.error(f"Error running assessment: {str(e)}")
        return None


def get_run_results(client: AttackIQRestClient, run_id: str, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """Get results for a completed run and return them as a list."""
    logger.info(f"Getting results for run {run_id}")
    results_generator = AssessmentUtils.get_results_by_run_id(client, run_id, limit=limit)
    collected_results = []
    for i, result in enumerate(results_generator):
        logger.info(f"Result {i + 1}:")
        logger.info(f"  ID: {result.get('id', 'N/A')}")
        logger.info(f"  Status: {result.get('status', 'N/A')}")
        logger.info(f"  Start Time: {result.get('start_time', 'N/A')}")
        logger.info(f"  End Time: {result.get('end_time', 'N/A')}")
        logger.info("---")
        collected_results.append(result)
    return collected_results


def get_detailed_result(client: AttackIQRestClient, result_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific result, including intermediate results."""
    logger.info(f"Getting detailed information for result {result_id}")
    result = AssessmentUtils.get_result_details(client, result_id)

    if not result:
        logger.error(f"Could not retrieve detailed result for result ID: {result_id}")
        return None

    logger.info("--- Detailed Result ---")
    logger.info(f"  Result ID: {result.get('id', 'N/A')}")
    logger.info(f"  Overall Outcome: {result.get('outcome', 'N/A')}")
    logger.info(f"  Detection Outcome: {result.get('detection_outcome', 'N/A')}")
    logger.info(f"  Run Started At: {result.get('run_started_at', 'N/A')}")

    # Log intermediate results
    intermediate_results = result.get("intermediate_results")
    if intermediate_results and isinstance(intermediate_results, list):
        logger.info("--- Intermediate Results (Nodes/Steps) ---")
        for i, step in enumerate(intermediate_results):
            logger.info(f"  Step {i + 1}:")
            logger.info(f"    Node ID: {step.get('node_id', 'N/A')}")
            logger.info(f"    Scenario Name: {step.get('scenario_name', 'N/A')}")
            logger.info(f"    Outcome: {step.get('outcome', 'N/A')}")

    return result


def list_assets_in_assessment(client: AttackIQRestClient, assessment_id: str, limit: Optional[int] = 10):
    """List assets associated with an assessment."""
    logger.info(f"Listing assets for assessment {assessment_id}")
    count = 0

    for asset in AssessmentUtils.get_assets_in_assessment(client, assessment_id, limit=limit):
        count += 1
        logger.info(f"Asset {count}:")
        logger.info(f"  ID: {asset.get('id', 'N/A')}")
        logger.info(f"  Name: {asset.get('name', 'N/A')}")
        logger.info(f"  Type: {asset.get('type', 'N/A')}")
        logger.info(f"  IP Address: {asset.get('ipv4_address', 'N/A')}")
        logger.info("---")

    return count


def get_recent_run_id(client: AttackIQRestClient, assessment_id: str) -> Optional[str]:
    """Get the most recent run ID for an assessment."""
    logger.info(f"Getting most recent run ID for assessment {assessment_id}")
    runs = list(AssessmentUtils.list_assessment_runs(client, assessment_id, limit=1))
    if not runs:
        logger.warning(f"No runs found for assessment {assessment_id}")
        return None
    run_id = runs[0].get("id")
    logger.info(f"Found most recent run ID: {run_id}")
    return run_id


def assessment_workflow_demo(client: AttackIQRestClient, assessment_id: str, run_assessment: bool):
    """Demonstrate a complete assessment workflow."""
    logger.info(f"Starting assessment workflow demo for assessment {assessment_id}")

    # Step 1: Get assessment metadata
    metadata = get_assessment_by_id(client, assessment_id)
    if not metadata:
        logger.error("Could not get assessment metadata. Aborting workflow.")
        return

    # Step 2: List recent runs
    list_assessment_runs(client, assessment_id)

    # Step 3: Run the assessment and wait for completion
    run_id = None
    if run_assessment:
        run_id = run_and_monitor_assessment(client, assessment_id, timeout=60, check_interval=60)

    # If we didn't run an assessment or it didn't complete, get the most recent run
    if not run_id:
        run_id = get_recent_run_id(client, assessment_id)
        if not run_id:
            logger.error("No runs found for assessment. Aborting workflow.")
            return

    # Step 4: Get results for the run
    results = get_run_results(client, run_id)
    if not results:
        logger.error("No results found for run. Aborting workflow.")
        return

    # Step 5: Get detailed results including intermediate results
    for result in results:
        get_detailed_result(client, result["id"])


def main():
    """Main function to demonstrate assessment use cases."""
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)
    atomic_assessment_id = os.environ.get("ATTACKIQ_ATOMIC_ASSESSMENT_ID")
    stag_assessment_id = os.environ.get("ATTACKIQ_STAG_ASSESSMENT_ID")
    run_assessment = os.environ.get("RUN_ASSESSMENT", "false").lower() == "true"
    list_assessments(client)
    if atomic_assessment_id:
        assessment_workflow_demo(client, atomic_assessment_id, run_assessment)
    if stag_assessment_id:
        assessment_workflow_demo(client, stag_assessment_id, run_assessment)


if __name__ == "__main__":
    main()
