import dataclasses
import datetime
import json
from typing import List
from typing import Optional
from typing import Union

from eval_studio_client import api
from eval_studio_client import dashboards as d8s
from eval_studio_client import evaluators as e8s
from eval_studio_client import leaderboards as l10s
from eval_studio_client import tests
from eval_studio_client.api import models

# Key for Azure environment ID parameter within Model parameters.
_AZURE_ENV_ID_PARAM = "environment_id"

# Resource name of the default RAG model.
DEFAULT_RAG_MODEL_KEY = "models/defaultRAGModel"

# Resource name of the default LLM model.
DEFAULT_LLM_MODEL_KEY = "models/defaultLLMModel"


@dataclasses.dataclass
class CollectionInfo:
    """Represents the information about a collection in the H2OGPTE
    or a Knowledge Base in Amazon Bedrock.
    """

    key: str
    name: str
    description: str

    def __str__(self):
        return f"{self.name} ({self.key})"

    @staticmethod
    def _from_api_collection_info(api_col: models.V1CollectionInfo) -> "CollectionInfo":
        return CollectionInfo(
            key=api_col.id or "",
            name=api_col.display_name or "",
            description=api_col.description or "",
        )


@dataclasses.dataclass
class Model:
    """Represents Eval Studio connection to an external RAG/LLM system.

    Attributes:
        key (str): Generated ID of the model.
        name (str): Name of the model.
        description (str): Description of the model.
        url (str): URL of the model host system.
        api_key (str): API key for the model host system.
        is_rag (bool): Whether the model is a RAG or LLM-only system.
        create_time (datetime): Timestamp of the model creation.
        update_time (datetime): Timestamp of the last model update.
    """

    key: str
    name: str
    description: str
    url: str
    api_key: str
    is_rag: bool
    create_time: Optional[datetime.datetime] = None
    update_time: Optional[datetime.datetime] = None
    _client: Optional[api.ApiClient] = None

    def __post_init__(self):
        if self._client:
            self._model_api = api.ModelServiceApi(self._client)
            self._leaderboard_api = api.LeaderboardServiceApi(self._client)
            self._dashboard_api = api.DashboardServiceApi(self._client)

    @property
    def leaderboards(self) -> List[l10s.Leaderboard]:
        """List of all leaderboards created for this model."""
        result = []
        page_token = ""
        while True:
            res = self._leaderboard_api.leaderboard_service_list_leaderboards(
                filter=f'model="{self.key}"',
                view=models.V1LeaderboardView.LEADERBOARD_VIEW_BASIC_WITH_TABLE,
                page_token=page_token,
            )
            if not res or not res.leaderboards:
                break

            res_leaderboards = res.leaderboards or []
            lbs = [
                l10s.Leaderboard._from_api_leaderboard(lb, self._client)
                for lb in res_leaderboards
            ]
            result.extend(lbs)

            page_token = res.next_page_token
            if not page_token:
                break

        return result

    @property
    def base_models(self) -> List[str]:
        """List of base LLM models available to use e.g. for the evaluation."""
        res = self._model_api.model_service_list_base_models(self.key)
        if res and res.base_models:
            return [str(m) for m in res.base_models]

        raise RuntimeError("Failed to list base models")

    @property
    def collections(self) -> List[CollectionInfo]:
        """List of collections available for evaluation.

        NOTE: This is currently supported only for H2OGPTe and Amazon Bedrock RAG
        model hosts.
        """
        res = self._model_api.model_service_list_model_collections(self.key)
        if res and res.collections:
            return list(res.collections)

        raise RuntimeError("Failed to list model host collections")

    def create_leaderboard(
        self,
        name: str,
        evaluator: e8s.Evaluator,
        test_suite: List[tests.Test],
        description: Optional[str] = None,
        base_models: Optional[List[str]] = None,
        use_cache: bool = True,
        existing_collection: Optional[str] = None,
    ) -> Optional[l10s.Leaderboard]:
        """Runs a new evaluation for the model and creates a new leaderboard.

        Args:
            name: The name of the leaderboard.
            evaluator: The evaluator to use for the evaluation.
            test_suite: The list of tests used to evaluate the model.
            description (optional): The description of the leaderboard.
            base_models (optional): The base LLM models to use for the evaluation.
            use_cache (optional): Whether to use the cached answers if available.
            existing_collection (str): ID or the resource name of the existing
                collection, which will be used as a corpus for evaluation.
                NOTE: This option works only for the H2OGPTe and Amazon Bedrock model hosts ATM.
        """
        lb = l10s.Leaderboard(
            key="",
            name=name,
            description=description or "",
            base_models=base_models or [],
            existing_collection=existing_collection,
            _model_name=self.key,
            _evaluator_name=evaluator.key,
            _test_names=[t.key for t in test_suite],
            _client=self._client,
        )
        if use_cache:
            res = self._leaderboard_api.leaderboard_service_create_leaderboard(
                lb.to_api_proto()
            )
        else:
            res = self._leaderboard_api.leaderboard_service_create_leaderboard_without_cache(
                lb.to_api_proto()
            )

        if res and res.operation:
            return l10s.Leaderboard.from_operation(res.operation, self._client)

        return None

    def evaluate(
        self,
        name: str,
        evaluators: Union[e8s.Evaluator, List[e8s.Evaluator]],
        test_suites: Union[tests.Test, List[tests.Test]],
        description: Optional[str] = None,
        base_models: Optional[List[str]] = None,
        existing_collection: Optional[str] = None,
    ) -> Optional[d8s.Dashboard]:
        """Runs a new evaluation for the model and creates a new dashboard.

        Args:
            evaluators: The evaluator(s) to use for the evaluation.
            test_suites: The test(s) used to evaluate the model.
            description (optional): The description of the dashboard.
            base_models (optional): The base LLM models to use for the evaluation.
            existing_collection (str): ID or the resource name of the existing
                collection, which will be used as a corpus for evaluation.
                NOTE: This option works only for the H2OGPTe and Amazon Bedrock model hosts ATM.
        """
        _evaluators = (
            [evaluators] if isinstance(evaluators, e8s.Evaluator) else evaluators
        )
        _test_suites = (
            [test_suites] if isinstance(test_suites, tests.Test) else test_suites
        )

        create_lb_reqs: List[models.V1CreateLeaderboardRequest] = []
        for evaluator in _evaluators:
            lb = l10s.Leaderboard(
                key="",
                name=f"{name} - {evaluator.name}",
                description=description or "",
                base_models=base_models or [],
                existing_collection=existing_collection,
                _model_name=self.key,
                _evaluator_name=evaluator.key,
                _test_names=[t.key for t in _test_suites],
                _client=self._client,
            )
            create_lb_req = models.V1CreateLeaderboardRequest(
                leaderboard=lb.to_api_proto()
            )
            create_lb_reqs.append(create_lb_req)

        res = self._leaderboard_api.leaderboard_service_batch_create_leaderboards(
            models.V1BatchCreateLeaderboardsRequest(
                requests=create_lb_reqs,
                dashboard_display_name=name,
                dashboard_description=description,
            )
        )

        if res and res.operation:
            return d8s.Dashboard.from_operation(res.operation, self._client)

        return None

    def create_leaderboard_from_testlab(
        self,
        name: str,
        evaluator: e8s.Evaluator,
        test_lab: str,
        description: Optional[str] = None,
    ) -> Optional[l10s.Leaderboard]:
        """Runs an evaluation from pre-built Test Lab, which contains
        tests and pre-computed answers.

        Args:
            name: The name of the leaderboard.
            evaluator: The evaluator to use for the evaluation.
            test_lab: The test lab in JSON format to use for the evaluation.
            description (optional): The description of the leaderboard.
        """
        req = models.V1ImportLeaderboardRequest(
            testLabJson=test_lab,
            evaluator=evaluator.key,
            model=self.key,
            leaderboardDisplayName=name,
            leaderboardDescription=description or "",
            testDisplayName=f"{name}-Test",
            testDescription=description or "",
        )
        res = self._leaderboard_api.leaderboard_service_import_leaderboard(req)
        if res and res.operation:
            return l10s.Leaderboard.from_operation(res.operation, self._client)

        return None

    def delete(self):
        """Deletes the model"""
        self._model_api.model_service_delete_model(self.key)

    def list_base_models(self) -> List[str]:
        """List base LLM models available to use for the evaluation."""
        res = self._model_api.model_service_list_base_models(self.key)
        if res and res.base_models:
            return [str(m) for m in res.base_models]

        raise RuntimeError("Failed to list base models")

    @staticmethod
    def _from_api_model(api_model: models.V1Model, client: api.ApiClient) -> "Model":
        """Converts the API model to the client model."""
        return Model(
            key=api_model.name or "",
            name=api_model.display_name or "",
            description=api_model.description or "",
            url=api_model.url or "",
            api_key=api_model.api_key or "",
            is_rag=Model._is_rag_model(api_model),
            create_time=api_model.create_time,
            update_time=api_model.update_time,
            _client=client,
        )

    @staticmethod
    def _is_rag_model(api_model: models.V1Model) -> bool:
        return api_model.type in [
            models.V1ModelType.MODEL_TYPE_H2_OGPTE_RAG,
            models.V1ModelType.MODEL_TYPE_OPENAI_RAG,
        ]


