# coding=UTF-8

import json
import requests
import os
from collections import OrderedDict
from ..version import __version__
import logging


def request(method, uri, baseUrl=None, params={}, token=None, **kwargs):
    if baseUrl == None:
        baseUrl = os.environ.get('CLOUDPSS_API_URL', 'https://cloudpss.net/')
    url = requests.compat.urljoin(baseUrl,uri)
    token = os.environ.get('CLOUDPSS_TOKEN', None)
    
    if token:
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json; charset=utf-8',
           
        }
    else:
        raise Exception('token undefined')

    xToken =kwargs.get('xToken',None)
    if xToken:
        headers['x-Authorization'] = 'Bearer ' +xToken
        del kwargs['xToken']
    
    r = requests.request(method, url, params=params, headers=headers, **kwargs)
    
    if (uri.startswith('graphql')):
        if 'X-Cloudpss-Version' not in r.headers:
            raise Exception(
                '当前SDK版本（ver 3.X.X）与服务器版本（3.0.0 以下）不兼容，请更换服务器地址或更换SDK版本。')
        os.environ['X_CLOUDPSS_VERSION'] = r.headers['X-Cloudpss-Version']
        if float(r.headers['X-Cloudpss-Version']) >= 5:
            raise Exception('当前SDK版本（ver '+__version__ +'）与服务器版本（ver ' +
                            r.headers['X-Cloudpss-Version'] +
                            '.X.X）不兼容，请更换服务器地址或更换SDK版本(pip 使用 pip install -U cloudpss 命令更新, conda 使用 conda update cloudpss 命令更新)。')

    # if r.ok:
    #     return r
    # logging.debug(r.text)
    # if r.text =="":
    r.raise_for_status()
    if "statusCode" in r.text:
        t = json.loads(r.text)
        raise  Exception(t.get('errors',r.text))
    return r
    
