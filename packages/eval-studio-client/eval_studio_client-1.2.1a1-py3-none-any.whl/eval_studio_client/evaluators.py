import dataclasses
from typing import List

from eval_studio_client import api
from eval_studio_client.api import models


@dataclasses.dataclass
class Evaluator:
    """Represents an evaluation method in Eval Studio.

    Attributes:
        key (str): Generated ID of the evaluator.
        name (str): Display name of the evaluator.
        description (str): Description of the evaluator.
        keywords (List[str]): Keywords associated with the evaluator.
            These include tags specifying whether evaluators can be used for
            RAG evaluation, LLM evaluation, or both.
        enabled (bool): Whether this evaluator is enabled and can be used for evaluation.
    """

    key: str
    name: str
    description: str
    keywords: List[str]
    enabled: bool

    @staticmethod
    def _from_api_evaluator(api_evaluator: models.V1Evaluator) -> "Evaluator":
        """Converts an API Evaluator to a client Evaluator."""
        return Evaluator(
            key=api_evaluator.name or "",
            name=api_evaluator.display_name or "",
            description=(
                api_evaluator.description or api_evaluator.brief_description or ""
            ),
            keywords=api_evaluator.tags or [],
            enabled=api_evaluator.enabled or False,
        )


class _Evaluators:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.EvaluatorServiceApi(client)

    def get(self, key: str) -> Evaluator:
        """Retrieves an evaluator by key.

        Args:
            key (str): ID of the evaluator.
        """
        res = self._api.evaluator_service_get_evaluator(key)
        if res and res.evaluator:
            return Evaluator._from_api_evaluator(res.evaluator)

        raise KeyError("Evaluator not found")

    def list(self) -> List[Evaluator]:
        """Lists all available evaluators in Eval Studio."""
        res = self._api.evaluator_service_list_evaluators()
        if res and res.evaluators:
            return [Evaluator._from_api_evaluator(e) for e in res.evaluators]

        return []
