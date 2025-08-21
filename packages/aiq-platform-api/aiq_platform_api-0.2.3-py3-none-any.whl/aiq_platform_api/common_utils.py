import itertools
import logging
import os
import time
from datetime import datetime
from enum import Enum
from http import HTTPStatus
from typing import Optional, Dict, Any, Generator
from urllib.parse import urlencode

import requests
from IPython import get_ipython
from requests.exceptions import RequestException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    retry_if_exception,
)


class AttackIQLogger:
    """Logger for AttackIQ platform.

    This class provides a logger for the AttackIQ platform.
    It handles logging to the console and Jupyter notebooks.
    """

    _instances = {}

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        if name not in cls._instances:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            logger.propagate = False

            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            if cls.is_jupyter():
                handler = cls.NotebookHandler()
            else:
                handler = logging.StreamHandler()

            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            cls._instances[name] = logger

        return cls._instances[name]

    @staticmethod
    def is_jupyter():
        try:
            shell = get_ipython().__class__.__name__
            return shell == "ZMQInteractiveShell"
        except NameError:
            return False

    class NotebookHandler(logging.Handler):
        def emit(self, record):
            from IPython.display import display, HTML

            log_entry = self.format(record)
            color = "white"
            if record.levelno >= logging.ERROR:
                color = "red"
            elif record.levelno >= logging.WARNING:
                color = "orange"
            display(HTML(f'<pre style="color: {color}">{log_entry}</pre>'))


logger = AttackIQLogger.get_logger(__name__)


