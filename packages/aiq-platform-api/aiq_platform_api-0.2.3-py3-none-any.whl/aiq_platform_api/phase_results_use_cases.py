# Example notebook: https://colab.research.google.com/drive/1YKniUVbEKglCmYQV0I6tia1QObBgX3xB?usp=sharing
import os
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    PhaseResultsUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_phase_results(
    client: AttackIQRestClient,
    assessment_id: str,
    project_run_id: Optional[str] = None,
    result_summary_id: Optional[str] = None,
    limit: Optional[int] = 10,
):
    logger.info(f"Listing up to {limit} phase results ...")
    count = 0

    for phase_result in PhaseResultsUtils.get_phase_results(
        client,
        assessment_id=assessment_id,
        project_run_id=project_run_id,
        result_summary_id=result_summary_id,
        limit=limit,
    ):
        count += 1
        logger.info(f"Phase Result {count}:")
        logger.info(f"  Result ID: {phase_result.get('id')}")
        phase = phase_result.get("phase")
        if phase:
            logger.info(f"  Phase ID: {phase.get('id')}")
            logger.info(f"  Phase Name: {phase.get('name')}")
        logger.info(f"  Created: {phase_result.get('created')}")
        logger.info(f"  Modified: {phase_result.get('modified')}")
        logger.info(f"  Outcome: {phase_result.get('outcome_description')}")
        logger.info("---")
    logger.info(f"Total phase results listed: {count}")


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)
    assessment_id = os.environ.get("ATTACKIQ_ATOMIC_ASSESSMENT_ID")
    if assessment_id:
        list_phase_results(client, assessment_id, limit=100)
    else:
        logger.error("ATTACKIQ_ATOMIC_ASSESSMENT_ID environment variable not set.")


if __name__ == "__main__":
    main()
