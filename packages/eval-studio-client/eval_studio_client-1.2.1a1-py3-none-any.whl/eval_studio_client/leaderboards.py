import dataclasses
import datetime
import json
import os
import time
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import urljoin

import urllib3

from eval_studio_client import api
from eval_studio_client import evaluators
from eval_studio_client import insights as i6s
from eval_studio_client import problems as p6s
from eval_studio_client import tests
from eval_studio_client.api import models

LeaderboardTable = Dict[str, Dict[str, float]]


@dataclasses.dataclass
class Leaderboard:
    """Represents a single leaderboard in Eval Studio."""

    key: str
    name: str
    description: str
    base_models: List[str]
    _test_names: List[str]
    _evaluator_name: str
    create_time: Optional[datetime.datetime] = None
    update_time: Optional[datetime.datetime] = None
    problems: List[p6s.Problem] = dataclasses.field(default_factory=list)
    insights: List[i6s.Insight] = dataclasses.field(default_factory=list)
    summary: Optional[str] = None
    existing_collection: Optional[str] = None
    _report: Optional[str] = None
    _leaderboard: Optional[str] = None
    _model_name: Optional[str] = None
    _status: Optional[models.V1LeaderboardStatus] = None
    _client: Optional[api.ApiClient] = None
    _operation: Optional[str] = None

    def __post_init__(self):
        self._evaluator_api = api.EvaluatorServiceApi(self._client)
        self._test_api = api.TestServiceApi(self._client)
        self._leaderboard_api = api.LeaderboardServiceApi(self._client)

    @property
    def evaluator(self) -> Optional[evaluators.Evaluator]:
        """Retrieves the evaluator used in this leaderboard."""
        if self._client and self._evaluator_name:
            res = self._evaluator_api.evaluator_service_get_evaluator(
                self._evaluator_name
            )
            if res and res.evaluator:
                return evaluators.Evaluator._from_api_evaluator(res.evaluator)

        return None

    @property
    def finished(self) -> bool:
        """Indicates whether the leaderboard has finished."""
        return self._status in [
            models.V1LeaderboardStatus.LEADERBOARD_STATUS_COMPLETED,
            models.V1LeaderboardStatus.LEADERBOARD_STATUS_FAILED,
        ]

    @property
    def successful(self) -> bool:
        """Indicates whether the leaderboard has finished successfully."""
        return self._status == models.V1LeaderboardStatus.LEADERBOARD_STATUS_COMPLETED

    @property
    def test_suite(self) -> List[tests.Test]:
        """Retrieves the test suite used in this leaderboard."""
        if self._client and self._test_names:
            res = self._test_api.test_service_batch_get_tests(self._test_names)
            if res and res.tests:
                return [tests.Test._from_api_test(t, self._client) for t in res.tests]

        return []

    def delete(self):
        """Deletes the leaderboard."""
        if self._client:
            self._leaderboard_api.leaderboard_service_delete_leaderboard(self.key)

    def download_result(self, dest: str):
        """Downloads the leaderboard result to a JSON file.

        Args:
            dest (str): The destination path for the report.
        """
        if not os.path.exists(dest):
            raise ValueError("Destination path does not exist.")

        if os.path.isdir(dest):
            dest = os.path.join(dest, "results.json")

        if self._client and self.finished:
            headers: Dict[str, str] = {}
            url = urljoin(
                self._client.configuration.host, f"/content/{self.key}/results"
            )
            self._client.update_params_for_auth(
                headers=headers,
                queries=[],
                auth_settings=[],
                resource_path=url,
                method="GET",
                body=None,
            )
            response = urllib3.request("GET", url, headers=headers)

            if response.status == 200:
                with open(dest, "wb") as f:
                    f.write(response.data)
                    return
            else:
                raise RuntimeError("Failed to retrieve leaderboard result.")

        raise ValueError("Cannot download result for unfinished leaderboard.")

    def download_report(self, dest: str):
        """Downloads the leaderboard report to a zip file.

        Args:
            dest: The destination path for the report.
        """
        if self._client and self.finished:
            headers: Dict[str, str] = {}
            url = urljoin(self._client.configuration.host, f"/content/{self.key}")
            self._client.update_params_for_auth(
                headers=headers,
                queries=[],
                auth_settings=[],
                resource_path=url,
                method="GET",
                body=None,
            )
            response = urllib3.request("GET", url, headers=headers)

            if response.status == 200:
                with open(dest, "wb") as f:
                    f.write(response.data)
                    return
            else:
                raise RuntimeError("Failed to retrieve leaderboard report.")

        raise ValueError("Cannot download report for unfinished leaderboard.")

    def get_result_json(self) -> str:
        """Retrieves the leaderboard result as a JSON string."""
        if self._client and self.finished:
            headers: Dict[str, str] = {}
            url = urljoin(
                self._client.configuration.host, f"/content/{self.key}/results"
            )
            self._client.update_params_for_auth(
                headers=headers,
                queries=[],
                auth_settings=[],
                resource_path=url,
                method="GET",
                body=None,
            )
            response = urllib3.request("GET", url, headers=headers)

            if response.status == 200:
                return str(response.data)
            else:
                raise RuntimeError("Failed to retrieve leaderboard result.")

        raise ValueError("Cannot download result for unfinished leaderboard.")

    def get_table(self) -> LeaderboardTable:
        """Retrieves the leaderboard table."""
        if self._client and self.finished:
            if not self._leaderboard:
                lb = self._leaderboard_api.leaderboard_service_get_leaderboard(self.key)
                if lb and lb.leaderboard:
                    self._leaderboard = lb.leaderboard.leaderboard_table

            if self._leaderboard:
                return json.loads(self._leaderboard)
            else:
                raise RuntimeError("Failed to retrieve leaderboard table.")

        raise ValueError("Cannot retrieve table for unfinished leaderboard.")

    def wait_to_finish(self, timeout: Optional[float] = None):
        """Waits for the leaderboard to finish.

        Args:
            timeout: The maximum time to wait in seconds.
        """
        timeout = timeout or float("inf")
        if self.finished:
            return

        if self._client:
            ctr = 0
            while ctr < timeout:
                lb = self._leaderboard_api.leaderboard_service_get_leaderboard(self.key)
                if lb and lb.leaderboard:
                    if Leaderboard._is_finished_leaderboard(lb.leaderboard):
                        self._update_result(lb.leaderboard)
                        return
                ctr += 1
                time.sleep(1)
        else:
            raise ValueError("Cannot establish connection to Eval Studio host.")

        raise TimeoutError("Waiting timeout has been reached.")

    def to_api_proto(self) -> models.V1Leaderboard:
        """Converts the client Leaderboard to an API Leaderboard."""
        return models.V1Leaderboard(
            display_name=self.name,
            description=self.description,
            llm_models=self.base_models or None,
            evaluator=self._evaluator_name,
            tests=self._test_names,
            model=self._model_name,
            h2ogpte_collection=self.existing_collection or None,
        )

    def _update_result(self, api_leaderboard: models.V1Leaderboard):
        """Refresh the leaderboard with the latest API data."""
        self.key = api_leaderboard.name or ""
        self.update_time = api_leaderboard.update_time
        self.summary = api_leaderboard.leaderboard_summary
        self._leaderboard = api_leaderboard.leaderboard_table
        self._report = api_leaderboard.leaderboard_report or ""
        self._status = api_leaderboard.status

    @staticmethod
    def _from_api_leaderboard(
        api_leaderboard: models.V1Leaderboard, client: Optional[api.ApiClient]
    ) -> "Leaderboard":
        """Converts an API Leaderboard to a client Leaderboard."""
        api_problems = api_leaderboard.leaderboard_problems or []
        api_insights = api_leaderboard.insights or []
        problems = [p6s.Problem._from_api_problem(p) for p in api_problems]
        insights = [i6s.Insight._from_api_insight(i) for i in api_insights]
        return Leaderboard(
            key=api_leaderboard.name or "",
            name=api_leaderboard.display_name or "",
            description=api_leaderboard.description or "",
            base_models=api_leaderboard.llm_models or [],
            create_time=api_leaderboard.create_time,
            update_time=api_leaderboard.update_time,
            problems=problems,
            insights=insights,
            summary=api_leaderboard.leaderboard_summary,
            existing_collection=api_leaderboard.h2ogpte_collection or None,
            _evaluator_name=api_leaderboard.evaluator or "",
            _test_names=api_leaderboard.tests or [],
            _report=api_leaderboard.leaderboard_report or "",
            _leaderboard=api_leaderboard.leaderboard_table,
            _status=api_leaderboard.status,
            _client=client,
            _operation=api_leaderboard.create_operation or None,
        )

    @staticmethod
    def _is_finished_leaderboard(leaderboard: models.V1Leaderboard) -> bool:
        return leaderboard.status in [
            models.V1LeaderboardStatus.LEADERBOARD_STATUS_COMPLETED,
            models.V1LeaderboardStatus.LEADERBOARD_STATUS_FAILED,
        ]

    @staticmethod
    def from_operation(
        operation: models.V1Operation, client: Optional[api.ApiClient]
    ) -> Optional["Leaderboard"]:
        """Retrieves the leaderboard from the operation, which created it.

        Args:
            operation: The operation that created the dashboard.
            client: The API client to use for the leaderboard retrieval.

        Returns:
            Leaderboard: The leaderboard instance created by the operation.
        """
        if not client:
            raise RuntimeError("API Client is not provided")

        if not operation.metadata:
            raise RuntimeError(
                "Operation metadata missing, it's not possible to retrieve leaderboard from operation"
            )

        leaderboard_api = api.LeaderboardServiceApi(client)
        leadeboard_id = operation.metadata.to_dict().get("leaderboard", "")
        res = leaderboard_api.leaderboard_service_get_leaderboard(str(leadeboard_id))
        if res and res.leaderboard:
            return Leaderboard._from_api_leaderboard(res.leaderboard, client)

        return None


class _Leaderboards:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.LeaderboardServiceApi(client)

    def get(self, key: str) -> Leaderboard:
        """Gets an individual leaderboard with a given key from Eval Studio.

        Args:
            key: The leaderboard resource name to retrieve.
        """
        res = self._api.leaderboard_service_get_leaderboard(key)
        if res and res.leaderboard:
            return Leaderboard._from_api_leaderboard(res.leaderboard, self._client)

        raise KeyError("Leaderboard not found.")

    def list(self) -> List[Leaderboard]:
        """Lists all user leaderboards in Eval Studio."""
        res = self._api.leaderboard_service_list_leaderboards()
        if res:
            res_leaderboards = res.leaderboards or []
            return [
                Leaderboard._from_api_leaderboard(lb, self._client)
                for lb in res_leaderboards
            ]

        return []
