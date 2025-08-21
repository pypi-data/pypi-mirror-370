from typing import Callable
from typing import Optional

import h2o_authn

from eval_studio_client import api
from eval_studio_client import dashboards
from eval_studio_client import documents
from eval_studio_client import evaluators
from eval_studio_client import leaderboards
from eval_studio_client import models
from eval_studio_client import perturbators
from eval_studio_client import test_labs
from eval_studio_client import tests


class Client:
    """Main Eval Studio client class."""

    def __init__(
        self,
        host: str,
        token_provider: Optional[h2o_authn.TokenProvider] = None,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initialize the client connection to Eval Studio host.

        Args:
            host: The Eval Studio host URL.
            token_provider: Optional TokenProvider used for authentication. If not
                provided, the client will not set any authentication headers.
            verify: Whether to verify SSL certificates. Defaults to True.
            ssl_ca_cert: Path to a file of concatenated CA certificates
                in PEM format. If not provided, the default system CA certificates will be used.
        """
        _host = host.rstrip("/")
        _api_config = api.Configuration(host=_host, ssl_ca_cert=ssl_ca_cert)
        _api_config.verify_ssl = verify_ssl

        self._api_client = api.ApiClient(configuration=_api_config)
        if token_provider is not None:
            self._api_client = _TokenApiClient(_api_config, token_provider.token)

        self._dashboards = dashboards._Dashboards(self._api_client)
        self._leaderboards = leaderboards._Leaderboards(self._api_client)
        self._documents = documents._Documents(self._api_client)
        self._evaluators = evaluators._Evaluators(self._api_client)
        self._perturbators = perturbators._Perturbators(self._api_client)
        self._models = models._Models(self._api_client)
        self._tests = tests._Tests(self._api_client)
        self._test_labs = test_labs._TestLabs(self._api_client)

    @property
    def dashboards(self) -> dashboards._Dashboards:
        """API for managing the collection of dashboards."""
        return self._dashboards

    @property
    def documents(self) -> documents._Documents:
        """API for managing the collection of documents."""
        return self._documents

    @property
    def evaluators(self) -> evaluators._Evaluators:
        """API for getting information about evaluation techniques in the Eval Studio."""
        return self._evaluators

    @property
    def leaderboards(self) -> leaderboards._Leaderboards:
        """API for managing the collection of leaderboards."""
        return self._leaderboards

    @property
    def perturbators(self) -> perturbators._Perturbators:
        """API for getting information about perturbation techniques in the Eval Studio."""
        return self._perturbators

    @property
    def models(self) -> models._Models:
        """API for managing models and connections to RAG/LLM system."""
        return self._models

    @property
    def tests(self) -> tests._Tests:
        """API for managing the collection of tests."""
        return self._tests

    @property
    def test_labs(self) -> test_labs._TestLabs:
        """API for building and evaluating test labs."""
        return self._test_labs


class _TokenApiClient(api.ApiClient):
    """Custom API client class to handle bearer token authentication."""

    def __init__(
        self, configuration: api.Configuration, token_provider: Callable[[], str]
    ):
        self._token_provider = token_provider
        super().__init__(configuration=configuration)

    def update_params_for_auth(
        self,
        headers,
        queries,
        auth_settings,
        resource_path,
        method,
        body,
        request_auth=None,
    ):
        headers["Authorization"] = f"Bearer {self._token_provider()}"
