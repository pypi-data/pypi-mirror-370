import os
from typing import List, Optional
import requests
import httpx
import asyncio

from tako.types.common.exceptions import (
    RelevantResultsNotFoundException,
    raise_exception_from_response,
)
from tako.types.knowledge_search.types import (
    KnowledgeSearchOutputs,
    KnowledgeSearchRequestOutputSettings,
    KnowledgeSearchResults,
    KnowledgeSearchSourceIndex,
)
from tako.types.visualize.types import (
    TakoDataFormatDataset,
    UserRequestedVizComponentType,
    VisualizeRequest,
    VisualizeSupportedModels,
)

TAKO_API_KEY = os.getenv("TAKO_API_KEY", None)
TAKO_SERVER_URL = os.getenv("TAKO_SERVER_URL", "https://trytako.com/")
TAKO_API_VERSION = os.getenv("TAKO_API_VERSION", "v1")


class TakoClient:
    def __init__(
        self,
        api_key: Optional[str] = TAKO_API_KEY,
        server_url: Optional[str] = TAKO_SERVER_URL,
        api_version: Optional[str] = TAKO_API_VERSION,
    ):
        assert api_key is not None, "API key is required"
        self.api_key = api_key
        self.server_url = server_url
        self.api_version = api_version

    def knowledge_search(
        self,
        text: str,
        source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = [
            KnowledgeSearchSourceIndex.TAKO,
        ],
        output_settings: Optional[KnowledgeSearchRequestOutputSettings] = None,
        country_code: Optional[str] = "US",
    ) -> KnowledgeSearchResults:
        """
        Search for knowledge cards based on a text query.

        Args:
            text: The text to search for.
            source_indexes: The source indexes to search for.

        Returns:
            A list of knowledge search results.

        Raises:
            APIException: If the API returns an error.
        """
        url = f"{self.server_url}/api/{self.api_version}/knowledge_search"
        payload = {
            "inputs": {
                "text": text,
            },
        }
        if source_indexes:
            payload["source_indexes"] = source_indexes
        if output_settings:
            payload["output_settings"] = output_settings.model_dump()
        if country_code:
            payload["country_code"] = country_code

        response = requests.post(url, json=payload, headers={"X-API-Key": self.api_key})
        try:
            # Based on the response, raise an exception if the response is an error
            raise_exception_from_response(response)
        except RelevantResultsNotFoundException:
            # For cases where no relevant results are found, return an empty list
            # instead of raising an exception
            return KnowledgeSearchResults(
                outputs=KnowledgeSearchOutputs(knowledge_cards=[])
            )

        return KnowledgeSearchResults.model_validate(response.json())

    def get_image(self, card_id: str) -> bytes:
        """
        Get an image for a knowledge card.

        Args:
            card_id: The ID of the knowledge card.

        Returns:
            The image as bytes.
        """
        url = f"{self.server_url}/api/{self.api_version}/image/{card_id}/"
        response = requests.get(
            url,
            headers={
                "Accept": "image/*",
            },
        )
        return response.content

    def beta_visualize(
        self,
        tako_formatted_dataset: Optional[TakoDataFormatDataset] = None,
        file_id: Optional[str] = None,
        query: Optional[str] = None,
        model: Optional[VisualizeSupportedModels] = None,
        output_settings: Optional[KnowledgeSearchRequestOutputSettings] = None,
        viz_component_type: Optional[UserRequestedVizComponentType] = None,
    ) -> KnowledgeSearchResults:
        url = f"{self.server_url}/api/{self.api_version}/beta/visualize"
        if tako_formatted_dataset is None and file_id is None:
            raise ValueError(
                "Either tako_formatted_dataset or file_id must be provided"
            )
        if tako_formatted_dataset is not None and file_id is not None:
            raise ValueError(
                "Only one of tako_formatted_dataset or file_id must be provided"
            )
        visualize_request = VisualizeRequest(
            tako_formatted_dataset=tako_formatted_dataset,
            file_id=file_id,
            query=query,
            model=model,
            output_settings=output_settings,
            viz_component_type=viz_component_type,
        )
        payload = visualize_request.model_dump()
        response = requests.post(url, json=payload, headers={"X-API-Key": self.api_key})
        raise_exception_from_response(response)
        return KnowledgeSearchResults.model_validate(response.json())

    def _get_presigned_url(
        self, file_name: str, file_context: Optional[str] = None, source: Optional[str] = None
    ) -> dict:
        url = f"{self.server_url}/api/{self.api_version}/beta/file_upload_url"
        params = {"file_name": file_name}
        if file_context:
            params["file_context"] = file_context
        if source:
            params["source"] = source
        response = requests.get(
            url,
            params=params,
            headers={"X-API-Key": self.api_key, "Accept": "application/json"},
        )
        raise_exception_from_response(response)
        return response.json()

    def _upload_file(self, file_path: str, upload_info: dict) -> None:
        """Upload file using presigned URL and fields."""
        with open(file_path, "rb") as f:
            # Prepare form data with all required fields
            files = {"file": (os.path.basename(file_path), f)}
            data = upload_info["fields"]

            # POST to the presigned URL
            response = requests.post(upload_info["url"], files=files, data=data)
            response.raise_for_status()  # Raises exception for HTTP errors

    def beta_upload_file(
        self, file_path: str, file_context: Optional[str] = None, source: Optional[str] = None
    ) -> str:
        """Upload a file and return the file ID.

        Args:
            file_path: Path to the file to upload.

        Returns:
            The file ID.

        """
        file_name = os.path.basename(file_path)

        # Step 1: Get presigned URL and upload fields
        upload_info = self._get_presigned_url(
            file_name=file_name, file_context=file_context, source=source
        )

        # Step 2: Upload the file using the presigned URL
        self._upload_file(file_path, upload_info)

        # Return the file ID
        return upload_info["file_id"]

    def beta_file_connector(self, file_url: str, file_id: Optional[str] = None) -> dict:
        """
        Connect to a hosted file via URL.

        Args:
            file_url: URL of the file to connect to.
            file_id: ID of the file to connect to. If not provided, a new file ID will be generated.

        Returns:
            Dictionary containing 'message' and 'id' fields.

        Raises:
            APIException: If the API returns an error.
        """
        url = f"{self.server_url}/api/{self.api_version}/beta/file_connector"
        payload = {
            "file_url": file_url,
        }
        if file_id is not None:
            payload["file_id"] = file_id

        response = requests.post(url, json=payload, headers={"X-API-Key": self.api_key})
        raise_exception_from_response(response)
        return response.json()


