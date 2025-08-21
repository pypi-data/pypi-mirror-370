import dataclasses
import enum
import json
from typing import List
from typing import Optional
from typing import Union
import uuid

from eval_studio_client import api
from eval_studio_client import dashboards
from eval_studio_client import evaluators as e8s
from eval_studio_client import leaderboards as l10s
from eval_studio_client.api import models as apiModels


class ModelType(enum.Enum):
    h2ogpte = "h2ogpte"  # h2oGPTe RAG
    h2ogpte_llm = "h2ogpte_llm"  # h2oGPTe-hosted LLM
    h2ogpt = "h2ogpt"  # h2oGPT-hosted LLM
    h2ollmops = "h2ollmops"  # H2O LLMOps-hosted LLM
    openai_rag = "openai_rag"  # OpenAI RAG
    openai_llm = "openai_llm"  # OpenAI-hosted LLM
    azure_openai_llm = "azure_openai_llm"  # MS Azure hosted OpenAI LLM
    amazon_bedrock = "amazon_bedrock"  # Amazon Bedrock


@dataclasses.dataclass
class TestLab:
    """Represents an Eval Studio Test Lab, which can directly be evaluated,
    without a need to contact LLM/RAG system. This object contains all the information,
    needed for the evaluation, such as prompt, actual answer and retrieved contexts,
    for all of the models.

    Attributes:
        name (str): The name of the test lab.
        description (str): The description of the test lab.
        dataset: The dataset consists of test cases, which are used for the evaluation.
        models: The models contain definitions of connections to different models
                or RAG systems
    """

    name: str
    description: str = ""
    _models: List["TestLabModel"] = dataclasses.field(default_factory=list)
    _client: Optional[api.ApiClient] = None

    __test__ = False

    def __post_init__(self):
        if self._client:
            self._leaderboard_api = api.LeaderboardServiceApi(self._client)

    @property
    def models(self) -> List["TestLabModel"]:
        return self._models

    def add_model(
        self,
        name: str,
        model_type: ModelType,
        llm_model_name: str,
        collection_id: str = "",
        collection_name: str = "",
        documents: Optional[List[str]] = None,
    ) -> "TestLabModel":
        """Registers a new model to the Test Lab.

        Args:
            name (str): Human readable name of the model.
            model_type (ModelType): The type of the model. One of `ModelType` values.
            llm_model_name (str): Identification of the LLM models used,
                e.g. "h2oai/h2ogpt-4096-llama2-13b-chat"
            collection_id (str, optional): ID of the existing collection in the RAG
                system, which produced the answers.
            collection_name (str, optional): Name of the existing collection in the RAG
                system, which produced the answers.
            documents (Optional[List[str]], optional): List of document URLs used
                in the RAG evaluation. These can later be reused.

        Returns:
            TestLabModel: New instance of TestLabModel.
        """
        key = str(uuid.uuid4())
        _m = TestLabModel(
            name=name,
            key=key,
            model_type=model_type.value,
            llm_model_name=llm_model_name,
            collection_id=collection_id,
            collection_name=collection_name,
            documents=documents or [],
        )
        self._models.append(_m)
        return _m

    def evaluate(
        self,
        evaluators: Union[e8s.Evaluator, List[e8s.Evaluator]],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[dashboards.Dashboard]:
        """Runs an evaluation for the test lab.

        Args:
            evaluators (Union[e8s.Evaluator, List[e8s.Evaluator]]): One or many evaluators
                used to evaluate the test lab.
            name (str, optional): Optional name for the evaluation.
            description (str, optional): Optional description for the evaluation.

        Returns:
           Dashboard: Evaluation dashboard instance. In case launching of evaluation
              fails, `None` is returned.
        """
        _evaluators = (
            [evaluators] if isinstance(evaluators, e8s.Evaluator) else evaluators
        )
        name = name or self.name or "Imported Dashboard"
        description = description or self.description or ""
        req = apiModels.V1BatchImportLeaderboardRequest(
            testLabJson=self.json(),
            evaluators=[e.key for e in _evaluators],
            model=None,
            dashboardDisplayName=name,
            dashboardDescription=description,
            testDisplayName=f"{name} - Test",
            testDescription=f"Test suite for {description}",
        )
        res = self._leaderboard_api.leaderboard_service_batch_import_leaderboard(req)

        if res and res.operation:
            return dashboards.Dashboard.from_operation(res.operation, self._client)

        return None

    def create_leaderboard(
        self, evaluator: e8s.Evaluator
    ) -> Optional[l10s.Leaderboard]:
        """Creates a single leaderboard for the test lab.

        Args:
            evaluator: The evaluator to use for the evaluation.

        Returns:
           Leaderboard: Single evaluation leaderboard instance.
            In case launching of evaluation fails, `None` is returned.
        """
        req = apiModels.V1ImportLeaderboardRequest(
            testLabJson=self.json(),
            evaluator=evaluator.key,
            model=None,
            leaderboardDisplayName=self.name,
            leaderboardDescription=self.description or "",
            testDisplayName=f"{self.name}-Test",
            testDescription=self.description or "",
        )
        res = self._leaderboard_api.leaderboard_service_import_leaderboard(req)
        if res and res.operation:
            return l10s.Leaderboard.from_operation(res.operation, self._client)

        return None

    def json(self) -> str:
        raw_inputs = []
        dataset = []
        for m in self.models:
            raw_inputs.extend(m.raw_inputs)
            dataset.extend(m.dataset)

        lab = {
            "name": self.name,
            "description": self.description,
            "raw_dataset": {"inputs": raw_inputs},
            "dataset": {"inputs": dataset},
            "models": [m.to_dict() for m in self.models],
            "llm_model_names": self._llm_model_names(),
        }

        return json.dumps(lab, indent=4, sort_keys=True)

    def _llm_model_names(self) -> List[str]:
        return [m.llm_model_name for m in self.models]


@dataclasses.dataclass
class TestLabModel:
    """Represents a model, which is used in the testing. This object contains
    the model key, the model name and the model type.
    """

    # Human readable name of the model
    name: str
    # The unique identification of the model to link with inputs
    key: str
    model_type: str
    llm_model_name: str
    collection_id: str = ""
    collection_name: str = ""
    documents: List[str] = dataclasses.field(default_factory=list)
    connection: str = ""
    _inputs: List["_TestLabInput"] = dataclasses.field(default_factory=list)

    __test__ = False

    def __post_init__(self):
        self.validate_model_type()

    @property
    def raw_inputs(self) -> List[dict]:
        return [i.to_raw_input_dict() for i in self._inputs]

    @property
    def dataset(self) -> List[dict]:
        return [i.to_dataset_dict() for i in self._inputs]

    def add_input(
        self,
        prompt: str,
        actual_output: str,
        corpus: Optional[List[str]] = None,
        context: Optional[List[str]] = None,
        categories: Union[str, List[str]] = "",
        expected_output: str = "",
        output_constraints: Optional[List[str]] = None,
        actual_duration: float = 0.0,
        cost: float = 0.0,
        output_condition: str = "",
    ) -> "_TestLabInput":
        """Add an evaluation input, which contains all the info relevant for the
        evaluation, to avoid calling the RAG/LLM itself.

        Args:
            prompt (str): Prompt or input to the RAG/LLM.
            actual_output (str): Actual output from the RAG/LLM.
            corpus (Optional[List[str]], optional): List of document URLs used in the RAG.
            context (Optional[List[str]], optional): List of retrieved contexts.
            categories (Union[str, List[str]]): List of categories/tags for the input.
            expected_output (str): Expected output from the RAG/LLM.
            output_constraints (List[str]): List of constraints for the output,
                such as expected tokens in the answer.
            actual_duration (float, optional): Duration of the inference of the answer.
            cost (float, optional): Cost estimate of the inference.
            output_condition (str, optional): Output condition is a logical expression
                used to set the expectation on the output. The expression is in
                Google's filtering language format defined in
                https://google.aip.dev/160#logical-operators .

        Returns:
            TestLabInput instance.
        """
        i = _TestLabInput(
            prompt=prompt,
            corpus=corpus,
            context=context,
            categories=categories,
            expected_output=expected_output,
            output_constraints=output_constraints,
            output_condition=output_condition,
            actual_output=actual_output,
            actual_duration=actual_duration,
            cost=cost,
            model_key=self.key,
        )
        self._inputs.append(i)
        return i

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "key": self.key,
            "model_type": self.model_type,
            "collection_id": self.collection_id,
            "collection_name": self.collection_name,
            "llm_model_name": self.llm_model_name,
            "documents": self.documents or [],
            "connection": self.connection,
        }

    def validate_model_type(self):
        valid_values = [e.value for e in set(ModelType)]
        if self.model_type not in valid_values:
            raise ValueError(
                f"Invalid model type: {self.model_type}. Valid values: {valid_values}"
            )


