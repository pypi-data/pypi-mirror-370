from __future__ import annotations

import io
import os
import datetime
from typing import Any, Dict, List, Optional

import httpx
import pytest
from respx import MockRouter

from replicate import Replicate, AsyncReplicate
from replicate._compat import model_dump
from replicate.lib._files import FileOutput, AsyncFileOutput
from replicate._exceptions import ModelError, NotFoundError, BadRequestError
from replicate.lib._models import Model, Version, ModelVersionIdentifier
from replicate.types.file_create_response import URLs, Checksums, FileCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
bearer_token = "My Bearer Token"


# Mock prediction data for testing
def create_mock_prediction(
    status: str = "succeeded",
    output: Any = "test output",
    error: Optional[str] = None,
    logs: Optional[str] = None,
    urls: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    if urls is None:
        urls = {
            "get": "https://api.replicate.com/v1/predictions/test_prediction_id",
            "cancel": "https://api.replicate.com/v1/predictions/test_prediction_id/cancel",
            "web": "https://replicate.com/p/test_prediction_id",
        }

    return {
        "id": "test_prediction_id",
        "version": "test_version",
        "status": status,
        "input": {"prompt": "test prompt"},
        "output": output,
        "error": error,
        "logs": logs,
        "created_at": "2023-01-01T00:00:00Z",
        "started_at": "2023-01-01T00:00:01Z",
        "completed_at": "2023-01-01T00:00:02Z" if status in ["succeeded", "failed"] else None,
        "urls": urls,
        "model": "test-model",
        "data_removed": False,
    }


def _version_with_schema(id: str = "v1", output_schema: Optional[object] = None) -> Version:
    return Version(
        id=id,
        created_at=datetime.datetime.fromisoformat("2022-03-16T00:35:56.210272"),
        cog_version="dev",
        openapi_schema={
            "openapi": "3.0.2",
            "info": {"title": "Cog", "version": "0.1.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Input": {
                        "type": "object",
                        "title": "Input",
                        "required": ["text"],
                        "properties": {
                            "text": {
                                "type": "string",
                                "title": "Text",
                                "x-order": 0,
                                "description": "The text input",
                            },
                        },
                    },
                    "Output": output_schema
                    or {
                        "type": "string",
                        "title": "Output",
                    },
                }
            },
        },
    )


