import json
import logging
from time import sleep

import requests


def request_post_json(api_url: str, headers: dict, request_param: dict, retry_times: int = 5) -> dict:
    '''
    发送post request，使用自动重试机制；得到json并转换成字典返回
    :param request_param: 字典格式
    :param headers: const里有或传入
    :param api_url:
    :return: 字典
    '''
    request_data = json.dumps(request_param)
    for _ in range(retry_times):  # 重试机制
        try:
            response = requests.post(api_url,
                                     headers=headers,
                                     data=request_data)
            if response.status_code != 200:
                logging.error('返回code不是200！')
                raise Exception
        except:
            sleep(2)
        else:
            break
    return response.json()
