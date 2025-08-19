"""Unit tests for LFX CLI FastAPI serve app."""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from lfx.cli.serve_app import (
    FlowMeta,
    create_multi_serve_app,
    verify_api_key,
)


class TestSecurityFunctions:
    """Test security-related functions."""

    def test_verify_api_key_with_query_param(self):
        """Test API key verification with query parameter."""
        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-key-123"}):
            result = verify_api_key("test-key-123", None)
            assert result == "test-key-123"

    def test_verify_api_key_with_header_param(self):
        """Test API key verification with header parameter."""
        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-key-123"}):
            result = verify_api_key(None, "test-key-123")
            assert result == "test-key-123"

    def test_verify_api_key_header_takes_precedence(self):
        """Test that query parameter is used when both are provided."""
        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-key-123"}):
            result = verify_api_key("test-key-123", "wrong-key")
            assert result == "test-key-123"

    def test_verify_api_key_missing(self):
        """Test error when no API key is provided."""
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(None, None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "API key required"

    def test_verify_api_key_invalid(self):
        """Test error when API key is invalid."""
        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "correct-key"}):
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key("wrong-key", None)
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid API key"

    def test_verify_api_key_env_not_set(self):
        """Test error when environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key("any-key", None)
            assert exc_info.value.status_code == 500
            assert "LANGFLOW_API_KEY environment variable is not set" in exc_info.value.detail


class TestCreateServeApp:
    """Test FastAPI app creation."""

    @pytest.fixture
    def mock_graph(self):
        """Create a mock graph."""
        graph = MagicMock()
        graph.flow_id = "test-flow-id"

        # Mock nodes as a dictionary for graph analysis
        mock_node = MagicMock()
        mock_node.data = {
            "type": "TestComponent",
            "display_name": "Test Component",
            "description": "A test component",
            "template": {},
        }
        graph.nodes = {"node1": mock_node}

        # Mock edges as a list
        mock_edge = MagicMock()
        mock_edge.source = "node1"
        mock_edge.target = "node2"
        graph.edges = [mock_edge]

        graph.vertices = []
        graph.prepare = Mock()
        return graph

    @pytest.fixture
    def mock_meta(self):
        """Create mock flow metadata."""
        return FlowMeta(
            id="test-flow-id",
            relative_path="test.json",
            title="Test Flow",
            description="A test flow",
        )

    def test_create_multi_serve_app_single_flow(self, mock_graph, mock_meta):
        """Test creating app with single flow."""
        graphs = {"test-flow-id": mock_graph}
        metas = {"test-flow-id": mock_meta}
        verbose_print = Mock()

        app = create_multi_serve_app(
            root_dir=Path("/test"),
            graphs=graphs,
            metas=metas,
            verbose_print=verbose_print,
        )

        assert app.title == "LFX Multi-Flow Server (1)"
        assert "Use `/flows` to list available IDs" in app.description

        # Check routes
        routes = [route.path for route in app.routes]
        assert "/health" in routes
        assert "/flows" in routes  # Multi-flow always has this
        assert "/flows/test-flow-id/run" in routes  # Flow-specific endpoint

    def test_create_multi_serve_app_multiple_flows(self, mock_graph, mock_meta):
        """Test creating app with multiple flows."""
        graph2 = MagicMock()
        graph2.flow_id = "flow-2"
        meta2 = FlowMeta(
            id="flow-2",
            relative_path="flow2.json",
            title="Flow 2",
            description="Second flow",
        )

        graphs = {"test-flow-id": mock_graph, "flow-2": graph2}
        metas = {"test-flow-id": mock_meta, "flow-2": meta2}
        verbose_print = Mock()

        app = create_multi_serve_app(
            root_dir=Path("/test"),
            graphs=graphs,
            metas=metas,
            verbose_print=verbose_print,
        )

        assert app.title == "LFX Multi-Flow Server (2)"
        assert "Use `/flows` to list available IDs" in app.description

        # Check routes
        routes = [route.path for route in app.routes]
        assert "/health" in routes
        assert "/flows" in routes
        assert "/flows/test-flow-id/run" in routes
        assert "/flows/test-flow-id/info" in routes
        assert "/flows/flow-2/run" in routes
        assert "/flows/flow-2/info" in routes

    def test_create_multi_serve_app_mismatched_keys(self, mock_graph, mock_meta):
        """Test error when graphs and metas have different keys."""
        graphs = {"test-flow-id": mock_graph}
        metas = {"different-id": mock_meta}
        verbose_print = Mock()

        with pytest.raises(ValueError, match="graphs and metas must contain the same keys"):
            create_multi_serve_app(
                root_dir=Path("/test"),
                graphs=graphs,
                metas=metas,
                verbose_print=verbose_print,
            )


class TestServeAppEndpoints:
    """Test the FastAPI endpoints."""

    @pytest.fixture
    def mock_graph(self):
        """Create a mock graph with async run capability."""
        graph = AsyncMock()
        graph.flow_id = "test-flow-id"

        # Mock nodes as a dictionary for graph analysis
        mock_node = MagicMock()
        mock_node.data = {
            "type": "TestComponent",
            "display_name": "Test Component",
            "description": "A test component",
            "template": {},
        }
        graph.nodes = {"node1": mock_node}

        # Mock edges as a list
        mock_edge = MagicMock()
        mock_edge.source = "node1"
        mock_edge.target = "node2"
        graph.edges = [mock_edge]

        graph.vertices = []
        graph.prepare = Mock()

        # Mock successful execution
        mock_result = MagicMock(results={"text": "Hello from flow"})

        async def mock_async_start(inputs):  # noqa: ARG001
            yield mock_result

        graph.async_start = mock_async_start

        return graph

    @pytest.fixture
    def app_client(self, mock_graph):
        """Create test client with single flow app."""
        meta = FlowMeta(
            id="test-flow-id",
            relative_path="test.json",
            title="Test Flow",
            description="A test flow",
        )

        graphs = {"test-flow-id": mock_graph}
        metas = {"test-flow-id": meta}
        verbose_print = Mock()

        app = create_multi_serve_app(
            root_dir=Path("/test"),
            graphs=graphs,
            metas=metas,
            verbose_print=verbose_print,
        )

        # Set up test API key
        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            return TestClient(app)

    @pytest.fixture
    def multi_flow_client(self, mock_graph):
        """Create test client with multiple flows."""
        graph2 = AsyncMock()
        graph2.flow_id = "flow-2"

        # Mock nodes as a dictionary for graph analysis
        mock_node2 = MagicMock()
        mock_node2.data = {
            "type": "TestComponent2",
            "display_name": "Test Component 2",
            "description": "A second test component",
            "template": {},
        }
        graph2.nodes = {"node2": mock_node2}

        # Mock edges as a list
        mock_edge2 = MagicMock()
        mock_edge2.source = "node2"
        mock_edge2.target = "node3"
        graph2.edges = [mock_edge2]

        async def mock_async_start2(inputs):  # noqa: ARG001
            yield MagicMock(outputs=[])

        graph2.async_start = mock_async_start2

        meta1 = FlowMeta(
            id="test-flow-id",
            relative_path="test.json",
            title="Test Flow",
            description="First flow",
        )
        meta2 = FlowMeta(
            id="flow-2",
            relative_path="flow2.json",
            title="Flow 2",
            description="Second flow",
        )

        graphs = {"test-flow-id": mock_graph, "flow-2": graph2}
        metas = {"test-flow-id": meta1, "flow-2": meta2}
        verbose_print = Mock()

        app = create_multi_serve_app(
            root_dir=Path("/test"),
            graphs=graphs,
            metas=metas,
            verbose_print=verbose_print,
        )

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            return TestClient(app)

    def test_health_endpoint(self, app_client):
        """Test health check endpoint."""
        response = app_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["flow_count"] == 1

    def test_run_endpoint_success(self, app_client):
        """Test successful flow execution."""
        request_data = {"input_value": "Test input"}
        headers = {"x-api-key": "test-api-key"}

        with (
            patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}),
            patch("lfx.cli.common.extract_structured_result") as mock_extract,
        ):
            mock_extract.return_value = {
                "result": "Hello from flow",
                "success": True,
                "type": "message",
                "component": "TestComponent",
            }
            response = app_client.post("/flows/test-flow-id/run", json=request_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Hello from flow"
        assert data["success"] is True
        assert data["type"] == "message"

    def test_run_endpoint_no_auth(self, app_client):
        """Test flow execution without authentication."""
        request_data = {"input_value": "Test input"}

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            response = app_client.post("/flows/test-flow-id/run", json=request_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "API key required"

    def test_run_endpoint_wrong_auth(self, app_client):
        """Test flow execution with wrong API key."""
        request_data = {"input_value": "Test input"}
        headers = {"x-api-key": "wrong-key"}

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            response = app_client.post("/flows/test-flow-id/run", json=request_data, headers=headers)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"

    def test_run_endpoint_query_auth(self, app_client):
        """Test flow execution with query parameter authentication."""
        request_data = {"input_value": "Test input"}

        with (
            patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}),
            patch("lfx.cli.common.extract_structured_result") as mock_extract,
        ):
            mock_extract.return_value = {
                "result": "Hello from flow",
                "success": True,
                "type": "message",
                "component": "TestComponent",
            }
            response = app_client.post("/flows/test-flow-id/run?x-api-key=test-api-key", json=request_data)

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_run_endpoint_execution_error(self, app_client, mock_graph):
        """Test flow execution with error."""

        # Make graph raise an error
        async def mock_async_start_error(inputs):  # noqa: ARG001
            msg = "Flow execution failed"
            raise RuntimeError(msg)
            yield  # Makes it an async generator

        mock_graph.async_start = mock_async_start_error

        request_data = {"input_value": "Test input"}
        headers = {"x-api-key": "test-api-key"}

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            response = app_client.post("/flows/test-flow-id/run", json=request_data, headers=headers)

        assert response.status_code == 200  # Returns 200 with error in response body
        data = response.json()
        assert data["success"] is False
        # serve_app error handling returns "Flow execution failed: {error}"
        assert data["result"] == "Flow execution failed: Flow execution failed"
        assert data["type"] == "error"
        # The error message should be in the logs
        assert "ERROR: Flow execution failed" in data["logs"]

    def test_run_endpoint_no_results(self, app_client, mock_graph):
        """Test flow execution with no results."""

        # Make graph return empty results
        async def mock_async_start_empty(inputs):  # noqa: ARG001
            return
            yield  # Makes it an async generator

        mock_graph.async_start = mock_async_start_empty

        request_data = {"input_value": "Test input"}
        headers = {"x-api-key": "test-api-key"}

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            response = app_client.post("/flows/test-flow-id/run", json=request_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "No response generated"
        assert data["success"] is False
        assert data["type"] == "error"

    def test_list_flows_endpoint(self, multi_flow_client):
        """Test listing flows in multi-flow mode."""
        response = multi_flow_client.get("/flows")

        assert response.status_code == 200
        flows = response.json()
        assert len(flows) == 2
        assert any(f["id"] == "test-flow-id" for f in flows)
        assert any(f["id"] == "flow-2" for f in flows)

    def test_flow_info_endpoint(self, multi_flow_client):
        """Test getting flow info in multi-flow mode."""
        headers = {"x-api-key": "test-api-key"}

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            response = multi_flow_client.get("/flows/test-flow-id/info", headers=headers)

        assert response.status_code == 200
        info = response.json()
        assert info["id"] == "test-flow-id"
        assert info["title"] == "Test Flow"
        assert info["description"] == "First flow"

    def test_flow_run_endpoint_multi_flow(self, multi_flow_client):
        """Test running specific flow in multi-flow mode."""
        request_data = {"input_value": "Test input"}
        headers = {"x-api-key": "test-api-key"}

        with (
            patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}),
            patch("lfx.cli.common.extract_structured_result") as mock_extract,
        ):
            mock_extract.return_value = {
                "result": "Hello from flow",
                "success": True,
                "type": "message",
                "component": "TestComponent",
            }
            response = multi_flow_client.post("/flows/test-flow-id/run", json=request_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Hello from flow"
        assert data["success"] is True

    def test_invalid_request_body(self, app_client):
        """Test with invalid request body."""
        headers = {"x-api-key": "test-api-key"}

        with patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}):
            response = app_client.post("/flows/test-flow-id/run", json={}, headers=headers)

        assert response.status_code == 422  # Validation error

    def test_flow_execution_with_message_output(self, app_client, mock_graph):
        """Test flow execution with message-type output."""
        # Mock output with message
        mock_message = MagicMock()
        mock_message.text = "Message output"

        mock_out = MagicMock()
        mock_out.message = mock_message
        del mock_out.results  # No results attribute

        # Create mock result with message
        mock_result = MagicMock()
        mock_result.message = mock_message
        # Ensure results attribute doesn't exist
        delattr(mock_result, "results")

        async def mock_async_start_message(inputs):  # noqa: ARG001
            yield mock_result

        mock_graph.async_start = mock_async_start_message

        request_data = {"input_value": "Test input"}
        headers = {"x-api-key": "test-api-key"}

        with (
            patch.dict(os.environ, {"LANGFLOW_API_KEY": "test-api-key"}),
            patch("lfx.cli.common.extract_structured_result") as mock_extract,
        ):
            mock_extract.return_value = {
                "result": "Message output",
                "success": True,
                "type": "message",
                "component": "TestComponent",
            }
            response = app_client.post("/flows/test-flow-id/run", json=request_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Message output"
        assert data["success"] is True