class TestRun:
    client = Replicate(base_url=base_url, bearer_token=bearer_token, _strict_response_validation=True)

    # Common model reference format that will work with the new SDK
    model_ref = "owner/name:version"
    file_create_response = FileCreateResponse(
        id="test_file_id",
        checksums=Checksums(sha256="test_sha256"),
        content_type="application/octet-stream",
        created_at=datetime.datetime.now(),
        expires_at=datetime.datetime.now() + datetime.timedelta(days=1),
        metadata={},
        size=1234,
        urls=URLs(get="https://api.replicate.com/v1/files/test_file_id"),
    )

    @pytest.mark.respx(base_url=base_url)
    def test_run_basic(self, respx_mock: MockRouter) -> None:
        """Test basic model run functionality."""
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = self.client.run(self.model_ref, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_wait_true(self, respx_mock: MockRouter) -> None:
        """Test run with wait=True parameter."""
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = self.client.run(self.model_ref, wait=True, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_wait_int(self, respx_mock: MockRouter) -> None:
        """Test run with wait as an integer value."""
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = self.client.run(self.model_ref, wait=10, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_without_wait(self, respx_mock: MockRouter) -> None:
        """Test run with wait=False parameter."""
        # Initial prediction state is "processing"
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(status="processing"))
        )

        # When we wait for it, it becomes "succeeded"
        respx_mock.get("/predictions/test_prediction_id").mock(
            return_value=httpx.Response(200, json=create_mock_prediction(status="succeeded"))
        )

        output: Any = self.client.run(self.model_ref, wait=False, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url, assert_all_mocked=False)
    def test_run_with_file_output(self, respx_mock: MockRouter) -> None:
        """Test run with file output."""
        # Mock prediction with file URL output
        file_url = "https://replicate.delivery/output.png"
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=file_url))
        )

        output: Any = self.client.run(self.model_ref, input={"prompt": "generate image"})

        assert isinstance(output, FileOutput)
        assert output.url == file_url

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_data_uri_output(self, respx_mock: MockRouter) -> None:
        """Test run with data URI output."""
        # Create a data URI for a small PNG image (1x1 transparent pixel)
        data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

        # Mock prediction with data URI output
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=data_uri))
        )

        # Use a valid model version ID format
        output: Any = self.client.run("owner/name:version", input={"prompt": "generate small image"})

        assert isinstance(output, FileOutput)
        assert output.url == data_uri

        # Test that we can read the data
        image_data = output.read()
        assert isinstance(image_data, bytes)
        assert len(image_data) > 0

        # Test that we can iterate over the data
        chunks = list(output)
        assert len(chunks) == 1
        assert chunks[0] == image_data

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_file_list_output(self, respx_mock: MockRouter) -> None:
        """Test run with list of file outputs."""
        # Create a mock prediction response with a list of file URLs
        file_urls = ["https://replicate.delivery/output1.png", "https://replicate.delivery/output2.png"]
        mock_prediction = create_mock_prediction()
        mock_prediction["output"] = file_urls

        # Mock the endpoint
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=mock_prediction))

        output: list[FileOutput] = self.client.run(
            self.model_ref, use_file_output=True, input={"prompt": "generate multiple images"}
        )

        assert isinstance(output, list)
        assert len(output) == 2
        assert all(isinstance(item, FileOutput) for item in output)

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_dict_file_output(self, respx_mock: MockRouter) -> None:
        """Test run with dictionary of file outputs."""
        # Mock prediction with dict of file URLs
        file_urls = {
            "image1": "https://replicate.delivery/output1.png",
            "image2": "https://replicate.delivery/output2.png",
        }
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=file_urls))
        )

        output: Dict[str, FileOutput] = self.client.run(self.model_ref, input={"prompt": "structured output"})

        assert isinstance(output, dict)
        assert len(output) == 2
        assert all(isinstance(item, FileOutput) for item in output.values())

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_error(self, respx_mock: MockRouter) -> None:
        """Test run with model error."""
        # Mock prediction with error
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(status="failed", error="Model error occurred"))
        )

        with pytest.raises(ModelError):
            self.client.run(self.model_ref, input={"prompt": "trigger error"})

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_base64_file(self, respx_mock: MockRouter) -> None:
        """Test run with base64 encoded file input."""
        # Create a simple file-like object
        file_obj = io.BytesIO(b"test content")

        # Mock the prediction response
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = self.client.run(self.model_ref, input={"file": file_obj}, file_encoding_strategy="base64")

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_file_upload(self, respx_mock: MockRouter) -> None:
        """Test run with base64 encoded file input."""
        # Create a simple file-like object
        file_obj = io.BytesIO(b"test content")

        # Mock the prediction response
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))
        # Mock the file upload endpoint
        respx_mock.post("/files").mock(
            return_value=httpx.Response(201, json=model_dump(self.file_create_response, mode="json"))
        )

        output: Any = self.client.run(self.model_ref, input={"file": file_obj})

        assert output == "test output"

    def test_run_with_prefer_conflict(self) -> None:
        """Test run with conflicting wait and prefer parameters."""
        with pytest.raises(TypeError, match="cannot mix and match prefer and wait"):
            self.client.run(self.model_ref, wait=True, prefer="nowait", input={"prompt": "test"})

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_iterator(self, respx_mock: MockRouter) -> None:
        """Test run with an iterator output."""
        # Create a mock prediction with an iterator output
        output_iterator = ["chunk1", "chunk2", "chunk3"]
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=output_iterator))
        )

        output: list[str] = self.client.run(self.model_ref, input={"prompt": "generate iterator"})

        assert isinstance(output, list)
        assert len(output) == 3
        assert output == output_iterator

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_invalid_identifier(self, respx_mock: MockRouter) -> None:
        """Test run with an invalid model identifier."""
        # Mock a 404 response for an invalid model identifier
        respx_mock.post("/predictions").mock(return_value=httpx.Response(404, json={"detail": "Model not found"}))

        with pytest.raises(NotFoundError):
            self.client.run("invalid/model:ref", input={"prompt": "test prompt"})

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_invalid_cog_version(self, respx_mock: MockRouter) -> None:
        """Test run with an invalid Cog version."""
        # Mock an error response for an invalid Cog version
        respx_mock.post("/predictions").mock(return_value=httpx.Response(400, json={"detail": "Invalid Cog version"}))

        with pytest.raises(BadRequestError):
            self.client.run("invalid/cog:model", input={"prompt": "test prompt"})

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_model_object(self, respx_mock: MockRouter) -> None:
        """Test run with Model object reference."""
        # Mock the models endpoint for owner/name lookup
        respx_mock.post("/models/test-owner/test-model/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction())
        )

        model = Model(owner="test-owner", name="test-model")
        output = self.client.run(model, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_version_object(self, respx_mock: MockRouter) -> None:
        """Test run with Version object reference."""
        # Version ID is used directly
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        version = _version_with_schema("test-version-id")
        output = self.client.run(version, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_model_version_identifier(self, respx_mock: MockRouter) -> None:
        """Test run with ModelVersionIdentifier dict reference."""
        # Case where version ID is provided
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        identifier = ModelVersionIdentifier(owner="test-owner", name="test-model", version="test-version-id")
        output = self.client.run(identifier, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    def test_run_with_file_output_iterator(self, respx_mock: MockRouter) -> None:
        """Test run with file output iterator."""
        # Mock URLs for file outputs
        file_urls = [
            "https://replicate.delivery/output1.png",
            "https://replicate.delivery/output2.png",
            "https://replicate.delivery/output3.png",
        ]

        # Initial response with processing status and no output
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(status="processing", output=None))
        )

        # First poll returns still processing
        respx_mock.get("/predictions/test_prediction_id").mock(
            return_value=httpx.Response(200, json=create_mock_prediction(status="processing", output=None))
        )

        # Second poll returns success with file URLs
        respx_mock.get("/predictions/test_prediction_id").mock(
            return_value=httpx.Response(200, json=create_mock_prediction(output=file_urls))
        )

        output: list[FileOutput] = self.client.run(
            self.model_ref, use_file_output=True, wait=False, input={"prompt": "generate file iterator"}
        )

        assert isinstance(output, list)
        assert len(output) == 3
        assert all(isinstance(item, FileOutput) for item in output)
        assert [item.url for item in output] == file_urls


class TestAsyncRun:
    client = AsyncReplicate(base_url=base_url, bearer_token=bearer_token, _strict_response_validation=True)

    # Common model reference format that will work with the new SDK
    model_ref = "owner/name:version"
    file_create_response = FileCreateResponse(
        id="test_file_id",
        checksums=Checksums(sha256="test_sha256"),
        content_type="application/octet-stream",
        created_at=datetime.datetime.now(),
        expires_at=datetime.datetime.now() + datetime.timedelta(days=1),
        metadata={},
        size=1234,
        urls=URLs(get="https://api.replicate.com/v1/files/test_file_id"),
    )

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_basic(self, respx_mock: MockRouter) -> None:
        """Test basic async model run functionality."""
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = await self.client.run(self.model_ref, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_wait_true(self, respx_mock: MockRouter) -> None:
        """Test async run with wait=True parameter."""
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = await self.client.run(self.model_ref, wait=True, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_wait_int(self, respx_mock: MockRouter) -> None:
        """Test async run with wait as an integer value."""
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = await self.client.run(self.model_ref, wait=10, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_without_wait(self, respx_mock: MockRouter) -> None:
        """Test async run with wait=False parameter."""
        # Initial prediction state is "processing"
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(status="processing"))
        )

        # When we wait for it, it becomes "succeeded"
        respx_mock.get("/predictions/test_prediction_id").mock(
            return_value=httpx.Response(200, json=create_mock_prediction(status="succeeded"))
        )

        output: Any = await self.client.run(self.model_ref, wait=False, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url, assert_all_mocked=False)
    async def test_async_run_with_file_output(self, respx_mock: MockRouter) -> None:
        """Test async run with file output."""
        # Mock prediction with file URL output
        file_url = "https://replicate.delivery/output.png"
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=file_url))
        )

        output: Any = await self.client.run(self.model_ref, input={"prompt": "generate image"})

        assert isinstance(output, AsyncFileOutput)
        assert output.url == file_url

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_data_uri_output(self, respx_mock: MockRouter) -> None:
        """Test async run with data URI output."""
        # Create a data URI for a small PNG image (1x1 transparent pixel)
        data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

        # Mock prediction with data URI output
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=data_uri))
        )

        # Use a valid model version ID format
        output: Any = await self.client.run("owner/name:version", input={"prompt": "generate small image"})

        assert isinstance(output, AsyncFileOutput)
        assert output.url == data_uri

        # Test that we can read the data asynchronously
        image_data = await output.read()
        assert isinstance(image_data, bytes)
        assert len(image_data) > 0

        # Test that we can iterate over the data asynchronously
        chunks: List[Any] = []
        async for chunk in output:
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0] == image_data

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_file_list_output(self, respx_mock: MockRouter) -> None:
        """Test async run with list of file outputs."""
        # Create a mock prediction response with a list of file URLs
        file_urls = ["https://replicate.delivery/output1.png", "https://replicate.delivery/output2.png"]
        mock_prediction = create_mock_prediction()
        mock_prediction["output"] = file_urls

        # Mock the endpoint
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=mock_prediction))

        output: list[AsyncFileOutput] = await self.client.run(
            self.model_ref, input={"prompt": "generate multiple images"}
        )

        assert isinstance(output, list)
        assert len(output) == 2
        assert all(isinstance(item, AsyncFileOutput) for item in output)

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_dict_file_output(self, respx_mock: MockRouter) -> None:
        """Test async run with dictionary of file outputs."""
        # Mock prediction with dict of file URLs
        file_urls = {
            "image1": "https://replicate.delivery/output1.png",
            "image2": "https://replicate.delivery/output2.png",
        }
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=file_urls))
        )

        output: Dict[str, AsyncFileOutput] = await self.client.run(
            self.model_ref, input={"prompt": "structured output"}
        )

        assert isinstance(output, dict)
        assert len(output) == 2
        assert all(isinstance(item, AsyncFileOutput) for item in output.values())

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_error(self, respx_mock: MockRouter) -> None:
        """Test async run with model error."""
        # Mock prediction with error
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(status="failed", error="Model error occurred"))
        )

        with pytest.raises(ModelError):
            await self.client.run(self.model_ref, input={"prompt": "trigger error"})

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_base64_file(self, respx_mock: MockRouter) -> None:
        """Test async run with base64 encoded file input."""
        # Create a simple file-like object
        file_obj = io.BytesIO(b"test content")

        # Mock the prediction response
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        output: Any = await self.client.run(self.model_ref, input={"file": file_obj}, file_encoding_strategy="base64")

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_file_upload(self, respx_mock: MockRouter) -> None:
        """Test async run with base64 encoded file input."""
        # Create a simple file-like object
        file_obj = io.BytesIO(b"test content")

        # Mock the prediction response
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))
        # Mock the file upload endpoint
        respx_mock.post("/files").mock(
            return_value=httpx.Response(201, json=model_dump(self.file_create_response, mode="json"))
        )

        output: Any = await self.client.run(self.model_ref, input={"file": file_obj})

        assert output == "test output"

    async def test_async_run_with_prefer_conflict(self) -> None:
        """Test async run with conflicting wait and prefer parameters."""
        with pytest.raises(TypeError, match="cannot mix and match prefer and wait"):
            await self.client.run(self.model_ref, wait=True, prefer="nowait", input={"prompt": "test"})

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_iterator(self, respx_mock: MockRouter) -> None:
        """Test async run with an iterator output."""
        # Create a mock prediction with an iterator output
        output_iterator = ["chunk1", "chunk2", "chunk3"]
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(output=output_iterator))
        )

        output: list[str] = await self.client.run(self.model_ref, input={"prompt": "generate iterator"})

        assert isinstance(output, list)
        assert len(output) == 3
        assert output == output_iterator

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_invalid_identifier(self, respx_mock: MockRouter) -> None:
        """Test async run with an invalid model identifier."""
        # Mock a 404 response for an invalid model identifier
        respx_mock.post("/predictions").mock(return_value=httpx.Response(404, json={"detail": "Model not found"}))

        with pytest.raises(NotFoundError):
            await self.client.run("invalid/model:ref", input={"prompt": "test prompt"})

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_invalid_cog_version(self, respx_mock: MockRouter) -> None:
        """Test async run with an invalid Cog version."""
        # Mock an error response for an invalid Cog version
        respx_mock.post("/predictions").mock(return_value=httpx.Response(400, json={"detail": "Invalid Cog version"}))

        with pytest.raises(BadRequestError):
            await self.client.run("invalid/cog:model", input={"prompt": "test prompt"})

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_model_object(self, respx_mock: MockRouter) -> None:
        """Test async run with Model object reference."""
        # Mock the models endpoint for owner/name lookup
        respx_mock.post("/models/test-owner/test-model/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction())
        )

        model = Model(owner="test-owner", name="test-model")
        output = await self.client.run(model, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_version_object(self, respx_mock: MockRouter) -> None:
        """Test async run with Version object reference."""
        # Version ID is used directly
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        version = _version_with_schema("test-version-id")
        output = await self.client.run(version, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_model_version_identifier(self, respx_mock: MockRouter) -> None:
        """Test async run with ModelVersionIdentifier dict reference."""
        # Case where version ID is provided
        respx_mock.post("/predictions").mock(return_value=httpx.Response(201, json=create_mock_prediction()))

        identifier = ModelVersionIdentifier(owner="test-owner", name="test-model", version="test-version-id")
        output = await self.client.run(identifier, input={"prompt": "test prompt"})

        assert output == "test output"

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_with_file_output_iterator(self, respx_mock: MockRouter) -> None:
        """Test async run with file output iterator."""
        # Mock URLs for file outputs
        file_urls = [
            "https://replicate.delivery/output1.png",
            "https://replicate.delivery/output2.png",
            "https://replicate.delivery/output3.png",
        ]

        # Initial response with processing status and no output
        respx_mock.post("/predictions").mock(
            return_value=httpx.Response(201, json=create_mock_prediction(status="processing", output=None))
        )

        # First poll returns still processing
        respx_mock.get("/predictions/test_prediction_id").mock(
            return_value=httpx.Response(200, json=create_mock_prediction(status="processing", output=None))
        )

        # Second poll returns success with file URLs
        respx_mock.get("/predictions/test_prediction_id").mock(
            return_value=httpx.Response(200, json=create_mock_prediction(output=file_urls))
        )

        output: list[AsyncFileOutput] = await self.client.run(
            self.model_ref, use_file_output=True, wait=False, input={"prompt": "generate file iterator"}
        )

        assert isinstance(output, list)
        assert len(output) == 3
        assert all(isinstance(item, AsyncFileOutput) for item in output)
        assert [item.url for item in output] == file_urls

    @pytest.mark.respx(base_url=base_url)
    async def test_async_run_concurrently(self, respx_mock: MockRouter) -> None:
        """Test running multiple models concurrently with asyncio."""
        import asyncio

        # Mock three different prediction responses
        mock_outputs = ["output1", "output2", "output3"]
        prompts = ["prompt1", "prompt2", "prompt3"]

        # Set up mocks for each request (using side_effect to allow multiple matches)
        # Note: This will match any POST to /predictions but return different responses
        route = respx_mock.post("/predictions")
        route.side_effect = [httpx.Response(201, json=create_mock_prediction(output=output)) for output in mock_outputs]

        # Run three predictions concurrently
        tasks = [self.client.run("owner/name:version", input={"prompt": prompt}) for prompt in prompts]

        results = await asyncio.gather(*tasks)

        # Verify each result matches expected output
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result == mock_outputs[i]