class _Models:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.ModelServiceApi(client)

    def get(self, key: str) -> Model:
        """Gets a model with given key from Eval Studio.

        Args:
            key: The model resource name to retrieve.

        Returns:
            Model: The model object.

        Raises:
            KeyError: If the model is not found.
        """
        res = self._api.model_service_get_model(key)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise KeyError("Model not found.")

    def get_default_rag(self) -> Model:
        """Gets the default RAG model from Eval Studio.

        Returns:
            Model: The default RAG model object.

        Raises:
            KeyError: If no default RAG model is set.
        """
        return self.get(DEFAULT_RAG_MODEL_KEY)

    def get_default_llm(self) -> Model:
        """Gets the default LLM model from Eval Studio.

        Returns:
            Model: The default LLM model object.

        Raises:
            KeyError: If no default LLM model is set.
        """
        return self.get(DEFAULT_LLM_MODEL_KEY)

    def create_h2ogpte_model(
        self, name: str, is_rag: bool, description: str, url: str, api_key: str
    ) -> Model:
        """Creates a new H2OGPTe model in Eval Studio.

        **Note**: You have to choose between RAG or LLM-only mode for this model.

        Args:
            name: Name of the model.
            is_rag:
                Whether the model is a RAG or LLM-only system, i.e. no context retrieval.
            description: Description of the model.
            url: URL of the model host system.
            api_key: API key for the model host system.
        """
        model_type = (
            models.V1ModelType.MODEL_TYPE_H2_OGPTE_RAG
            if is_rag
            else models.V1ModelType.MODEL_TYPE_H2_OGPTE_LLM
        )
        req = models.V1Model(
            display_name=name,
            description=description,
            url=url,
            api_key=api_key,
            type=model_type,
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create H2OGPTe model")

    def create_h2ogpt_model(
        self, name: str, description: str, url: str, api_key: str
    ) -> Model:
        """Creates a new H2OGPT model in Eval Studio.

        Args:
            name: Name of the model.
            description: Description of the model.
            url: URL of the model host system.
            api_key: API key for the model host system.
        """
        req = models.V1Model(
            display_name=name,
            description=description,
            url=url,
            api_key=api_key,
            type=models.V1ModelType.MODEL_TYPE_H2_OGPT_LLM,
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create H2OGPT model")

    def create_h2o_llmops_model(
        self, name: str, description: str, url: str, api_key: str
    ) -> Model:
        """Creates a new H2O LLMOps Model.

        Args:
            name: Name of the model.
            description: Description of the model.
            url: URL of the model host system.
            api_key: API key for the model host system.
        """
        req = models.V1Model(
            display_name=name,
            description=description,
            url=url,
            api_key=api_key,
            type=models.V1ModelType.MODEL_TYPE_H2_OLLMOPS,
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create H2O LLMOps model")

    def create_openai_model(
        self,
        name: str,
        description: str,
        api_key: str,
        url: str = "",
        is_rag: bool = True,
    ) -> Model:
        """Creates a new OpenAI model in Eval Studio.

        Args:
            name: Name of the model.
            description: Description of the model.
            api_key: API key for the model host system.
            url (optional): If not specified, connects to default OpenAI endpoint.
                Otherwise can use custom OpenAI compatible API.
            is_rag (optional): If True, uses the OpenAI Assistants API for RAG.
                If False, uses plain OpenAI Chat.

        """
        if url and is_rag:
            raise ValueError(
                "OpenAI Assistants are not currently supported on custom OpenAI endpoints."
            )

        model_type = (
            models.V1ModelType.MODEL_TYPE_OPENAI_RAG
            if is_rag
            else models.V1ModelType.MODEL_TYPE_OPENAI_CHAT
        )
        req = models.V1Model(
            display_name=name,
            description=description,
            api_key=api_key,
            url=url or None,
            type=model_type,
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create OpenAI model")

    def create_azure_openai_model(
        self, name: str, description: str, url: str, api_key: str, environmentID: str
    ) -> Model:
        """Creates a new Azure-hosted OpenAI model in Eval Studio.

        Args:
            name: Name of the model.
            description: Description of the model.
            url: URL of the model host system.
            api_key: API key for the model host system.
            environmentID: Azure environment ID.
        """
        params = {_AZURE_ENV_ID_PARAM: environmentID}
        req = models.V1Model(
            display_name=name,
            description=description,
            url=url,
            api_key=api_key,
            type=models.V1ModelType.MODEL_TYPE_AZURE_OPENAI_CHAT,
            parameters=json.dumps(params),
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create Azure model")

    def create_ollama_model(
        self, name: str, description: str, url: str, api_key: str
    ) -> Model:
        """Creates a new OLLAMA model in Eval Studio.

        Args:
            name: Name of the model.
            description: Description of the model.
            url: URL of the model host system.
            api_key: API key for the model host system.
        """
        req = models.V1Model(
            display_name=name,
            description=description,
            url=url,
            api_key=api_key,
            type=models.V1ModelType.MODEL_TYPE_OLLAMA,
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create OLLAMA model")

    def create_amazon_bedrock_model(
        self,
        name: str,
        description: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_session_token: str,
        aws_region: str,
    ) -> Model:
        """Creates a new Amazon Bedrock model in Eval Studio.

        Args:
            name: Name of the model.
            description: Description of the model.
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
            aws_session_token: AWS session token.
            aws_region: AWS region.
        """
        credentials = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
        }
        req = models.V1Model(
            display_name=name,
            description=description,
            type=models.V1ModelType.MODEL_TYPE_AMAZON_BEDROCK,
            api_key=json.dumps(credentials),
            parameters=json.dumps({"region": aws_region}),
        )
        res = self._api.model_service_create_model(req)
        if res and res.model:
            return Model._from_api_model(res.model, self._client)

        raise RuntimeError("Failed to create Amazon Bedrock model")

    def delete(self, key: str):
        """Deletes a model with given key from Eval Studio.

        Args:
            key: The model resource name to delete.
        """
        self._api.model_service_delete_model(key)

    def list(self) -> List[Model]:
        """Lists all user models in Eval Studio."""
        res = self._api.model_service_list_models()
        if res:
            res_models = res.models or []
            return [Model._from_api_model(m, self._client) for m in res_models]

        return []