class AttackIQRestClient:
    """REST client for interacting with the AttackIQ platform.

    This class provides a clean, unified API for interacting with the AttackIQ platform.
    It handles authentication, pagination, and error handling for all platform endpoints.
    """

    def __init__(self, platform_url: str, platform_api_token: str):
        self.platform_url = platform_url.rstrip("/")
        self.headers = {
            "Authorization": (
                f"Bearer {platform_api_token}"
                if os.environ.get("IS_AIQ_PLATFORM_ENABLE", "false") == "true"
                else f"Token {platform_api_token}"
            ),
            "Content-Type": "application/json",
        }

    def get_object(self, endpoint: str, params: dict = None) -> Optional[Dict[str, Any]]:
        url = self._build_url(endpoint, params)
        logger.info(f"Fetching object from {url}")
        return self._make_request(url, method="get", json=None)

    def get_all_objects(self, endpoint: str, params: dict = None) -> Generator[Dict[str, Any], None, None]:
        url = self._build_url(endpoint, params)
        logger.info(f"Fetching objects from {url}")
        total_count = None
        objects_yielded = 0
        while url:
            try:
                data = self._make_request(url, method="get", json=None)
                if not data:
                    logger.info("Received empty data, stopping pagination.")
                    break
                # Check if the response is the expected dict or just a list
                if isinstance(data, dict):
                    results = data.get("results", [])
                    if total_count is None:
                        total_count = data.get("count")
                    url = data.get("next")  # Get next page URL
                    if total_count is not None:
                        objects_left = total_count - objects_yielded
                        logger.info(f"Objects left: {objects_left}")
                    else:
                        logger.info("Total count not available in response.")
                elif isinstance(data, list):
                    logger.info("Received a direct list response (non-paginated).")
                    results = data
                    total_count = len(results)  # Count is just the length of the list
                    url = None  # No next page for a direct list response
                    logger.info(f"Yielding {total_count} objects from the list.")
                else:
                    logger.error(f"Unexpected data type received: {type(data)}. Stopping.")
                    break
                if not results:
                    logger.info("No results found in the current batch.")
                    # Keep url as is if it was set from dict, or None if it was a list
                    if url is None:  # Break if it was a list or dict had no next
                        break
                    else:  # Continue if it was a dict with a next url
                        continue
                for result in results:
                    yield result
                    objects_yielded += 1  # If it was a list response, url is already None, loop will terminate
            except RequestException as e:
                logger.error(f"Failed to fetch objects during pagination: {e}")
                break
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during pagination: {e}",
                    exc_info=True,
                )
                break

    def get_total_objects_count(self, endpoint: str, params: dict = None) -> Optional[int]:
        url = self._build_url(endpoint, params)
        data = self._make_request(url, method="get", json=None)
        return data.get("count") if data else None

    def post_object(self, endpoint: str, data: dict) -> Optional[Dict[str, Any]]:
        url = self._build_url(endpoint)
        logger.info(f"Posting object to {url} with data: {data}")
        return self._make_request(url, method="post", json=data)

    def delete_object(self, endpoint: str) -> Optional[Dict[str, Any]]:
        url = self._build_url(endpoint)
        logger.info(f"Deleting object at {url}")
        return self._make_request(url, method="delete", json=None)

    def _build_url(self, endpoint: str, params: dict = None) -> str:
        if not endpoint.startswith(self.platform_url):
            endpoint = endpoint.lstrip("/")
            url = f"{self.platform_url}/{endpoint}"
        else:
            url = endpoint
        if params:
            url += f"?{urlencode(params)}"
        return url

    @staticmethod
    def _is_retryable_exception(exception):
        if isinstance(exception, RequestException):
            if exception.response is not None:
                return exception.response.status_code in [
                    HTTPStatus.BAD_GATEWAY,
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    HTTPStatus.GATEWAY_TIMEOUT,
                ]
        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception(_is_retryable_exception),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.DEBUG),
    )
    def _make_request(self, url: str, method: str, json: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            logger.info(f"Request method: {method.upper()} for URL: {url}")
            method = method.lower()
            if method not in ["get", "post", "delete", "put", "patch"]:
                raise ValueError(f"Unsupported method: {method}")
            if method == "post" and json:
                logger.info(f"Request data: {json}")
            response = requests.request(method, url, headers=self.headers, json=json)
            if response.status_code == HTTPStatus.NOT_FOUND:
                logger.error(f"Resource not found: {url}")
                return {}
            response.raise_for_status()
            if response.status_code in [
                HTTPStatus.NO_CONTENT,
                HTTPStatus.RESET_CONTENT,
            ]:
                logger.info(f"Request successful: {response.status_code} {response.reason}")
                return {"status_code": response.status_code}
            if response.content:
                return response.json()
            else:
                logger.info(f"Request successful but no content returned: {response.status_code} {response.reason}")
                return {"status_code": response.status_code}
        except requests.RequestException as e:
            if e.response is not None:
                logger.exception(
                    f"_make_request failed method: {method} \n"
                    f"\turl: {url} \n"
                    f"\tstatus: {e.response.status_code} \n"
                    f"\tcontent: {e.response.text} \n"
                    f"\tjson: {json} \n"
                    f"\theaders: {self.headers} \n"
                    f"\texception: {e}"
                )
            else:
                logger.exception(
                    f"_make_request failed method: {method} \n"
                    f"\turl: {url} \n"
                    f"\tjson: {json} \n"
                    f"\theaders: {self.headers} \n"
                    f"\texception: {e}"
                )
            raise e


class ResultsUtils:
    """Utilities for working with results in the AttackIQ platform.

    API Endpoint: /v1/results
    """

    ENDPOINT = "v1/results"

    @staticmethod
    def get_results(
        client: AttackIQRestClient,
        page: int = 1,
        page_size: int = 10,
        search: str = "",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List results, optionally filtered and limited."""
        params = {
            "page": page,
            "page_size": page_size,
            "search": search,
        }
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        generator = client.get_all_objects(ResultsUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_results_by_run_id(
        client: AttackIQRestClient, run_id: str, limit: Optional[int] = 10
    ) -> Generator[Dict[str, Any], None, None]:
        """Get assessment result summaries filtered by run ID, optionally limited."""
        endpoint_with_params = f"{ResultsUtils.ENDPOINT}?run_id={run_id}&assessment_results=true"
        logger.info(f"Fetching result summaries for run_id: {run_id} from constructed URL: {endpoint_with_params}")
        generator = client.get_all_objects(endpoint_with_params, params=None)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_result_by_id(client: AttackIQRestClient, result_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a specific result ID."""
        endpoint = f"{ResultsUtils.ENDPOINT}/{result_id}"
        logger.info(f"Attempting to fetch result details from endpoint: {endpoint}.")
        return client.get_object(endpoint)


class PhaseResultsUtils:
    """Utilities for working with phase results in the AttackIQ platform.

    API Endpoint: /v1/phase_results
    """

    ENDPOINT = "v1/phase_results"

    @staticmethod
    def get_phase_results(
        client: AttackIQRestClient,
        assessment_id: str,
        project_run_id: Optional[str] = None,
        result_summary_id: Optional[str] = None,
        limit: Optional[int] = 10,
    ) -> Generator[dict, None, None]:
        """Get phase results, optionally filtered and limited."""
        # BEWARE: created_after is NOT supported by phase_results endpoint yet
        params = {"project_id": assessment_id}
        if project_run_id:
            params["project_run"] = project_run_id
        if result_summary_id:
            params["result_summary"] = result_summary_id
        generator = client.get_all_objects(PhaseResultsUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)


class PhaseLogsUtils:
    """Utilities for working with phase logs in the AttackIQ platform.

    API Endpoint: /v1/phase_logs
    """

    ENDPOINT = "v1/phase_logs"

    @staticmethod
    def get_phase_logs(
        client: AttackIQRestClient,
        scenario_job_id: str,
        limit: Optional[int] = 10,
    ) -> Generator[dict, None, None]:
        """Get phase logs for a scenario job, optionally limited."""
        # BEWARE: created_after is NOT supported by phase_results endpoint yet
        params = {"scenario_job_id": scenario_job_id}
        generator = client.get_all_objects(PhaseLogsUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)


class TagSetUtils:
    """Utilities for working with tag sets.

    API Endpoint: /v1/tag_sets
    """

    ENDPOINT = "v1/tag_sets"

    @staticmethod
    def get_tag_set_id(client: AttackIQRestClient, tag_set_name: str) -> Optional[str]:
        """Get the ID of a tag set by its name."""
        logger.info(f"Searching for TagSet: '{tag_set_name}'")
        params = {"name": tag_set_name}
        # Tag sets are usually few, list() is fine here.
        tag_sets = list(client.get_all_objects(TagSetUtils.ENDPOINT, params=params))
        if tag_sets:
            tag_set = tag_sets[0]
            logger.info(f"TagSet '{tag_set_name}' found with ID '{tag_set['id']}'")
            return tag_set["id"]
        else:
            logger.warning(f"TagSet '{tag_set_name}' not found")
            return None

    @staticmethod
    def get_custom_tag_set_id(client: AttackIQRestClient) -> Optional[str]:
        """Get the ID of the 'Custom' tag set."""
        return TagSetUtils.get_tag_set_id(client, "Custom")


class TagUtils:
    """Utilities for managing tags in the AttackIQ platform.

    API Endpoint: /v1/tags
    """

    ENDPOINT = "v1/tags"

    @staticmethod
    def get_tags(
        client: AttackIQRestClient, params: dict = None, limit: Optional[int] = 10
    ) -> Generator[Dict[str, Any], None, None]:
        """List tags, optionally filtered and limited."""
        generator = client.get_all_objects(TagUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_tag_by_id(client: AttackIQRestClient, tag_id: str):
        """Get a specific tag by its ID."""
        return client.get_object(f"{TagUtils.ENDPOINT}/{tag_id}")

    @staticmethod
    def create_tag(client: AttackIQRestClient, tag_name: str, tag_set_id: str):
        """Create a new tag."""
        tag_data = {
            "name": tag_name,
            "display_name": tag_name,
            "tag_set": tag_set_id,
            "meta_data": None,
        }
        logger.info(f"Creating tag '{tag_name}' in tag set ID '{tag_set_id}'")
        return client.post_object(TagUtils.ENDPOINT, data=tag_data)

    @staticmethod
    def get_tag_id(client: AttackIQRestClient, tag_name: str, tag_set_id: str):
        """Get the ID of a tag by name and tag set ID."""
        params = {"name": tag_name, "tag_set": tag_set_id}
        if tags := list(client.get_all_objects(TagUtils.ENDPOINT, params=params)):
            tag = tags[0]
            logger.info(f"Tag '{tag_name}' found with ID '{tag['id']}'")
            return tag["id"]
        logger.info(f"Tag '{tag_name}' not found in custom tag set")
        return None

    @staticmethod
    def delete_tag(client: AttackIQRestClient, tag_id: str):
        """Delete a specific tag by its ID."""
        logger.info(f"Deleting tag with ID '{tag_id}'")
        return client.delete_object(f"{TagUtils.ENDPOINT}/{tag_id}")

    @staticmethod
    def get_or_create_tag(client: AttackIQRestClient, tag_name: str, tag_set_name: str) -> str:
        """Get a tag ID, creating the tag if it doesn't exist."""
        tag_set_id = TagSetUtils.get_tag_set_id(client, tag_set_name)
        if not tag_set_id:
            logger.error(f"Failed to get TagSet ID for '{tag_set_name}'")
            return ""
        tag_id = TagUtils.get_tag_id(client, tag_name, tag_set_id)
        if not tag_id:
            logger.info(f"Tag '{tag_name}' not found. Creating new tag.")
            tag = TagUtils.create_tag(client, tag_name, tag_set_id)
            if not tag:
                logger.error(f"Failed to create tag '{tag_name}'")
                return ""
            tag_id = tag["id"]
        return tag_id

    @staticmethod
    def get_or_create_custom_tag(client: AttackIQRestClient, tag_name: str) -> str:
        """Get a custom tag ID, creating the tag if it doesn't exist."""
        return TagUtils.get_or_create_tag(client, tag_name, "Custom")


class TaggedItemUtils:
    """Utilities for working with tagged items in the AttackIQ platform.

    API Endpoint: /v1/tagged_items
    """

    ENDPOINT = "v1/tagged_items"

    @staticmethod
    def get_tagged_items(
        client: AttackIQRestClient,
        content_type: str,
        object_id: str,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List tagged items for an object, optionally limited."""
        logger.info(f"Fetching tagged items for object of type: {content_type} with ID '{object_id}'")
        if content_type not in ["asset", "assessment"]:
            logger.error(f"Unsupported content type '{content_type}'. Supported types: 'asset', 'assessment'")
            return
        params = {"content_type": content_type, "object_id": object_id}
        generator = client.get_all_objects(TaggedItemUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_tagged_item(client: AttackIQRestClient, content_type: str, object_id: str, tag_id: str):
        """Get a specific tagged item linking an object and a tag."""
        params = {"content_type": content_type, "object_id": object_id, "tag": tag_id}
        items = list(client.get_all_objects(TaggedItemUtils.ENDPOINT, params=params))
        return items[0] if items else None

    @staticmethod
    def create_tagged_item(client: AttackIQRestClient, content_type: str, object_id: str, tag_id: str) -> str:
        """Create a tagged item (apply a tag to an object)."""
        logger.info(
            f"Creating tagged item with tag_id '{tag_id}' to object of type: {content_type} with ID '{object_id}'"
        )
        data = {
            "content_type": content_type,
            "object_id": object_id,
            "tag": tag_id,
        }  # tag is the tag_id
        tag_item = client.post_object(TaggedItemUtils.ENDPOINT, data)
        if tag_item:
            tag_item_id = tag_item["id"]
            logger.info(f"Successfully created tagged item with ID {tag_item_id}")
            return tag_item_id
        else:
            logger.error(f"Failed to create tag item with tag '{tag_id}' to object with ID '{object_id}'")
            return ""

    @staticmethod
    def delete_tagged_item(client: AttackIQRestClient, tagged_item_id: str) -> bool:
        """Delete a tagged item (remove a tag from an object)."""
        logger.info(f"Removing tag item with ID {tagged_item_id}")
        response = client.delete_object(f"{TaggedItemUtils.ENDPOINT}/{tagged_item_id}")
        if response:
            logger.info(f"Successfully deleted tag item with ID {tagged_item_id}")
            return True
        else:
            logger.error(f"Failed to delete tagged item with ID {tagged_item_id}")
            return False


class AssetStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class AssetUtils:
    """Utilities for working with assets a.k.a Test Points

    API Endpoint: /v1/assets, /v1/asset_jobs
    """

    ENDPOINT = "v1/assets"
    ASSET_JOBS_ENDPOINT = "v1/asset_jobs"
    JOB_NAME_DESTROY_SELF = "06230502-890c-4dca-aab1-296706758fd9"

    @staticmethod
    def get_assets(
        client: AttackIQRestClient, params: dict = None, limit: Optional[int] = 10
    ) -> Generator[Dict[str, Any], None, None]:
        """List assets, optionally filtered and limited."""
        generator = client.get_all_objects(AssetUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_asset_by_id(client: AttackIQRestClient, asset_id: str):
        """Get a specific asset by its ID."""
        return client.get_object(f"{AssetUtils.ENDPOINT}/{asset_id}")

    @staticmethod
    def get_asset_by_hostname(client: AttackIQRestClient, hostname: str) -> Optional[Dict[str, Any]]:
        """Get a specific asset by its hostname."""
        params = {"hostname": hostname}
        assets = list(client.get_all_objects(AssetUtils.ENDPOINT, params=params))
        return assets[0] if assets else None

    @staticmethod
    def uninstall_asset(client: AttackIQRestClient, asset_id: str) -> bool:
        """Submit a job to uninstall an asset."""
        logger.info(f"Uninstalling asset with ID: {asset_id}")
        payload = {
            "asset": asset_id,
            "job_name": AssetUtils.JOB_NAME_DESTROY_SELF,
            "one_way": True,
        }
        try:
            response = client.post_object(AssetUtils.ASSET_JOBS_ENDPOINT, data=payload)
            if response:
                logger.info(f"Asset {asset_id} uninstall job submitted successfully")
                return True
            else:
                logger.error(f"Failed to submit uninstall job for asset {asset_id}")
                return False
        except Exception as e:
            logger.error(f"Error while uninstalling asset {asset_id}: {str(e)}")
            return False

    @staticmethod
    def add_tag(client: AttackIQRestClient, asset_id: str, tag_id: str) -> str:
        """Add a tag to an asset."""
        return TaggedItemUtils.create_tagged_item(client, "asset", asset_id, tag_id)

    @staticmethod
    def get_total_assets(client: AttackIQRestClient) -> Optional[int]:
        """Get the total number of assets."""
        logger.info("Fetching total number of assets...")
        return client.get_total_objects_count(AssetUtils.ENDPOINT)

    @staticmethod
    def get_assets_count_by_status(client: AttackIQRestClient, status: AssetStatus) -> Optional[int]:
        """Get the count of assets with a specific status."""
        logger.info(f"Fetching count of assets with status: {status.value}...")
        params = {"status": status.value}
        return client.get_total_objects_count(AssetUtils.ENDPOINT, params=params)


class ConnectorUtils:
    """Utilities for working with company connectors.

    API Endpoint: /v1/company_connectors
    """

    ENDPOINT = "v1/company_connectors"

    @staticmethod
    def get_connectors(
        client: AttackIQRestClient, params: dict = None, limit: Optional[int] = 10
    ) -> Generator[Dict[str, Any], None, None]:
        """List connectors, optionally filtered and limited."""
        generator = client.get_all_objects(ConnectorUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_connector_by_id(client: AttackIQRestClient, connector_id: str):
        """Get a specific connector by its ID."""
        return client.get_object(f"{ConnectorUtils.ENDPOINT}/{connector_id}")


class AssessmentUtils:
    """Utilities for working with assessments providing a clean, unified API.

    API Endpoint: /v1/assessments, /v1/public/assessment, /v1/results
    """

    ASSESSMENT_ENDPOINT = "v1/assessments"
    PUBLIC_ENDPOINT = "v1/public/assessment"
    RESULTS_ENDPOINT = "v1/results"

    @staticmethod
    def get_assessments(
        client: AttackIQRestClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List all assessments, optionally filtered by params and limited to a specific count."""
        generator = client.get_all_objects(AssessmentUtils.ASSESSMENT_ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_assessment_by_id(client: AttackIQRestClient, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment information by ID using the API for better details."""
        endpoint = f"{AssessmentUtils.ASSESSMENT_ENDPOINT}/{assessment_id}"
        logger.info(f"Fetching assessment details for ID: {assessment_id}")
        return client.get_object(endpoint)

    @staticmethod
    def list_assessment_runs(
        client: AttackIQRestClient,
        assessment_id: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List all runs for a given assessment, optionally limited to a specific count."""
        endpoint = f"{AssessmentUtils.PUBLIC_ENDPOINT}/{assessment_id}/runs"
        logger.info(f"Listing assessment runs for ID: {assessment_id}")
        generator = client.get_all_objects(endpoint, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_run_status(
        client: AttackIQRestClient,
        assessment_id: str,
        run_id: str,
        without_detection: bool = True,
    ) -> Optional[Dict[str, bool]]:
        """Check if a specific run is still executing."""
        logger.info(
            f"Checking status for run {run_id} of assessment {assessment_id} without detection: {without_detection}"
        )
        for run in AssessmentUtils.list_assessment_runs(client, assessment_id):
            if run.get("id") == run_id:
                status = {
                    "scenario_jobs_in_progress": run.get("scenario_jobs_in_progress", True),
                    "integration_jobs_in_progress": run.get("integration_jobs_in_progress", True),
                    "completed": (
                        run.get("scenario_jobs_in_progress", True)
                        if without_detection
                        else run.get("integration_jobs_in_progress", True)
                    ),
                }
                return status
        logger.warning(f"Run ID {run_id} not found for assessment {assessment_id}")
        return None

    @staticmethod
    def is_run_complete(
        client: AttackIQRestClient,
        assessment_id: str,
        run_id: str,
        without_detection: bool = True,
    ) -> bool:
        """Convenience method to check if a run has completed."""
        status = AssessmentUtils.get_run_status(client, assessment_id, run_id, without_detection)
        return status.get("completed", False) if status else False

    @staticmethod
    def run_assessment(client: AttackIQRestClient, assessment_id: str) -> str:
        """Start an assessment run."""
        endpoint = f"{AssessmentUtils.ASSESSMENT_ENDPOINT}/{assessment_id}/run_all"
        run_result = client.post_object(endpoint, data={})
        if not run_result or "run_id" not in run_result:
            raise ValueError("Failed to run the assessment.")
        logger.info(f"Assessment {assessment_id} started with run ID: {run_result['run_id']}")
        return run_result["run_id"]

    @staticmethod
    def get_results_by_run_id(
        client: AttackIQRestClient,
        run_id: str,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """Get results for a specific run ID, optionally limited to a specific count."""
        params = {"run_id": run_id, "assessment_results": "true"}
        logger.info(f"Fetching results for run ID: {run_id}")
        generator = client.get_all_objects(AssessmentUtils.RESULTS_ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_result_details(client: AttackIQRestClient, result_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific result."""
        endpoint = f"{AssessmentUtils.RESULTS_ENDPOINT}/{result_id}"
        logger.info(f"Fetching detailed result for ID: {result_id}")
        return client.get_object(endpoint)

    @staticmethod
    def get_assets_in_assessment(
        client: AttackIQRestClient,
        assessment_id: str,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List assets associated with an assessment, optionally limited to a specific count."""
        params = {"hide_hosted_agents": "true", "project_id": assessment_id}
        logger.info(f"Listing assets for assessment ID: {assessment_id}")
        generator = AssetUtils.get_assets(client, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def wait_for_run_completion(
        client: AttackIQRestClient,
        assessment_id: str,
        run_id: str,
        timeout: int = 600,
        check_interval: int = 10,
        without_detection: bool = True,
    ) -> bool:
        """Wait for a run to complete, with timeout."""
        logger.info(
            f"Waiting for run {run_id} of assessment {assessment_id} to complete without detection: {without_detection}"
        )
        start_time = time.time()

        while time.time() - start_time < timeout:
            if AssessmentUtils.is_run_complete(client, assessment_id, run_id, without_detection):
                elapsed_time = round(time.time() - start_time, 2)
                logger.info(f"Run completed in {elapsed_time} seconds")
                return True

            if check_interval > 1:
                logger.info(f"Run still in progress. Waiting {check_interval} seconds...")
            time.sleep(check_interval)

        logger.warning(f"Run did not complete within {timeout} seconds")
        return False


class UnifiedMitigationUtils:
    """Utilities for interacting with Unified Mitigation rules.

    API Endpoint: /v1/unified_mitigations
    """

    ENDPOINT = "v1/unified_mitigations"

    @staticmethod
    def list_mitigations(
        client: AttackIQRestClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List all unified mitigation rules, optionally filtered and limited."""
        logger.info(f"Listing unified mitigations with params: {params}")
        generator = client.get_all_objects(UnifiedMitigationUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_mitigation(client: AttackIQRestClient, mitigation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific unified mitigation rule by its ID."""
        endpoint = f"{UnifiedMitigationUtils.ENDPOINT}/{mitigation_id}"
        logger.info(f"Getting unified mitigation: {mitigation_id}")
        return client.get_object(endpoint)

    @staticmethod
    def create_mitigation(client: AttackIQRestClient, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new unified mitigation rule."""
        logger.info(f"Creating unified mitigation with data: {data}")
        return client.post_object(UnifiedMitigationUtils.ENDPOINT, data=data)

    @staticmethod
    def update_mitigation(
        client: AttackIQRestClient, mitigation_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing unified mitigation rule (PUT)."""
        endpoint = f"{UnifiedMitigationUtils.ENDPOINT}/{mitigation_id}"
        logger.info(f"Updating unified mitigation {mitigation_id} with data: {data}")
        url = client._build_url(endpoint)
        return client._make_request(url, method="put", json=data)

    @staticmethod
    def partial_update_mitigation(
        client: AttackIQRestClient, mitigation_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Partially update an existing unified mitigation rule (PATCH)."""
        endpoint = f"{UnifiedMitigationUtils.ENDPOINT}/{mitigation_id}"
        logger.info(f"Partially updating unified mitigation {mitigation_id} with data: {data}")
        url = client._build_url(endpoint)
        return client._make_request(url, method="patch", json=data)

    @staticmethod
    def delete_mitigation(client: AttackIQRestClient, mitigation_id: str) -> bool:
        """Delete a unified mitigation rule."""
        endpoint = f"{UnifiedMitigationUtils.ENDPOINT}/{mitigation_id}"
        logger.info(f"Deleting unified mitigation: {mitigation_id}")
        response = client.delete_object(endpoint)
        # DELETE returns 204 No Content on success
        return response is not None and response.get("status_code") == HTTPStatus.NO_CONTENT


class UnifiedMitigationProjectUtils:
    """Utilities for interacting with Unified Mitigation Project associations.

    API Endpoint: /v1/unified_mitigation_projects
    """

    ENDPOINT = "v1/unified_mitigation_projects"

    @staticmethod
    def list_associations(
        client: AttackIQRestClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List all unified mitigation project associations, optionally filtered and limited."""
        logger.info(f"Listing unified mitigation project associations with params: {params}")
        generator = client.get_all_objects(UnifiedMitigationProjectUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_association(client: AttackIQRestClient, association_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific unified mitigation project association by its ID."""
        endpoint = f"{UnifiedMitigationProjectUtils.ENDPOINT}/{association_id}"
        logger.info(f"Getting unified mitigation project association: {association_id}")
        return client.get_object(endpoint)

    @staticmethod
    def create_association(client: AttackIQRestClient, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new unified mitigation project association."""
        logger.info(f"Creating unified mitigation project association with data: {data}")
        # POST endpoints don't need trailing slashes based on the API examples
        return client.post_object(UnifiedMitigationProjectUtils.ENDPOINT, data=data)

    @staticmethod
    def partial_update_association(
        client: AttackIQRestClient, association_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Partially update an existing unified mitigation project association (PATCH)."""
        endpoint = f"{UnifiedMitigationProjectUtils.ENDPOINT}/{association_id}"
        logger.info(f"Partially updating unified mitigation project association {association_id} with data: {data}")
        url = client._build_url(endpoint)
        return client._make_request(url, method="patch", json=data)

    @staticmethod
    def delete_association(client: AttackIQRestClient, association_id: str) -> bool:
        """Delete a unified mitigation project association."""
        endpoint = f"{UnifiedMitigationProjectUtils.ENDPOINT}/{association_id}"
        logger.info(f"Deleting unified mitigation project association: {association_id}")
        response = client.delete_object(endpoint)
        return response is not None and response.get("status_code") == HTTPStatus.NO_CONTENT


class UnifiedMitigationWithRelationsUtils:
    """Utilities for read-only access to Unified Mitigations with related data.

    API Endpoint: /v1/unified_mitigations_with_relations
    """

    ENDPOINT = "v1/unified_mitigations_with_relations"

    @staticmethod
    def list_mitigations_with_relations(
        client: AttackIQRestClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List all unified mitigations with relations, optionally filtered and limited."""
        logger.info(f"Listing unified mitigations with relations, params: {params}")
        generator = client.get_all_objects(UnifiedMitigationWithRelationsUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_mitigation_with_relations(client: AttackIQRestClient, mitigation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific unified mitigation with relations by its ID."""
        endpoint = f"{UnifiedMitigationWithRelationsUtils.ENDPOINT}/{mitigation_id}"
        logger.info(f"Getting unified mitigation with relations: {mitigation_id}")
        return client.get_object(endpoint)

    @staticmethod
    def get_overview(client: AttackIQRestClient, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get the overview data for unified mitigations with relations."""
        endpoint = f"{UnifiedMitigationWithRelationsUtils.ENDPOINT}/overview"
        logger.info(f"Getting unified mitigation overview with params: {params}")
        return client.get_object(endpoint, params=params)


class UnifiedMitigationReportingUtils:
    """Utilities for Unified Mitigation reporting endpoints.

    API Endpoint: /v3/reporting/unified_mitigation_detection_performance_timeline
    """

    ENDPOINT = "v3/reporting/unified_mitigation_detection_performance_timeline"

    @staticmethod
    def get_detection_performance_timeline(
        client: AttackIQRestClient, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get detection performance timeline data, optionally filtering."""
        logger.info(f"Getting detection performance timeline with params: {params}")
        # This endpoint likely returns a single JSON object, not paginated results
        return client.get_object(UnifiedMitigationReportingUtils.ENDPOINT, params=params)


class ScenarioUtils:
    """Utilities for interacting with Scenario models.

    API Endpoint: /v1/scenarios
    """

    ENDPOINT = "v1/scenarios"

    @staticmethod
    def list_scenarios(
        client: AttackIQRestClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """List all scenarios, optionally filtered and limited."""
        logger.info(f"Listing scenarios with params: {params}")
        generator = client.get_all_objects(ScenarioUtils.ENDPOINT, params=params)
        yield from itertools.islice(generator, limit)

    @staticmethod
    def get_scenario(client: AttackIQRestClient, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario by its ID."""
        endpoint = f"{ScenarioUtils.ENDPOINT}/{scenario_id}"
        logger.info(f"Getting scenario: {scenario_id}")
        return client.get_object(endpoint)

    @staticmethod
    def save_copy(client: AttackIQRestClient, scenario_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a copy of an existing scenario."""
        endpoint = f"{ScenarioUtils.ENDPOINT}/{scenario_id}/save_copy"
        logger.info(f"Creating copy of scenario {scenario_id} with data: {data}")
        return client.post_object(endpoint, data=data)

    @staticmethod
    def delete_scenario(client: AttackIQRestClient, scenario_id: str) -> bool:
        """Delete a specific scenario by its ID."""
        endpoint = f"{ScenarioUtils.ENDPOINT}/{scenario_id}"
        logger.info(f"Deleting scenario: {scenario_id}")
        response = client.delete_object(endpoint)
        # Typically, a successful DELETE returns 204 No Content
        if response is not None and 200 <= response["status_code"] < 300:
            logger.info(f"Successfully deleted scenario: {scenario_id}")
            return True
        else:
            logger.error(f"Failed to delete scenario: {scenario_id}")
            return False
