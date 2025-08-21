# Example notebook: https://colab.research.google.com/drive/1DO062G8PPaS_fD6PSs1LV56UXmmFe1cR?usp=sharing
import os
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    AssetUtils,
    TagUtils,
    TaggedItemUtils,
    AssetStatus,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def fetch_and_log_assets(client: AttackIQRestClient, limit: Optional[int] = 10):
    logger.info(f"Fetching and processing up to {limit} assets...")
    asset_count = 0

    for asset in AssetUtils.get_assets(client, limit=limit):
        asset_count += 1
        logger.info(f"Asset {asset_count}:")
        logger.info(f"  ID: {asset.get('id')}")
        logger.info(f"  Name: {asset.get('name')}")
        logger.info(f"  Type: {asset.get('type')}")
        logger.info(f"  IP Address: {asset.get('ipv4_address')}")
        logger.info("---")

    if asset_count == 0:
        logger.info("No assets retrieved with the current filters/limit.")
    else:
        logger.info(f"Successfully processed {asset_count} assets.")


def find_asset_by_hostname(client: AttackIQRestClient, hostname: str):
    logger.info(f"Searching for asset with hostname: {hostname}")
    asset = AssetUtils.get_asset_by_hostname(client, hostname)

    if asset:
        logger.info("Asset found:")
        logger.info(f"  ID: {asset.get('id')}")
        logger.info(f"  Name: {asset.get('name')}")
        logger.info(f"  Type: {asset.get('type')}")
        logger.info(f"  IP Address: {asset.get('ipv4_address')}")
        logger.info(f"  Hostname: {asset.get('hostname')}")
    else:
        logger.info(f"No asset found with hostname: {hostname}")


def uninstall_asset_by_uuid(client: AttackIQRestClient, asset_id: str):
    if not asset_id:
        logger.error("Asset id not provided.")
        return

    asset = AssetUtils.get_asset_by_id(client, asset_id)
    if not asset:
        logger.error(f"Asset with id {asset_id} not found.")
        return

    logger.info(f"Attempting to uninstall asset with id: {asset_id}")
    success = AssetUtils.uninstall_asset(client, asset_id)

    if success:
        logger.info(f"Asset {asset_id} uninstall job submitted successfully.")
    else:
        logger.error(f"Failed to submit uninstall job for asset {asset_id}.")


def list_asset_tags(client: AttackIQRestClient, asset_id: str, limit: Optional[int] = 10):
    logger.info(f"Listing up to {limit} tags for asset with ID: {asset_id}")
    tag_count = 0

    for tagged_item in TaggedItemUtils.get_tagged_items(client, "asset", asset_id, limit=limit):
        tag_count += 1
        tag_id = tagged_item.get("tag", {}).get("id")
        tag_name = tagged_item.get("tag", {}).get("name")
        logger.info(f"Tagged Item {tag_count}:")
        logger.info(f"  Item ID: {tagged_item.get('id')}")
        logger.info(f"  Tag ID: {tag_id}")
        logger.info(f"  Tag Name: {tag_name}")
    logger.info(f"Total tags listed: {tag_count}")


def tag_asset(client: AttackIQRestClient, asset_id: str, tag_id: str) -> str:
    logger.info(f"Tagging asset with ID: {asset_id} with tag ID: {tag_id}")
    tagged_item = TaggedItemUtils.get_tagged_item(client, "asset", asset_id, tag_id)
    tagged_item_id = tagged_item.get("id") if tagged_item else ""
    if tagged_item_id:
        logger.info(f"Asset {asset_id} is already tagged with tag item ID {tagged_item_id}")
        return tagged_item_id
    tagged_item_id = AssetUtils.add_tag(client, asset_id, tag_id)
    if tagged_item_id:
        logger.info(f"Successfully tagged asset {asset_id} with tag item ID {tagged_item_id}")
        return tagged_item_id
    else:
        logger.error(f"Failed to tag asset {asset_id} with tag ID {tag_id}")
        return ""


def untag_asset(client: AttackIQRestClient, tagged_item_id: str):
    logger.info(f"Removing tag item with ID: {tagged_item_id}")
    success = TaggedItemUtils.delete_tagged_item(client, tagged_item_id)
    if success:
        logger.info(f"Successfully removed tag item with ID {tagged_item_id}")
    else:
        logger.error(f"Failed to remove tag item with ID {tagged_item_id}")


def delete_tag(client: AttackIQRestClient, tag_id: str) -> bool:
    logger.info(f"Deleting tag with ID: {tag_id}")
    success = TagUtils.delete_tag(client, tag_id)
    if success:
        logger.info(f"Successfully deleted tag with ID {tag_id}")
    else:
        logger.error(f"Failed to delete tag with ID {tag_id}")
    return success


def get_and_log_total_assets(client: AttackIQRestClient):
    total_assets = AssetUtils.get_total_assets(client)
    if total_assets is not None:
        logger.info(f"Total number of assets: {total_assets}")
    else:
        logger.error("Failed to retrieve total number of assets.")


def get_and_log_assets_count_by_status(client: AttackIQRestClient, status: AssetStatus):
    assets_count = AssetUtils.get_assets_count_by_status(client, status)
    if assets_count is not None:
        logger.info(f"Number of {status.value} assets: {assets_count}")
    else:
        logger.error(f"Failed to retrieve count of {status.value} assets.")


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)

    get_and_log_total_assets(client)
    get_and_log_assets_count_by_status(client, AssetStatus.ACTIVE)
    get_and_log_assets_count_by_status(client, AssetStatus.INACTIVE)

    fetch_and_log_assets(client, limit=25)
    find_asset_by_hostname(client, "AIQ-CY4C7CC9W5")

    asset_id = os.environ.get("ATTACKIQ_ASSET_ID")
    if asset_id:
        if AssetUtils.get_asset_by_id(client, asset_id):
            tag_name = "TEST_TAG"
            if tag_id := TagUtils.get_or_create_custom_tag(client, tag_name):
                logger.info(f"Tag ID: {tag_id} for tag '{tag_name}'")
                if tagged_item_id := tag_asset(client, asset_id, tag_id):
                    list_asset_tags(client, asset_id)
                    untag_asset(client, tagged_item_id)
                    delete_tag(client, tag_id)
                uninstall_asset_by_uuid(client, asset_id)
    else:
        logger.warning("ATTACKIQ_ASSET_ID environment variable is not set. Skipping asset-specific operations.")


if __name__ == "__main__":
    main()
