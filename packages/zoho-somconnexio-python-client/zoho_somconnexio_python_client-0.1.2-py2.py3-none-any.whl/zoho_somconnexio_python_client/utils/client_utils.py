from zoho_somconnexio_python_client.exceptions import ZohoCRMClientException


def check_payload(data: dict):
    if isinstance(data, list):
        data = {"data": data}
    elif isinstance(data, dict):
        data = {"data": [data]}
    else:
        raise ZohoCRMClientException(500, "Invalid payload data")
    return data


def check_params(params):
    if params is None:
        params = {}
    return params
