import os
import time
import sys
import requests
from qalita.cli import pass_config
from qalita.internal.utils import logger


@pass_config
def send_api_request(
    config,
    request,
    mode,
    timeout=10,
    total_retry=3,
    current_retry=0,
    grace_period=10,
    query_params={},
    data=None,
):
    agent_conf = config.load_agent_config()
    r = send_request(
        f"{agent_conf['context']['local']['url']}{request}",
        mode,
        timeout,
        total_retry,
        current_retry,
        grace_period,
        query_params,
        data=data,
    )
    return r


@pass_config
def send_request(
    config,
    request,
    mode,
    timeout=300,
    total_retry=3,
    current_retry=0,
    grace_period=10,
    query_params={},
    data=None,
    file_path=None,
):
    """Send a request to the backend, manages retries and timeout"""
    if current_retry == total_retry:
        logger.error(
            f"Agent can't communicate with backend after {total_retry} retries"
        )
        sys.exit(1)

    if config.token:
        headers = {"Authorization": f"Bearer {config.token}"}
    else:
        config = config.load_agent_config()
        headers = {"Authorization": f"Bearer {config['context']['local']['token']}"}

    verify_ssl = not os.getenv("SKIP_SSL_VERIFY", False)

    try:
        if mode == "post":
            r = requests.post(
                request,
                headers=headers,
                timeout=timeout,
                params=query_params,
                json=data,
                verify=verify_ssl,
            )
        elif mode == "post-multipart":
            with open(file_path, "rb") as f:
                r = requests.post(
                    request,
                    headers=headers,
                    files={"file": f},
                    timeout=timeout,
                    params=query_params,
                    json=data,
                    verify=verify_ssl,
                )
        elif mode == "get":
            r = requests.get(
                request,
                headers=headers,
                timeout=timeout,
                params=query_params,
                verify=verify_ssl,
            )
        elif mode == "put":
            r = requests.put(
                request,
                headers=headers,
                timeout=timeout,
                params=query_params,
                json=data,
                verify=verify_ssl,
            )
        return r
    except Exception as exception:
        logger.warning(f"Agent can't communicate with backend : {exception}")
        logger.info(
            f"Retrying {current_retry+1}/{total_retry} in {grace_period} seconds..."
        )
        time.sleep(grace_period)
        r = send_request(
            config,
            request,
            mode,
            timeout,
            total_retry,
            current_retry + 1,
            grace_period,
            query_params,
            data,
            file_path,
        )
        logger.success(f"Backend communication restored")
        return r
