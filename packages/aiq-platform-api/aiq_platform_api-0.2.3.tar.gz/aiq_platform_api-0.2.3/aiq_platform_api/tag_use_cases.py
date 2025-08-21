# Example notebook: https://colab.research.google.com/drive/15V2OwWn4jpDXwWv5gVt6KGm_5joaIZ-H?usp=sharing
from typing import Optional

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    TagUtils,
    TagSetUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_tags(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    logger.info(f"Listing up to {limit} tags...")
    tag_count = 0

    for tag in TagUtils.get_tags(client, limit=limit):
        tag_count += 1
        logger.info(f"Tag {tag_count}:")
        logger.info(f"  ID: {tag.get('id', 'N/A')}")
        logger.info(f"  Name: {tag.get('name', 'N/A')}")
        logger.info(f"  Display Name: {tag.get('display_name', 'N/A')}")
        logger.info(f"  Tag Set ID: {tag.get('tag_set_id', 'N/A')}")
        logger.info("---")

    logger.info(f"Total tags listed: {tag_count}")
    return tag_count


def add_custom_tag(client: AttackIQRestClient, tag_name: str) -> Optional[str]:
    logger.info(f"Adding new tag: {tag_name} to Custom tag set")
    try:
        tag_set_id = TagSetUtils.get_tag_set_id(client, "Custom")
        if not tag_set_id:
            logger.error("TagSet 'Custom' not found. Cannot add tag.")
            return None
        if tag_id := TagUtils.get_tag_id(client, tag_name, tag_set_id):
            logger.info(f"Tag already exists with ID: {tag_id}")
            return tag_id
        tag = TagUtils.create_tag(client, tag_name, tag_set_id)
        logger.info(f"New tag added: {tag}")
        return tag["id"]
    except Exception as e:
        logger.error(f"Failed to add tag: {str(e)}")
        return None


def remove_tag(client: AttackIQRestClient, tag_id: str) -> bool:
    logger.info(f"Removing tag with ID: {tag_id}")
    try:
        result = TagUtils.delete_tag(client, tag_id)
        if result:
            logger.info(f"Tag {tag_id} removed successfully")
            return True
        else:
            logger.error(f"Failed to remove tag {tag_id}")
            return False
    except Exception as e:
        logger.error(f"Error while removing tag {tag_id}: {str(e)}")
        return False


def main():
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)

    list_tags(client, limit=5)

    new_tag_id = add_custom_tag(client, "NEW_TEST_TAG1")
    if new_tag_id:
        remove_tag(client, new_tag_id)


if __name__ == "__main__":
    main()
