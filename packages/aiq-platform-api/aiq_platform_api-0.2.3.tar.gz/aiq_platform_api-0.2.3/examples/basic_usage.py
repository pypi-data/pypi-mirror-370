"""
Basic example demonstrating how to use the AttackIQ Platform API utilities.

To use this example:
1. Copy this file to your project
2. Create a .env file with your credentials (see below)
3. Create and source a virtual environment: virtualenv venv && source venv/bin/activate
4. Install required packages: pip install --upgrade aiq-platform-api python-dotenv
5. Run: python basic_usage.py
"""

import os

from dotenv import load_dotenv

from aiq_platform_api import (
    AttackIQRestClient,
    AssetUtils,
    TagUtils,
    AttackIQLogger,
    AssetStatus,
)

# Initialize logging
logger = AttackIQLogger.get_logger(__name__)


def demonstrate_asset_operations(client: AttackIQRestClient):
    """Demonstrate basic asset operations."""
    # Get total assets
    total_assets = AssetUtils.get_total_assets(client)
    logger.info(f"Total assets: {total_assets}")

    # Get assets by status
    active_assets = AssetUtils.get_assets_count_by_status(client, AssetStatus.ACTIVE)
    logger.info(f"Active assets: {active_assets}")

    # List first 5 assets
    logger.info("Listing first 5 assets:")
    for i, asset in enumerate(AssetUtils.get_assets(client), 1):
        if i > 5:
            break
        logger.info(f"Asset {i}:")
        logger.info(f"  ID: {asset.get('id')}")
        logger.info(f"  Name: {asset.get('name')}")
        logger.info(f"  Type: {asset.get('type')}")
        logger.info("---")


def demonstrate_tag_operations(client: AttackIQRestClient):
    """Demonstrate basic tag operations."""
    # Create a test tag
    tag_name = "EXAMPLE_TAG"
    tag_id = TagUtils.get_or_create_custom_tag(client, tag_name)
    if tag_id:
        logger.info(f"Created/Found tag '{tag_name}' with ID: {tag_id}")

        # Clean up
        if TagUtils.delete_tag(client, tag_id):
            logger.info(f"Successfully deleted tag '{tag_name}'")


def main():
    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    platform_url = os.getenv("ATTACKIQ_PLATFORM_URL")
    api_token = os.getenv("ATTACKIQ_API_TOKEN")

    if not platform_url or not api_token:
        logger.error("Missing required environment variables")
        return

    try:
        # Initialize client
        client = AttackIQRestClient(platform_url, api_token)

        # Demonstrate different operations
        demonstrate_asset_operations(client)
        demonstrate_tag_operations(client)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    main()
