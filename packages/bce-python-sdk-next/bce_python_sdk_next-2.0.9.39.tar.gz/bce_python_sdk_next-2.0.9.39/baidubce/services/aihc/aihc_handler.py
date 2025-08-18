"""
This module provides general http handler functions for 
processing http responses from AIHC services.
"""

import json
import http.client
from baidubce import compat, utils
from baidubce.utils import Expando
from baidubce.exception import BceClientError
from baidubce.exception import BceServerError


def parse_json(http_response, response):
    body = http_response.read()
    if body:
        response.__dict__.update(json.loads(
            body, object_hook=dict_to_python_object).__dict__)
    http_response.close()
    return True


def dict_to_python_object(d):
    """

    :param d:
    :return:
    """
    attr = {}
    for k, v in list(d.items()):
        k = str(k)
        attr[k] = v
    return Expando(attr)

def parse_json_list(http_response, response):
    """
    Parse JSON list response and convert to Python object.
    
    If the body is not empty, convert it to a Python object and set as the value of
    response.result. The http_response is always closed if no error occurs.
    
    Args:
        http_response: The http_response object returned by HTTPConnection.getresponse()
        response: General response object which will be returned to the caller
        
    Returns:
        bool: Always returns True
    """
    body = http_response.read()
    if body:
        body = compat.convert_to_string(body)
        response.__dict__["result"] = json.loads(body, object_hook=utils.dict_to_python_object)
        response.__dict__["raw_data"] = body
    http_response.close()
    return True


def parse_error(http_response, response):
    """
    Handle error responses and raise appropriate exceptions.
    
    If the HTTP status code is not 2xx, parse the error response and raise
    appropriate BCE exceptions. The http_response is always closed.
    
    Args:
        http_response: The http_response object returned by HTTPConnection.getresponse()
        response: General response object which will be returned to the caller
        
    Returns:
        bool: False if HTTP status code is 2xx
        
    Raises:
        BceClientError: If HTTP status code is 1xx (not handled)
        BceServerError: If HTTP status code is not 2xx (error response)
    """
    if http_response.status // 100 == http.client.OK // 100:
        return False
    if http_response.status // 100 == http.client.CONTINUE // 100:
        raise BceClientError(b'Can not handle 1xx http status code')
    body = http_response.read()
    if not body:
        bse = BceServerError(http_response.reason, request_id=response.metadata.bce_request_id)
        bse.status_code = http_response.status
        raise bse

    error_dict = json.loads(compat.convert_to_string(body))
    message = str(error_dict)
    if 'message' in error_dict and error_dict['message'] is not None:
        message = error_dict['message']
    code = "Exception"
    if 'code' in error_dict and error_dict['code'] is not None:
        code = error_dict['code']
    request_id = response.metadata.bce_request_id
    if 'request_id' in error_dict and error_dict['request_id'] is not None:
        request_id = error_dict['request_id']

    bse = BceServerError(message, code=code, request_id=request_id)
    bse.status_code = http_response.status
    raise bse
