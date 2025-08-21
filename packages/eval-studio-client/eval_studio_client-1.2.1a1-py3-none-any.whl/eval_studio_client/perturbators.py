import dataclasses
import enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from eval_studio_client import api
from eval_studio_client.api import models


class PerturbatorIntensity(enum.Enum):
    """Intensity of the perturbator during perturbation."""

    low = "low"
    medium = "medium"
    high = "high"

    def to_api_proto(self) -> models.V1PerturbatorIntensity:
        """Converts the client PerturbatorIntensity to an API PerturbatorIntensity."""
        proto_values = {
            PerturbatorIntensity.low: models.V1PerturbatorIntensity.PERTURBATOR_INTENSITY_LOW,
            PerturbatorIntensity.medium: models.V1PerturbatorIntensity.PERTURBATOR_INTENSITY_MEDIUM,
            PerturbatorIntensity.high: models.V1PerturbatorIntensity.PERTURBATOR_INTENSITY_HIGH,
        }

        return proto_values[self]


@dataclasses.dataclass
class Perturbator:
    """Represents an perturbation method in Eval Studio.

    Attributes:
        key (str): Generated ID of the perturbator.
        name (str): Display name of the perturbator.
        description (str): Description of the perturbator.
        keywords (List[str]): Keywords associated with the perturbator.
    """

    _intensity: PerturbatorIntensity

    key: str
    name: str
    description: str
    keywords: List[str]

    params: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.intensity = self.intensity or PerturbatorIntensity.medium

    @staticmethod
    def _from_api_perturbator(api_perturbator: models.V1Perturbator) -> "Perturbator":
        """Converts an API Perturbator to a client Perturbator."""
        return Perturbator(
            key=api_perturbator.name or "",
            name=api_perturbator.display_name or "",
            description=api_perturbator.description or "",
            keywords=api_perturbator.tags or [],
            _intensity=PerturbatorIntensity.medium,
        )

    @property
    def intensity(self) -> PerturbatorIntensity:
        return self._intensity

    @intensity.setter
    def intensity(self, value: Union[PerturbatorIntensity, str]):
        if isinstance(value, str):
            value = PerturbatorIntensity(value)
        self._intensity = value


class _Perturbators:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.PerturbatorServiceApi(client)

    def get(self, key: str) -> Perturbator:
        """Retrieves a perturbator by key.

        Args:
            key (str): ID of the perturbator.
        """
        res = self._api.perturbator_service_get_perturbator(key)
        if res and res.perturbator:
            return Perturbator._from_api_perturbator(res.perturbator)

        raise KeyError("Perturbator not found")

    def list(self) -> List[Perturbator]:
        """Lists all available perturbators in Eval Studio."""
        res = self._api.perturbator_service_list_perturbators()
        if res and res.perturbators:
            return [Perturbator._from_api_perturbator(e) for e in res.perturbators]

        return []
