from datetime import timedelta
from typing import List
from typing import Union

import polling
import requests
from cachetools import cached
from cachetools import TTLCache
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import OnlineTable
from databricks.sdk.service.catalog import OnlineTableSpec
from databricks.sdk.service.catalog import OnlineTableSpecContinuousSchedulingPolicy
from databricks.sdk.service.catalog import OnlineTableSpecTriggeredSchedulingPolicy
from hip_online_store.ponyta.common.request_utils import _define_oauth_request_payload
from hip_online_store.ponyta.core.config import settings
from loguru import logger
from requests.auth import HTTPBasicAuth

_global_cache = TTLCache(maxsize=2, ttl=3000)


class _PonytaOnlineStore:
    """
    The online store client is used to manage online tables
    """

    def __init__(
        self,
        settings_config: settings,
        online_table_name: str = None,
        online_table_endpoint_name: str = None,
        oauth_client_id: str = None,
        oauth_client_secret: str = None,
    ):
        """
        Initialise ponyta online store client

        Parameters
        ----------
        settings_config: settings
            settings config
        online_table_name: str = None
            name of online table
        online_table_endpoint_name: str = None
            name of online table endpoint name
        oauth_client_id: str = None
            oauth client id
        oauth_client_secret: str = None
            oauth client secret
        """

        self.settings_config = settings_config
        self.workspace_client = WorkspaceClient(
            host=self.settings_config.DATABRICKS_CLUSTER_HOST,
            token=self.settings_config.DATABRICKS_PAT_TOKEN,
        )
        # test databricks connection
        if not self._test_connection_databricks():
            raise ValueError("Databricks creds provided are incorrect")

    def _test_connection_databricks(self) -> bool:
        """
        function to test connection to databricks

        Returns
        ----------
        bool
            if the test connection is successful or not
        """
        try:
            self.workspace_client.serving_endpoints.list()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def _check_online_table_exists(self, online_table_name: str) -> int:
        """
        function to check if name of online table exists

        Parameters
        ----------
        online_table_name: str
            name of online table name

        Returns
        ----------
        int
            success returns a non exit functon value
        """
        try:
            if self.workspace_client.online_tables.get(online_table_name):
                return 0
            return 1
        except Exception as e:
            logger.error(e)
            return 1

    def _get_online_table_status(self, online_table_name: str) -> str:
        """
        function to retrieve the online table status

        Parameters
        ----------
        online_table_name: str
            name of online table name

        Returns
        ----------
        str
            success returns a non exit functon value
        """
        _status = self.workspace_client.online_tables.get(online_table_name).status

        if "online table creation succeeded" in _status.message.lower():
            return "READY"
        return "NOT_READY"

    def _initialise_online_table(
        self,
        primary_keys: List,
        source_table_name: str,
        online_table_name: str,
        schedule_type: str = "continuous",
    ) -> Union[OnlineTable, int]:
        """
        function to initialise online table

        Parameters
        ----------
        primary_keys: List
            list of primary keys for lookup
        source_table_name: str
            name of source table
        online_table_name: str
            name of online table to be created

        Returns
        ----------
        OnlineTable
            if online table name does not exist
        int
            if online table name exist

        """

        schedule_policy = OnlineTableSpecContinuousSchedulingPolicy()

        if schedule_type != "continuous":
            schedule_policy = OnlineTableSpecTriggeredSchedulingPolicy.from_dict(
                {"triggered": "true"}
            )

        # initialise the online table spec
        online_spec = OnlineTableSpec(
            primary_key_columns=primary_keys,
            source_table_full_name=source_table_name,
            run_continuously=schedule_policy,
        )

        # check if online table exists, if not return the online table
        # if alr exists return an int, and statement that the table exists
        if not self._check_online_table_exists(online_table_name=online_table_name):
            logger.info(
                f"online table name alr exists: {online_table_name}. Pls choose another name"  # noqa: E501
            )
            return None

        return OnlineTable(
            name=online_table_name,
            spec=online_spec,
        )

    def _create_online_table(
        self,
        primary_keys: List,
        source_table_name: str,
        online_table_name: str,
        schedule_type: str = "continuous",
        timeout: int = 30,
        polling_step: int = 20,
        polling_max_tries: int = 90,
    ) -> int:
        """
        function to create online table

        Parameters
        ----------
        primary_keys: List
            list of primary keys for lookup
        source_table_name: str
            name of source table
        online_table_name: str
            name of online table to be created
        timeout: int = 30
            timeout duration of creating the online table, default 30 minutes
        polling_step: int = 20
            polling interval
        polling_max_tries: int = 90
            maximum number of tries for polling

        Returns
        ----------
        int
            success returns a non exit functon value
        """
        # check if online table exists, if not create the table
        _online_table = self._initialise_online_table(
            primary_keys=primary_keys,
            source_table_name=source_table_name,
            online_table_name=online_table_name,
            schedule_type=schedule_type,
        )

        if _online_table:
            logger.info(f"Creating online table, {online_table_name}")
            self.workspace_client.online_tables.create_and_wait(
                table=_online_table, timeout=timedelta(minutes=timeout)
            )

            # poll to check if the online table is up
            polling_response = polling.poll(
                lambda: "READY"
                in self._get_online_table_status(online_table_name=online_table_name),
                step=polling_step,
                poll_forever=False,
                max_tries=polling_max_tries,
            )

            if not polling_response:
                polling_response.raise_for_status()

            logger.info(f"finish creating online table: {online_table_name}")
            return 0

        logger.info(f"online table: {online_table_name} alr exists")
        return 1

    @cached(_global_cache)
    def _generate_oauth_token(
        self,
        online_table: str,
        client_id: str,
        client_secret: str,
    ) -> str:
        """
        function to create online table

        Parameters
        ----------
        online_table_name: str
            name of online table
        client_id: str
            oauth client id
        client_secret: str
            oauth client secret

        Returns
        ----------
        str
            oauth token string
        """

        response = requests.post(
            url=self.settings_config.DATABRICKS_TOKEN_URL,
            data=_define_oauth_request_payload(online_table_name=online_table),
            auth=HTTPBasicAuth(client_id, client_secret),
            timeout=60,
        )

        return response.json().get("access_token")
