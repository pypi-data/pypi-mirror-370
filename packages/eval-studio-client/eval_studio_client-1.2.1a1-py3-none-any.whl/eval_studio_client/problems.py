import dataclasses
import enum
from typing import Dict
from typing import List
from typing import Optional

from eval_studio_client.api import models


class ProblemSeverity(enum.Enum):
    """Severity of the problem detected during evaluation."""

    low = "low"
    medium = "medium"
    high = "high"
    unknown = "unknown"


@dataclasses.dataclass
class Problem:
    """Problems represents an issue detected during evaluation. It's always related
    to the specific evaluation technique that was used and also contains the
    suggested actions, which could mitigated the problem.
    """

    description: str
    severity: ProblemSeverity
    problem_type: str
    problem_attrs: Dict[str, str]
    recommended_actions: str
    resources: List[str]
    _evaluator_id: Optional[str] = None

    @staticmethod
    def _from_api_problem(api_problem: models.V1ProblemAndAction) -> "Problem":
        """Converts an API Problem to a client Problem."""
        try:
            severity = ProblemSeverity(api_problem.severity)
        except ValueError:
            severity = ProblemSeverity.unknown

        return Problem(
            description=api_problem.description or "",
            severity=severity,
            problem_type=api_problem.problem_type or "",
            problem_attrs=api_problem.problem_attrs or {},
            recommended_actions=api_problem.actions_description or "",
            resources=api_problem.resources or [],
            _evaluator_id=api_problem.explainer_id,
        )
