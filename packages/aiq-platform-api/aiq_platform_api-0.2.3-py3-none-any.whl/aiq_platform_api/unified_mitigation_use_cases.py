# Example use cases for Unified Mitigation endpoints
from typing import Optional, Dict, Any

from aiq_platform_api.common_utils import (
    AttackIQRestClient,
    AttackIQLogger,
    UnifiedMitigationUtils,
    UnifiedMitigationProjectUtils,
    UnifiedMitigationWithRelationsUtils,
    UnifiedMitigationReportingUtils,
)
from aiq_platform_api.env import ATTACKIQ_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def list_mitigation_rules(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """Lists unified mitigation rules."""
    logger.info(f"Listing up to {limit} unified mitigations...")
    count = 0
    try:
        for rule in UnifiedMitigationUtils.list_mitigations(client, limit=limit):
            count += 1
            logger.info(f"Mitigation Rule {count}: ID={rule.get('id')}, Name={rule.get('name')}")
        logger.info(f"Total mitigation rules listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list mitigation rules: {e}")
    return count


def create_and_delete_mitigation_rule(client: AttackIQRestClient, rule_data: Dict[str, Any]) -> None:
    """Creates a mitigation rule and then deletes it."""
    mitigation_id = None
    try:
        logger.info("Attempting to create a new mitigation rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            mitigation_id = created_rule["id"]
            logger.info(f"Successfully created mitigation rule with ID: {mitigation_id}")

            # Example: Get the created rule
            retrieved_rule = UnifiedMitigationUtils.get_mitigation(client, mitigation_id)
            if retrieved_rule:
                logger.info(f"Retrieved rule: {retrieved_rule.get('name')}")
            else:
                logger.warning("Could not retrieve the newly created rule.")

        else:
            logger.error("Failed to create mitigation rule or ID not found in response.")
            return

    except Exception as e:
        logger.error(f"Error during mitigation rule creation/retrieval: {e}")
    finally:
        if mitigation_id:
            logger.info(f"Attempting to delete mitigation rule: {mitigation_id}")
            deleted = UnifiedMitigationUtils.delete_mitigation(client, mitigation_id)
            if deleted:
                logger.info(f"Successfully deleted mitigation rule: {mitigation_id}")
            else:
                logger.error(f"Failed to delete mitigation rule: {mitigation_id}")


def create_sigma_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a Sigma detection rule for PowerShell encoded command detection.

    IMPORTANT: Required fields for creating detection rules:
    - 'unifiedmitigationtype': The mitigation type ID (integer)
    - 'name': Name of the rule
    - 'content': The actual rule content/query (despite docs saying 'rule_content')

    Common mitigation type IDs:
    - 1: Sigma
    - 2: YARA
    - 3: Snort
    - 4: Suricata
    - 5: SPL (Splunk)
    - 6: KQL (Kusto Query Language)
    - 7: EQL (Elastic Query Language)
    - 8: Lucene/Elasticsearch
    - 9: Custom
    - 12: Chronicle YARA-L
    """
    sigma_rule_content = """
title: Suspicious PowerShell Encoded Command
status: experimental
description: Detects suspicious PowerShell execution with encoded commands
logsource:
    product: windows
    service: process_creation
detection:
    selection:
        CommandLine|contains:
            - '-EncodedCommand'
            - '-enc'
        Image|endswith: '\\powershell.exe'
    condition: selection
falsepositives:
    - Administrative scripts
level: medium
"""

    rule_data = {
        "name": "Sigma - Suspicious PowerShell Encoded Command",
        "description": "Detects PowerShell execution with encoded commands that may indicate malicious activity",
        "unifiedmitigationtype": 1,  # REQUIRED: 1 = Sigma (integer type ID)
        "content": sigma_rule_content,  # REQUIRED: The actual rule content (field name is 'content')
    }

    try:
        logger.info("Creating Sigma detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created Sigma rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create Sigma rule")
            return None
    except Exception as e:
        logger.error(f"Error creating Sigma rule: {e}")
        return None


def create_yara_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a YARA detection rule for malware detection."""
    yara_rule_content = """
rule Detect_Mimikatz_Patterns {
    meta:
        description = "Detects common Mimikatz patterns and strings"
        author = "Security Team"
        date = "2025-01-20"
    strings:
        $a = "sekurlsa::logonpasswords" nocase
        $b = "privilege::debug" nocase
        $c = "mimikatz" nocase
        $d = "gentilkiwi" nocase
        $e = "lsadump::sam" nocase
    condition:
        2 of them
}
"""

    rule_data = {
        "name": "YARA - Detect Mimikatz Patterns",
        "description": "YARA rule to detect common Mimikatz tool patterns",
        "unifiedmitigationtype": 2,
        # REQUIRED: 2 = YARA (integer type ID)
        "content": yara_rule_content,  # REQUIRED: The actual rule content
    }

    try:
        logger.info("Creating YARA detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created YARA rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create YARA rule")
            return None
    except Exception as e:
        logger.error(f"Error creating YARA rule: {e}")
        return None


def create_snort_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a Snort IDS rule for network detection."""
    snort_rule_content = """alert tcp $EXTERNAL_NET any -> $HOME_NET 445 (msg:"Possible SMB Exploitation Attempt"; flow:to_server,established; content:"|FF|SMB"; offset:4; depth:4; content:"|00 00 00 00|"; distance:0; content:"|00 00 00 00 00 00 00 00|"; distance:4; within:8; sid:1000001; rev:1;)"""

    rule_data = {
        "name": "Snort - SMB Exploitation Detection",
        "description": "Snort rule to detect potential SMB exploitation attempts",
        "unifiedmitigationtype": 3,
        # REQUIRED: 3 = Snort (integer type ID)
        "content": snort_rule_content,  # REQUIRED: The actual rule content
    }

    try:
        logger.info("Creating Snort detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created Snort rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create Snort rule")
            return None
    except Exception as e:
        logger.error(f"Error creating Snort rule: {e}")
        return None


def create_splunk_spl_detection_rule(client: AttackIQRestClient) -> Optional[str]:
    """Creates a Splunk SPL detection rule."""
    spl_rule_content = """index=windows EventCode=4688 (CommandLine="*-EncodedCommand*" OR CommandLine="*-enc*") Image="*\\powershell.exe" | stats count by Computer, User, CommandLine | where count > 5"""

    rule_data = {
        "name": "SPL - PowerShell Encoded Command Detection",
        "description": "Splunk query to detect encoded PowerShell commands",
        "unifiedmitigationtype": 5,
        # REQUIRED: 5 = SPL/Splunk (integer type ID)
        "content": spl_rule_content,  # REQUIRED: The actual rule content
    }

    try:
        logger.info("Creating Splunk SPL detection rule...")
        created_rule = UnifiedMitigationUtils.create_mitigation(client, rule_data)
        if created_rule and created_rule.get("id"):
            rule_id = created_rule["id"]
            logger.info(f"Successfully created SPL rule with ID: {rule_id}")
            return rule_id
        else:
            logger.error("Failed to create SPL rule")
            return None
    except Exception as e:
        logger.error(f"Error creating SPL rule: {e}")
        return None


def list_project_associations(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """Lists unified mitigation project associations."""
    logger.info(f"Listing up to {limit} unified mitigation project associations...")
    count = 0
    try:
        for assoc in UnifiedMitigationProjectUtils.list_associations(client, limit=limit):
            count += 1
            logger.info(
                f"Association {count}: ID={assoc.get('id')}, RuleID={assoc.get('unified_mitigation')}, ProjectID={assoc.get('project')}"
            )
        logger.info(f"Total associations listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list project associations: {e}")
    return count


def list_mitigations_with_relations(client: AttackIQRestClient, limit: Optional[int] = 10) -> int:
    """Lists unified mitigations including related project and detection data."""
    logger.info(f"Listing up to {limit} unified mitigations with relations...")
    count = 0
    try:
        for rule in UnifiedMitigationWithRelationsUtils.list_mitigations_with_relations(client, limit=limit):
            count += 1
            logger.info(f"Mitigation+Relations {count}: ID={rule.get('id')}, Name={rule.get('name')}")
            # Add more details as needed, e.g., project info
            if rule.get("project"):
                logger.info(f"  Associated Project: {rule.get('project').get('name')}")
        logger.info(f"Total mitigations with relations listed: {count}")
    except Exception as e:
        logger.error(f"Failed to list mitigations with relations: {e}")
    return count


def get_detection_timeline(client: AttackIQRestClient, params: Optional[Dict[str, Any]] = None):
    """Gets the detection performance timeline data."""
    logger.info(f"Getting detection performance timeline with params: {params}")
    try:
        timeline_data = UnifiedMitigationReportingUtils.get_detection_performance_timeline(client, params)
        if timeline_data:
            logger.info(
                "Successfully retrieved detection timeline data."
            )  # Process or display data as needed  # logger.info(f"Timeline Data: {timeline_data}") # Potentially large output
        else:
            logger.warning("No detection timeline data returned.")
    except Exception as e:
        logger.error(f"Failed to get detection timeline: {e}")


def associate_rule_with_assessment(client: AttackIQRestClient, rule_id: str, assessment_id: str) -> Optional[str]:
    """Associates a detection rule with an assessment/project.

    Args:
        client: The AttackIQ REST client
        rule_id: The ID of the detection rule to associate
        assessment_id: The ID of the assessment/project

    Returns:
        The association ID if successful, None otherwise
    """
    try:
        logger.info(f"Associating rule {rule_id} with assessment {assessment_id}")

        association_data = {"unified_mitigation": rule_id, "project": assessment_id, "enabled": True}

        association = UnifiedMitigationProjectUtils.create_association(client, association_data)

        if association and association.get("id"):
            logger.info(f"Successfully associated rule with assessment. Association ID: {association['id']}")
            return association["id"]
        else:
            logger.error("Failed to associate rule with assessment")
            return None

    except Exception as e:
        logger.error(f"Error associating rule with assessment: {str(e)}")
        return None


def delete_detection_rule(client: AttackIQRestClient, rule_id: str) -> bool:
    """Deletes a detection rule by ID.

    Args:
        client: The AttackIQ REST client
        rule_id: The ID of the rule to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Deleting detection rule: {rule_id}")
        deleted = UnifiedMitigationUtils.delete_mitigation(client, rule_id)
        if deleted:
            logger.info(f"Successfully deleted rule: {rule_id}")
            return True
        else:
            logger.error(f"Failed to delete rule: {rule_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return False


def main():
    """Main function demonstrating unified mitigation use cases.

    This example shows how to:
    1. List existing mitigation rules
    2. Create various types of detection rules (Sigma, YARA, Snort, SPL)
    3. Associate rules with assessments/projects
    4. Delete rules after testing
    5. Query mitigation reporting data
    """
    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_API_TOKEN)

    logger.info("--- Listing Existing Unified Mitigation Rules ---")
    list_mitigation_rules(client, limit=5)

    logger.info("\n--- Creating Detection Rules Examples ---")

    # Example 1: Create a Sigma rule
    sigma_rule_id = create_sigma_detection_rule(client)
    if sigma_rule_id:
        logger.info(f"Created Sigma rule: {sigma_rule_id}")
        # Optional: Associate with an assessment (replace with valid assessment ID)
        # assessment_id = "48370285-bcd4-4d68-85d3-ba13353fe925"
        # associate_rule_with_assessment(client, sigma_rule_id, assessment_id)

        # Clean up
        delete_detection_rule(client, sigma_rule_id)

    # Example 2: Create a YARA rule
    yara_rule_id = create_yara_detection_rule(client)
    if yara_rule_id:
        logger.info(f"Created YARA rule: {yara_rule_id}")
        # Clean up
        delete_detection_rule(client, yara_rule_id)

    # Example 3: Create a Snort rule
    snort_rule_id = create_snort_detection_rule(client)
    if snort_rule_id:
        logger.info(f"Created Snort rule: {snort_rule_id}")
        # Clean up
        delete_detection_rule(client, snort_rule_id)

    # Example 4: Create a Splunk SPL rule
    spl_rule_id = create_splunk_spl_detection_rule(client)
    if spl_rule_id:
        logger.info(f"Created SPL rule: {spl_rule_id}")
        # Clean up
        delete_detection_rule(client, spl_rule_id)

    # Example with minimal required fields - demonstrates the absolute minimum needed
    logger.info("\n--- Creating Rule with Minimal Required Fields ---")
    minimal_rule_data = {
        "name": "Minimal Test Rule - Delete Me",
        "description": "Test rule with minimal required fields",
        "unifiedmitigationtype": 9,
        # REQUIRED: 9 = Custom (integer type ID)
        "content": "Basic rule content",  # REQUIRED: The actual rule content (field name is 'content')
    }
    create_and_delete_mitigation_rule(client, minimal_rule_data)

    logger.info("\n--- Testing Project Associations ---")
    list_project_associations(client, limit=5)

    logger.info("\n--- Testing Mitigations With Relations ---")
    list_mitigations_with_relations(client, limit=5)

    logger.info("\n--- Testing Detection Performance Timeline ---")
    timeline_params = {"time_interval": "monthly"}
    get_detection_timeline(client, timeline_params)


if __name__ == "__main__":
    main()
