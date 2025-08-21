from typing import Dict


def _define_request_headers(
    oauth_token: str,
    accept_profile: str,
) -> Dict:
    """
    function to define request header

        Parameters
        ----------
        oauth_token: str
            oauth token
        accept_profile: str
            name of accept profile; schema of UC

        Returns
        ----------
        Dict
            dictionary for request header
    """

    return {"Authorization": f"Bearer {oauth_token}", "Accept-Profile": accept_profile}


def _define_oauth_request_payload(
    online_table_name: str,
) -> Dict:
    """
    function to define oauth request payload

        Parameters
        ----------
        online_table_name: str
            name of online table

        Returns
        ----------
        Dict
            dictionary for request header
    """

    return {
        "grant_type": "client_credentials",
        "scope": "all-apis",
        "authorization_details": f'[{{"type":"unity_catalog_permission","securable_type":"table","securable_object_name":"{online_table_name}","operation":"ReadOnlineView"}}]',  # noqa: E501
    }