class AsyncTakoClient:
    def __init__(
        self,
        api_key: Optional[str] = TAKO_API_KEY,
        server_url: Optional[str] = TAKO_SERVER_URL,
        api_version: Optional[str] = TAKO_API_VERSION,
        default_timeout_seconds: Optional[float] = 30.0,
    ):
        assert api_key is not None, "API key is required"
        self.api_key = api_key
        self.server_url = server_url.strip("/")
        self.api_version = api_version
        self.default_timeout_seconds = default_timeout_seconds

    async def knowledge_search(
        self,
        text: str,
        source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> KnowledgeSearchResults:
        """
        Async search for knowledge cards based on a text query.

        Args:
            text: The text to search for.
            source_indexes: The source indexes to search for.

        Returns:
            A list of knowledge search results.

        Raises:
            APIException: If the API returns an error.
        """
        # Trailing slash is required for httpx
        url = f"{self.server_url}/api/{self.api_version}/knowledge_search/"
        payload = {
            "inputs": {
                "text": text,
            },
        }
        if source_indexes:
            payload["source_indexes"] = source_indexes

        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.post(
                url, json=payload, headers={"X-API-Key": self.api_key}
            )
            return KnowledgeSearchResults.model_validate(response.json())

    async def get_image(
        self, card_id: str, timeout_seconds: Optional[float] = None
    ) -> bytes:
        """
        Async get an image for a knowledge card.

        Args:
            card_id: The ID of the knowledge card.

        Returns:
            The image as bytes.
        """
        # Trailing slash is required for httpx
        url = f"{self.server_url}/api/{self.api_version}/image/{card_id}/"
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.get(
                url,
                headers={
                    "Accept": "image/*",
                },
            )
            return response.content

    async def beta_visualize(
        self,
        tako_formatted_dataset: Optional[TakoDataFormatDataset] = None,
        file_id: Optional[str] = None,
        query: Optional[str] = None,
        model: Optional[VisualizeSupportedModels] = None,
        timeout_seconds: Optional[float] = None,
    ) -> KnowledgeSearchResults:
        url = f"{self.server_url}/api/{self.api_version}/beta/visualize"
        if tako_formatted_dataset is None and file_id is None:
            raise ValueError(
                "Either tako_formatted_dataset or file_id must be provided"
            )
        if tako_formatted_dataset is not None and file_id is not None:
            raise ValueError(
                "Only one of tako_formatted_dataset or file_id must be provided"
            )
        visualize_request = VisualizeRequest(
            tako_formatted_dataset=tako_formatted_dataset,
            file_id=file_id,
            query=query,
            model=model,
        )
        payload = visualize_request.model_dump()
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.post(
                url, json=payload, headers={"X-API-Key": self.api_key}
            )
            raise_exception_from_response(response)
            return KnowledgeSearchResults.model_validate(response.json())

    async def _get_presigned_url(
        self,
        file_name: str,
        timeout_seconds: Optional[float] = None,
        file_context: Optional[str] = None,
        source: Optional[str] = None,
    ) -> dict:
        """Async get presigned URL for file upload."""
        url = f"{self.server_url}/api/{self.api_version}/beta/file_upload_url"
        params = {"file_name": file_name}
        if file_context:
            params["file_context"] = file_context
        if source:
            params["source"] = source
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.get(
                url,
                params=params,
                headers={"X-API-Key": self.api_key, "Accept": "application/json"},
            )
            raise_exception_from_response(response)
            return response.json()

    async def _upload_file(
        self, file_path: str, upload_info: dict, timeout_seconds: Optional[float] = None
    ) -> None:
        """Async upload file using presigned URL and fields."""
        # Run file reading in a thread pool executor
        file_content = await asyncio.to_thread(lambda: open(file_path, "rb").read())

        # Prepare form data with all required fields
        files = {"file": (os.path.basename(file_path), file_content)}
        data = upload_info["fields"]

        # POST to the presigned URL
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.post(upload_info["url"], files=files, data=data)
            response.raise_for_status()  # Raises exception for HTTP errors

    async def beta_upload_file(
        self,
        file_path: str,
        timeout_seconds: Optional[float] = None,
        file_context: Optional[str] = None,
        source: Optional[str] = None,
    ) -> str:
        """Async upload a file and return the file ID."""
        file_name = os.path.basename(file_path)

        # Step 1: Get presigned URL and upload fields
        upload_info = await self._get_presigned_url(
            file_name=file_name,
            timeout_seconds=timeout_seconds,
            file_context=file_context,
            source=source,
        )

        # Step 2: Upload the file using the presigned URL
        await self._upload_file(file_path, upload_info, timeout_seconds)

        # Return the file ID
        return upload_info["file_id"]

    async def beta_file_connector(
        self,
        file_url: str,
        file_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        source: Optional[str] = None,
    ) -> dict:
        """
        Async connect your file to Tako for visualization and analysis.

        Args:
            file_url: URL of the file to connect to.
            file_id: ID of the file to connect to. If not provided, a new file ID will be generated.
            timeout_seconds: Timeout for the request.

        Returns:
            Dictionary containing 'message' and 'id' fields.

        Raises:
            APIException: If the API returns an error.
        """
        url = f"{self.server_url}/api/{self.api_version}/beta/file_connector"
        payload = {
            "file_url": file_url,
        }
        if file_id is not None:
            payload["file_id"] = file_id
        if source:
            payload["source"] = source
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.post(
                url, json=payload, headers={"X-API-Key": self.api_key}
            )
            raise_exception_from_response(response)
            return response.json()
