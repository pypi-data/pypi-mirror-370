# Example notebook: https://colab.research.google.com/drive/1lkBknmfM3Ygt2X4NBxDVecz8Z7LKaECB?usp=sharing
from datetime import datetime, timedelta
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    ResultsUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_results(
    client: AttackIQRestClient,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = 10,
):
    logger.info(f"Listing up to {limit} results...")
    count = 0

    for result in ResultsUtils.get_results(
        client,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ):
        count += 1
        logger.info(f"Result {count}:")
        logger.info(f"  Result ID: {result.get('id')}")
        logger.info("---")
    logger.info(f"Total results listed: {count}")
    return count


def iterate_results_from(client: AttackIQRestClient, hours_ago: int):
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_ago)
    logger.info(f"Iterating over results from {start_date} to {end_date}")
    return list_results(client, start_date=start_date, end_date=end_date)


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)
    hours_ago = 2
    total_results = iterate_results_from(client, hours_ago)
    logger.info(f"Total results from hours ago:  {hours_ago} : {total_results}")


if __name__ == "__main__":
    main()
