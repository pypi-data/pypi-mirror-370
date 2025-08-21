import dataclasses
from typing import Dict
from typing import List
from typing import Optional

from eval_studio_client.api import models


@dataclasses.dataclass
class Insight:
    """Insight represents an insight detected during evaluation, which is always
    related to the specific evaluation technique used and it also provides
    recommended actions, which can help improve the model performance.
    """

    description: str
    insight_type: str
    insight_attrs: Dict[str, str]
    recommended_actions: str
    action_codes: List[str]
    resources: List[str]
    _evaluator_id: Optional[str] = None

    @staticmethod
    def _from_api_insight(api_insight: models.V1Insight) -> "Insight":
        """Converts an API Insight to a client Insight."""
        return Insight(
            description=api_insight.description or "",
            insight_type=api_insight.insight_type or "",
            insight_attrs=api_insight.insight_attrs or {},
            recommended_actions=api_insight.actions_description or "",
            action_codes=api_insight.actions_codes or [],
            resources=api_insight.resources or [],
            _evaluator_id=api_insight.evaluator_id,
        )
