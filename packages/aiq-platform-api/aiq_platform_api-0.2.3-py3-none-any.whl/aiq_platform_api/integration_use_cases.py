# Example notebook: https://colab.research.google.com/drive/1KdS1JC5bJjUu95br4HatdKfxVqcKNzkn?usp=sharing
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    ConnectorUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def fetch_and_log_connectors(client: AttackIQRestClient, limit: Optional[int] = 10):
    logger.info(f"Fetching and processing up to {limit} company connectors...")
    connector_count = 0

    for connector in ConnectorUtils.get_connectors(client, limit=limit):
        connector_count += 1
        logger.info(f"Connector {connector_count}:")
        logger.info(f"  ID: {connector.get('id')}")
        logger.info(f"  Name: {connector.get('name')}")
        logger.info(f"  Type: {connector.get('type')}")
        logger.info(f"  Status: {connector.get('status')}")
        logger.info("---")

    if connector_count == 0:
        logger.info("No company connectors found.")
    else:
        logger.info(f"Successfully processed {connector_count} company connectors.")


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)

    fetch_and_log_connectors(client, limit=5)


if __name__ == "__main__":
    main()
