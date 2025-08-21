from bot_common.utils.utils import catch_exception
from bot_common.utils.logging_conf import logger
from pydantic import BaseModel
from typing import Any
import requests
import json


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = 'OK'
    response: Any = None


@catch_exception
def manage_api_request(url, req, case='', out_obj=None, timeout=12):
    try:
        resp = requests.post(url, json=req, timeout=timeout)
        if resp.status_code != 200:
            raise Exception(f'{case} api_request exception: error_code = {resp.status_code}')
        resp_obj = SuccessResponse.parse_obj(resp.json())
        if not bool(resp_obj.success):
            raise Exception(f'{case} exception: {str(resp_obj.message)}')
        elif out_obj:
            return out_obj.parse_obj(resp_obj.response)
        else:
            return resp_obj.response
    except requests.ConnectionError:
        raise Exception(f'{case} {url} not found')
