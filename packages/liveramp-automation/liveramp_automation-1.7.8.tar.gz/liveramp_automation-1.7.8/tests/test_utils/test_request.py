from liveramp_automation.utils import request
from unittest.mock import patch
import requests

def mocked_requests_response(*args, **kwargs):
    response = requests.models.Response()
    response.status_code = 200
    return response

def mocked_requests_response_throw_HTTPError(*args, **kwargs):
    raise requests.exceptions.HTTPError("url", "", "HTTPError", None, None)

def mocked_requests_response_throw_RequestException(*args, **kwargs):
    raise requests.exceptions.RequestException("url", "", "RequestException", None, None)

def mocked_requests_response_throw_Timeout(*args, **kwargs):
    raise requests.exceptions.Timeout("url", "", "Timeout", None, None)

def mocked_allure_method():
    pass

@patch('allure.attach')
def test_request_post_data(mock):
    url = 'https://serviceaccounts.liveramp.com/authn/v1/oauth2/token'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": "liveramp-api"
    }
    response = request.request_post(url, headers=headers, data=data)
    assert response.status_code == 400

@patch('allure.attach')
def test_request_post_json(mock):
    url = 'https://serviceaccounts.liveramp.com/authn/v1/oauth2/token'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": "liveramp-api"
    }
    response = request.request_post(url, headers=headers, data=None, json=data)
    assert response.status_code == 400

@patch('allure.attach')
def test_request_post_json(mock):
    url = 'https://serviceaccounts.liveramp.com/authn/v1/oauth2/token'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": "liveramp-api"
    }
    response = request.request_post(url, headers=headers, json=data)
    assert response.status_code == 400


@patch('allure.attach')
@patch('requests.get')
def test_request_get(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_get(url, headers=headers, data=data)
    assert response is not None

@patch('allure.attach')
@patch('requests.get')
def test_request_get_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test" : "test"
    }
    response = request.request_get(url, headers=headers, data=None, json=data)
    assert response is not None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response)
def test_request_delete(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_delete(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response)
def test_request_delete_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_delete(url, headers=headers, data=None, json=data)
    assert response.status_code == 200


@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response)
def test_request_options(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response)
def test_request_head(mock1, mock2):
    url = 'https://www.google.com/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_head(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response)
def test_request_head_json(mock1, mock2):
    url = 'https://www.google.com/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_head(url, headers=headers, data=None, json=data)
    assert response.status_code == 200


@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response)
def test_request_put(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_put(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response)
def test_request_put_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_put(url, headers=headers, data=None, json=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response)
def test_request_patch(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_patch(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response)
def test_request_patch_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_patch(url, headers=headers, data=None, json=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_post_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_get_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_delete_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_options_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_head_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_head(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_put_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_put(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_patch_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_patch(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_RequestException)
def test_request_post_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_throw_RequestException)
def test_request_get_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response_throw_RequestException)
def test_request_delete_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_throw_RequestException)
def test_request_options_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response_throw_RequestException)
def test_request_head_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_head(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response_throw_RequestException)
def test_request_put_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_put(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response_throw_RequestException)
def test_request_patch_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_patch(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_Timeout)
def test_request_post_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_throw_Timeout)
def test_request_get_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response_throw_Timeout)
def test_request_delete_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_throw_Timeout)
def test_request_options_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response_throw_Timeout)
def test_request_head_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_head(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response_throw_Timeout)
def test_request_put_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_put(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response_throw_Timeout)
def test_request_patch_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_patch(url, headers=headers, data=data)
    assert response is None