@dataclasses.dataclass
class _TestLabInput:
    """Represents a single input for the testing, which is basically a `TestCase`,
    with more information.
    """

    # The input prompt
    prompt: str
    corpus: Optional[List[str]] = None
    context: Optional[List[str]] = None
    categories: Union[str, List[str]] = ""
    expected_output: str = ""
    output_constraints: Optional[List[str]] = None
    output_condition: str = ""
    actual_output: str = ""
    actual_duration: float = 0.0
    cost: float = 0.0
    model_key: str = ""

    def to_raw_input_dict(self) -> dict:
        return {
            "input": self.prompt,
            "corpus": self.corpus or [],
            "context": [],
            "categories": self.categories,
            "expected_output": self.expected_output,
            "output_constraints": self.output_constraints or [],
            "output_condition": self.output_condition or "",
            "actual_output": "",
            "actual_duration": 0.0,
            "cost": 0.0,
            "model_key": self.model_key,
        }

    def to_dataset_dict(self) -> dict:
        return {
            "input": self.prompt,
            "corpus": self.corpus or [],
            "context": self.context or [],
            "categories": self.categories,
            "expected_output": self.expected_output,
            "output_constraints": self.output_constraints or [],
            "output_condition": self.output_condition or "",
            "actual_output": self.actual_output,
            "actual_duration": self.actual_duration,
            "cost": self.cost,
            "model_key": self.model_key,
        }


class _TestLabs:
    def __init__(self, client: api.ApiClient):
        self._client = client

    def create(self, name: str, description: str = "") -> TestLab:
        """Create a new Test Lab instance

        Args:
            name: Name of the test lab
            description: Description of the test lab
        """
        return TestLab(name, description, _client=self._client)
