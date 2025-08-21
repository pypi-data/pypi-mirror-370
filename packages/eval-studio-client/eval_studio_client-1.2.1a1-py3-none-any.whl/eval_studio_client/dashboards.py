import dataclasses
import datetime
import time
from typing import List
from typing import Optional
import urllib.parse

from eval_studio_client import api
from eval_studio_client import insights as i6s
from eval_studio_client import leaderboards as l10s
from eval_studio_client import problems as p6s
from eval_studio_client import utils
from eval_studio_client.api import models


@dataclasses.dataclass
class Dashboard:
    """Dashboard groups score of Model on given Tests.

    Attributes:
        key (str): Generated ID of the dashboard.
        name (str): Name of the dashboard.
        description (str): Description of the dashboard.
        url (str): URL of the dashboard host system.
        api_key (str): API key for the dashboard host system.
        is_rag (bool): Whether the dashboard is a RAG or LLM-only system.
        create_time (datetime): Timestamp of the dashboard creation.
        update_time (datetime): Timestamp of the last dashboard update.
    """

    key: str
    name: str
    description: str
    _leaderboards: List[str]
    create_time: Optional[datetime.datetime] = None
    update_time: Optional[datetime.datetime] = None
    _create_operation: Optional[str] = None
    _client: Optional[api.ApiClient] = None

    def __post_init__(self):
        if self._client:
            self._dashboard_api = api.DashboardServiceApi(self._client)
            self._leaderboard_api = api.LeaderboardServiceApi(self._client)
            self._info_api = api.InfoServiceApi(self._client)
            self._operation_api = api.OperationServiceApi(self._client)

    @property
    def leaderboards(self) -> Optional[List[l10s.Leaderboard]]:
        """Returns the leaderboards in the dashboard."""
        if self._client and self._leaderboards:
            get_lbs_resp = (
                self._leaderboard_api.leaderboard_service_batch_get_leaderboards(
                    self._leaderboards
                )
            )
            if get_lbs_resp:
                return [
                    l10s.Leaderboard._from_api_leaderboard(lb, self._client)
                    for lb in get_lbs_resp.leaderboards
                ]
        return None

    @property
    def finished(self) -> bool:
        """Indicates whether all leaderboards in the dashboard have finished."""
        if self.leaderboards:
            return all(lb.finished for lb in self.leaderboards)
        return False

    @property
    def successful(self) -> bool:
        """Indicates whether all leaderboards in the dashboard have finished successfully."""
        if self.leaderboards:
            return all(lb.successful for lb in self.leaderboards)
        return False

    @property
    def problems(self) -> List[p6s.Problem]:
        """Retrieves the problems detected in the dashboard.
        The problems are aggregated across all leaderboards in the Dashboard.
        """
        lbs = self.leaderboards or []
        problems_agg = []
        for lb in lbs:
            problems_agg.extend(lb.problems or [])
        return problems_agg

    @property
    def insights(self) -> List[i6s.Insight]:
        """Retrieves the insights provided by the evaluation.
        The insights are aggregated across all leaderboards in the Dashboard.
        """
        lbs = self.leaderboards or []
        insights_agg = []
        for lb in lbs:
            insights_agg.extend(lb.insights or [])
        return insights_agg

    def download_report(self, dest: str):
        """Downloads the dashboard report to the given destination."""

        # All leaderboards in the dashboard have the same report. Download the first successful one.
        lbs = self.leaderboards
        if lbs:
            for lb in lbs:
                try:
                    return lb.download_report(dest)
                except (ValueError, RuntimeError):
                    continue
        raise ValueError("No successful leaderboard found.")

    def delete(self, delete_leaderboards: bool = False):
        """Deletes the dashboard."""
        if self._client:
            if delete_leaderboards:
                if self.leaderboards:
                    for lb in self.leaderboards:
                        lb.delete()
            self._dashboard_api.dashboard_service_delete_dashboard(self.key)
        else:
            raise ValueError("Cannot establish connection to Eval Studio host.")

    def wait_to_finish(self, timeout: Optional[float] = None, verbose: bool = False):
        """Waits for the dashboard to finish.

        Args:
            timeout: The maximum time to wait in seconds.
            verbose (bool): If True, prints the status of the evaluation while waiting.
        """
        timeout = timeout or float("inf")
        progress_bar = utils.ProgressBar()
        if self.finished:
            return

        if not self._create_operation:
            # This means that the evaluation has no assigned operation, thus cannot poll.
            raise RuntimeError("Failed to retrieve running evaluation info.")

        if self._client:
            ctr = 0
            while ctr < timeout:
                op = self._operation_api.operation_service_get_operation(
                    self._create_operation
                )
                if not op or not op.operation:
                    raise RuntimeError(
                        "Failed to retrieve running evaluation progress."
                    )

                if verbose:
                    if not op.operation.metadata:
                        raise RuntimeError(
                            "Failed to retrieve running evaluation progress details."
                        )

                    op_meta = op.operation.metadata.to_dict()
                    progress = op_meta.get("progress", 0)
                    progress_msg = op_meta.get("progressMessage", "Running")
                    progress_bar.update(progress, progress_msg)

                if op.operation.done:
                    return

                ctr += 1
                time.sleep(1)
        else:
            raise ValueError("Cannot establish connection to Eval Studio host.")

        raise TimeoutError("Waiting timeout has been reached.")

    def show(self) -> str:
        """Prints the endpoint URL of the evaluation dashboard."""
        if self._client:
            info_res = self._info_api.info_service_get_info()
            if not info_res or not info_res.info:
                raise RuntimeError("Cannot retrieve server information.")

            host = info_res.info.base_url
            url = urllib.parse.urljoin(host, self.key)
            print(f"Open following url to access evaluation dashboard: \n\n{url}")
            return url
        else:
            raise ValueError("Cannot establish connection to Eval Studio host.")

    @staticmethod
    def _from_api_dashboard(
        api_dashboard: models.V1Dashboard, client: api.ApiClient
    ) -> "Dashboard":
        """Converts the API dashboard to the client dashboard."""
        return Dashboard(
            key=api_dashboard.name or "",
            name=api_dashboard.display_name or "",
            description=api_dashboard.description or "",
            _leaderboards=api_dashboard.leaderboards or [],
            create_time=api_dashboard.create_time,
            update_time=api_dashboard.update_time,
            _create_operation=api_dashboard.create_operation,
            _client=client,
        )

    @staticmethod
    def from_operation(
        operation: models.V1Operation, client: Optional[api.ApiClient]
    ) -> Optional["Dashboard"]:
        """Retrieves the dashboard from the operation, which created it.

        Args:
            operation: The operation that created the dashboard.
            client: The API client to use for the dashboard retrieval.

        Returns:
            Dashboard: The dashboard instance created by the operation.
        """
        if not client:
            raise RuntimeError("API Client is not provided")

        if not operation.metadata:
            raise RuntimeError(
                "Operation metadata missing, it's not possible to retrieve dashboard from operation"
            )

        dashboard_api = api.DashboardServiceApi(client)
        dashboard_id = operation.metadata.to_dict().get("dashboard", "")
        res = dashboard_api.dashboard_service_get_dashboard(str(dashboard_id))
        if res and res.dashboard:
            return Dashboard._from_api_dashboard(res.dashboard, client)

        return None


class _Dashboards:
    def __init__(self, client: api.ApiClient):
        self._client = client
        self._api = api.DashboardServiceApi(client)

    def get(self, key: str) -> Dashboard:
        """Gets a dashboard with given key from Eval Studio.

        Args:
            key: The dashboard resource name to retrieve.
        """
        res = self._api.dashboard_service_get_dashboard(key)
        if res and res.dashboard:
            return Dashboard._from_api_dashboard(res.dashboard, self._client)

        raise KeyError("Dashboard not found.")

    def list(self) -> List[Dashboard]:
        """Lists all user dashboards in Eval Studio."""
        res = self._api.dashboard_service_list_dashboards()
        if res:
            res_dashboards = res.dashboards or []
            return [
                Dashboard._from_api_dashboard(m, self._client) for m in res_dashboards
            ]

        return []
