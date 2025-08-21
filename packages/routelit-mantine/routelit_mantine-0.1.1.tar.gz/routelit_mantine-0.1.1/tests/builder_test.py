from collections.abc import Mapping
from typing import Any, Optional

import pytest
from routelit import PropertyDict, RouteLitRequest

from routelit_mantine.builder import RLBuilder


class MockRLRequest(RouteLitRequest):
    def __init__(
        self,
        headers: Mapping[str, str] = {},
        path_params: Mapping[str, Any] = {},
        referrer: Optional[str] = None,
        is_json: bool = True,
        json: Optional[dict[str, Any]] = None,
        query_params: Mapping[str, str] = {},
        query_param_list: Mapping[str, list[str]] = {},
        session_id: str = "123",
        pathname: str = "/test",
        host: str = "localhost",
        method: str = "GET",
    ):
        self.headers = headers
        self.path_params = path_params
        self.referrer = referrer
        self._is_json = is_json
        self.json = json
        self.query_params = query_params
        self.query_param_list = query_param_list
        self.session_id = session_id
        self.pathname = pathname
        self.host = host
        self._method = method

    def get_headers(self) -> dict[str, str]:
        return self.headers

    def get_path_params(self) -> Optional[Mapping[str, Any]]:
        return self.path_params

    def get_referrer(self) -> Optional[str]:
        return self.referrer

    def is_json(self) -> bool:
        return self._is_json

    def get_json(self) -> Optional[dict[str, Any]]:
        return self.json

    def get_query_param(self, key: str) -> Optional[str]:
        return self.query_params.get(key)

    def get_query_param_list(self, key: str) -> list[str]:
        return self.query_param_list.get(key, [])

    def get_session_id(self) -> str:
        return self.session_id

    def get_pathname(self) -> str:
        return self.pathname

    def get_host(self) -> str:
        return self.host

    @property
    def method(self) -> str:
        return self._method


class TestRLBuilder:
    @pytest.fixture
    def mock_request(self) -> MockRLRequest:
        return MockRLRequest(method="POST")

    @pytest.fixture
    def builder(self, mock_request: MockRLRequest) -> RLBuilder:
        return RLBuilder(request=mock_request, session_state=PropertyDict({}), fragments={})

    def test_root_initialized(self, builder: RLBuilder) -> None:
        # Root provider exists with defaults
        assert builder._root.root_element.name == "provider"
        assert builder._root.root_element.key == "provider"
        assert builder._root.root_element.props["theme"]["primaryColor"] == "orange"

    def test_appshell_and_navbar_initialized(self, builder: RLBuilder) -> None:
        # App shell and navbar exist
        assert builder._app_shell.root_element.name == "appshell"
        # Public sidebar accessor should point to navbar builder
        assert builder.sidebar.root_element.name == "navbar"

    def test_set_provider_props_updates_root(self, builder: RLBuilder) -> None:
        builder.set_provider_props(theme={"primaryColor": "green"}, defaultColorScheme="dark")
        assert builder._root.root_element.props["theme"]["primaryColor"] == "green"
        assert builder._root.root_element.props["defaultColorScheme"] == "dark"

    def test_set_app_shell_props_updates(self, builder: RLBuilder) -> None:
        builder.set_app_shell_props(
            title="Mantine RouteLit",
            logo="/static/logo.svg",
            navbar_props={"width": 200},
            withBorder=True,
        )
        app_shell_props = builder._app_shell.root_element.props
        assert app_shell_props["title"] == "Mantine RouteLit"
        assert app_shell_props["logo"] == "/static/logo.svg"
        assert app_shell_props["navbarProps"]["width"] == 200
        assert app_shell_props["withBorder"] is True

    def test_container_layout_builder(self, builder: RLBuilder) -> None:
        nested = builder.container(fluid=True, size="xl", bg="var(--mantine-color-blue-light)")
        assert nested.root_element.name == "container"
        assert nested.root_element.props["fluid"] is True
        assert nested.root_element.props["size"] == "xl"
        assert nested.root_element.props["bg"] == "var(--mantine-color-blue-light)"
