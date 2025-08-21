import random
from typing import Dict

import requests
from databricks.sdk import WorkspaceClient
from hip_online_store.ponyta.common.request_utils import _define_request_headers
from hip_online_store.ponyta.core.config import settings
from loguru import logger


class _PonytaRegistry:
    """
    The registry client is a wrapper for the databricks python libraries.
    Here, we mainly deal with the creation of the online table, read
    of online tables, and retrieving similar tradies

    TODO: add similarity lookup of tradies
    """

    def __init__(self, settings_config: settings):
        """
        Initialise ponyta registry client

        Parameters
        ----------
        settings_config: settings
            settings config
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

    def _retrieve_online_features_tradie_empty(
        self,
        endpoint_url: str,
        columns_selection: Dict,
        primary_key_values_dict: Dict,
        oauth_token: str,
        limit_return: int = 1,
        timeout_request: int = 60,
    ) -> Dict:
        """
        function to retrieve tradie generic features

        Parameters
        ----------
        endpoint_url: str
            name of tradie online table url
        columns_selection: Dict
            feature columns to select
        primary_key_values_dict: Dict
            dictionary that stores the primary keys
        oauth_token: str
            oauth token
        limit_return: int = 1
            number of rows returned; default at 1
        timeout_request: int = 60
            request timeout is set to seconds

        Returns
        ----------
        Dict
            dictionary of retrieved features
        """
        _primary_key_values_dict = {
            "accountId": primary_key_values_dict["accountId"],
            "tenure_tradie": "gt.0",
        }

        _response = requests.get(
            url=endpoint_url,
            headers=_define_request_headers(
                oauth_token=oauth_token,
                accept_profile=self.settings_config.DATABRICKS_ACCEPT_PROFILE,
            ),
            params={
                **columns_selection,
                **_primary_key_values_dict,
                "limit": limit_return,
            },
            timeout=timeout_request,
        ).json()

        # get categoryId and tradieId regardless
        output_dict = {
            key: int(value[value.find("(") + 1 : value.find(")")])
            for key, value in primary_key_values_dict.items()
        }

        # if there is no values, tradie is new, and we impute active tradies
        # need to rethink about this for high VC tradies
        if not _response:
            return {
                **output_dict,
                **{
                    "tenure_tradie": 30,
                    "value_cap": 149,
                    "credit_available": 201,
                    "total_claim_attempts": 1,
                },
            }

        # if there is a response, we check tenure_tradie <= 30 for impute active
        if _response[0]["tenure_tradie"] <= 30:
            _response[0]["total_claim_attempts"] = 1
            return {**_response[0], **{"job_categoryId": output_dict["job_categoryId"]}}

        # else return what is presented for the tradie
        return {
            **_response[0],
            **{
                "job_categoryId": output_dict["job_categoryId"],
                "total_claim_attempts": _response[0]["total_claim_attempts"]
                if _response[0]["total_claim_attempts"] is not None
                else 0,
                "total_claim_attempts_category": 0,
                "total_claim_attempts_parent": 0,
                "category_frequent": 0,
                "parent_frequent": 0,
            },
        }

    def _retrieve_online_features_table_data_exact_match(
        self,
        endpoint_url: str,
        columns_selection: Dict,
        primary_key_values_dict: Dict,
        oauth_token: str,
        which_perspective: str,
        limit_return: int = 1,
        timeout_request: int = 60,
        columns_selection_empty: Dict = None,
    ) -> Dict:
        """
        function to retrieve tradie features for exact match

        Parameters
        ----------
        endpoint_url: str
            name of tradie online table url
        columns_selection: Dict
            feature columns to select
        primary_key_values_dict: Dict
            dictionary that stores the primary keys
        oauth_token: str
            oauth token
        limit_return: int = 1
            number of rows returned; default at 1
        timeout_request: int = 60
            request timeout is set to seconds
        columns_selection_empty: Dict = None
            feature columns to select if response is empty

        Returns
        ----------
        Dict
            dictionary of retrieved features
        """
        _response = requests.get(
            url=endpoint_url,
            headers=_define_request_headers(
                oauth_token=oauth_token,
                accept_profile=self.settings_config.DATABRICKS_ACCEPT_PROFILE,
            ),
            params={
                **columns_selection,
                **primary_key_values_dict,
                "limit": limit_return,
            },
            timeout=timeout_request,
        )
        # handle for empty returns for jobs
        if (not _response.json()) & (which_perspective == "job"):
            return {"first_round_price": 35}

        # handle for empty returns for tradie
        if (not _response.json()) & (which_perspective == "tradie"):
            return self._retrieve_online_features_tradie_empty(
                endpoint_url=endpoint_url,
                columns_selection=columns_selection_empty,
                primary_key_values_dict=primary_key_values_dict,
                oauth_token=oauth_token,
                limit_return=limit_return,
                timeout_request=timeout_request,
            )

        return _response.json()[0]

    def _retrieve_online_features_table_data_active_tradies(
        self,
        endpoint_url: str,
        filter_selection: Dict,
        query_values_dict: Dict,
        oauth_token: str,
        limit_return: int = 100,
        timeout_request: int = 60,
    ) -> Dict:
        """
        function to retrieve similar tradies with more activity

        Parameters
        ----------
        endpoint_url: str
            name of tradie online table url
        filter_selection: str
            filter selection column
        query_values_dict: Dict
            dictionary that stores the primary keys
        oauth_token: str
            oauth token
        limit_return: int = 100
            number of rows returned; default at 100
        timeout_request: int = 60
            request timeout is set to seconds

        Returns
        ----------
        Dict
            dictionary of a single active tradies
        """

        _response = requests.get(
            url=endpoint_url,
            headers=_define_request_headers(
                oauth_token=oauth_token,
                accept_profile=self.settings_config.DATABRICKS_ACCEPT_PROFILE,
            ),
            params={**filter_selection, **query_values_dict, "limit": limit_return},
            timeout=timeout_request,
        )

        return random.sample(_response.json(), 1)[0]
