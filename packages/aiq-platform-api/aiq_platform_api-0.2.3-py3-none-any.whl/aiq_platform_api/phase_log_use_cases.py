# Example notebook: https://colab.research.google.com/drive/1GTL1QvEfbBbX-W1uGLbsnngQIlKbqPnC?usp=sharing
import os
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    PhaseLogsUtils,
    AssessmentUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_phase_logs(
    client: AttackIQRestClient,
    scenario_job_id: str,
    limit: Optional[int] = 10,
):
    logger.info(f"Listing up to {limit} phase logs for scenario job ID: {scenario_job_id}...")
    count = 0

    for log in PhaseLogsUtils.get_phase_logs(client, scenario_job_id=scenario_job_id, limit=limit):
        count += 1
        logger.info(f"Phase Log {count}:")
        logger.info(f"  Log ID: {log.get('id')}")
        logger.info(f"  Trace Type: {log.get('trace_type')}")
        logger.info(f"  Result Summary ID: {log.get('result_summary_id')}")
        logger.info(f"  Created: {log.get('created')}")
        logger.info(f"  Modified: {log.get('modified')}")
        logger.info(f"  Message: {log.get('message')}")
        logger.info("---")
    logger.info(f"Total phase logs listed: {count}")


def get_recent_assessment_results(client: AttackIQRestClient, assessment_id: str, limit: int = 10) -> list:
    """Fetches recent assessment results using AssessmentUtils (which handles limit)."""
    results_generator = AssessmentUtils.get_results_by_run_id(client, assessment_id, limit=limit)
    results = list(results_generator)  # Convert generator to list
    logger.info(f"Fetched {len(results)} results for assessment ID: {assessment_id}")
    return results


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)
    assessment_id = os.environ.get("ATTACKIQ_ATOMIC_ASSESSMENT_ID")
    if assessment_id:
        # Fetch recent results to get scenario_job_ids
        assessment_results = get_recent_assessment_results(client, assessment_id)
        if assessment_results:
            for assessment_result in assessment_results:
                # Assuming scenario_job_id is directly available in the result summary
                scenario_job_id = assessment_result.get("id")  # Adjust if the key is different
                if scenario_job_id:
                    logger.info(f"\n--- Fetching logs for Scenario Job ID: {scenario_job_id} ---")
                    list_phase_logs(client, scenario_job_id)
                else:
                    logger.warning(f"Could not find scenario_job_id in result: {assessment_result.get('id')}")
    else:
        logger.error("ATTACKIQ_ATOMIC_ASSESSMENT_ID environment variable not set.")


if __name__ == "__main__":
    main()
