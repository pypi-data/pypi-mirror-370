import os

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def call_kyos_api_v1(url, method='get', payload={}, timeout=10):
    """Performs an HTTP request to KYOS API and returns HTTP response Code and body

    Args:
        url (string): Part of url that indicates API endpoint (eg, /curves/1)
        method (string): HTTP post. Can be: get, post, put, patch, delete
        payload (dict): HTTP request payload/post body. Needed for POST/PATCH/PUT
        timeout (int): Configured request timeout in seconds.

    Returns:
        (tuple): tuple containing:

            - (int): HTTP response status code
            - (dict): HTTP response body

    Note:
        This function relies on `EXECUTOR_HASH` and `PLATFORM_HOSTNAME` environment variables to be set.

        When job is running from inside a production container, these variables will be automatically set.

        In case of debugging, these need to be set from PyCharm's active configuration, or by executing:

        - `$ export EXECUTOR_HASH=8I2817LTWFBKVOPNRI4G7D6TXKGJJHA5XWDDG5CL`
        - `$ export PLATFORM_HOSTNAME=client.kyos.com`

    Examples:
        >>> from kyoslib_py.kyos_api import call_kyos_api_v1
        >>> status, data = call_kyos_api_v1("/commodities?ids=1")
        >>> if 200 >= status < 300:
        >>>     print(data)
        >>> else:
        >>>     print("An error was encountered: ", data)
        '{'data': [{'id': 1, 'name': 'Dutch power'}], 'includes': [], 'relationships': []}'
    """
    mandatory_env_vars = ["EXECUTOR_HASH", "PLATFORM_HOSTNAME"]

    for var in mandatory_env_vars:
        if var not in os.environ:
            raise EnvironmentError("Failed because {} is not set.".format(var))

    headers = {"Authorization": f"Bearer {os.getenv('EXECUTOR_HASH')}"}

    base_url = 'https://' + os.getenv('PLATFORM_HOSTNAME') + '/api/v1'
    url = (base_url + url) if (url[0] == '/') else (base_url + '/' + url)

    s = requests.Session()
    s.headers.update(headers)

    try:
        if method.lower() == 'get':
            response = requests_retry_session(session=s).get(url, timeout=timeout, verify=False)
        elif method.lower() == 'post':
            response = requests_retry_session(session=s).post(
                url, json=payload, timeout=timeout, verify=False
            )
        elif method.lower() == 'put' or method.lower() == 'patch':
            response = requests_retry_session(session=s).patch(
                url, json=payload, timeout=timeout, verify=False
            )
        elif method.lower() == 'delete':
            response = requests_retry_session(session=s).delete(url, timeout=timeout, verify=False)
    except Exception as err:
        return 500, {'error': 'Request failed with: %s' % str(err.__class__.__name__)}
    else:
        return response.status_code, response.json()
