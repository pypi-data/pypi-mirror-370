# -*- __rmi__.py: python ; coding: utf-8 -*-
# 访问服务器相关的工具类
import datetime
import time
from urllib.parse import urlparse

import requests
import urllib3

from . import Obj, d2o
from . import json_dump
from .win32 import get_profile, read_settings


def time_stamp(t) -> int:
    return int(time.mktime(t.timetuple()))


"""
http 请求-解析相关的工具类
"""


class RCall:
    service_base = None
    _default_obj_cls = Obj

    def __init__(self, url, direct_response=False):
        """
        远程调用
        :param url: 服务位置URL
        :param direct_response: 是否直接返回response对象。
        - True 直接返回response, get / post / put 方法中的cls参数将被忽略;
        - False 返回转换后的结果，类型由get / post / put 方法中的cls参数决定.
        """
        self._set_url(url)
        self._verify_ssl = False
        self._direct_response = direct_response  # 直接返回响应对象，不做json转换
        self._cert = ('', '')
        self._headers = self.default_headers()
        urllib3.disable_warnings()

    def default_headers(self):
        return {}

    def _set_url(self, url):
        if self.service_base:
            self._url = self.service_base + url
        else:
            self._url = url

    def _json_obj(self, r, obj_cls=None):
        if r.status_code != 200:
            raise RuntimeError(r.status_code, r.text)
        try:
            o = r.json(strict=False)
            o_type = type(o)
            if obj_cls is None:
                obj_cls = self._default_obj_cls
            if o_type in (list, tuple, set):
                return [d2o(oo, obj_cls) for oo in o]
            else:
                return d2o(o, obj_cls)
        except Exception as e:
            print('解析json错误', e)
            print(r.content)
            raise RuntimeError(e)

    def get(self, obj_cls=None, **kwargs):
        r = requests.get(self._url, params=kwargs, headers=self._headers, verify=self._verify_ssl, cert=self._cert)
        try:
            if self._direct_response:
                return r
            else:
                return self._json_obj(r, obj_cls)
        except Exception as e:
            print('error occurs while parsing json from request:', 'url=%s' % self._url, r, obj_cls, sep='\n')
            raise e

    def post(self, data=None, obj_cls=None, files=None, json=None, **kwargs):
        if data or json:
            json_data = json if json else json_dump(data)  # 给了json优先
            r = requests.post(self._url, json=json_data, headers=self._headers, files=files, params=kwargs,
                              verify=self._verify_ssl,
                              cert=self._cert)
        else:
            r = requests.post(self._url, files=files, headers=self._headers, params=kwargs, verify=self._verify_ssl,
                              cert=self._cert)
        if self._direct_response:
            return r
        else:
            return self._json_obj(r, obj_cls)

    def put(self, data=None, obj_cls=None, json=None, **kwargs):
        json_data = json if json else json_dump(data)  # 给了json优先
        r = requests.put(self._url, json=json_data, headers=self._headers, params=kwargs, verify=self._verify_ssl,
                         cert=self._cert)
        if self._direct_response:
            return r
        else:
            return self._json_obj(r, obj_cls)

    def delete(self, data=None, json=None, **kwargs):
        json_data = json if json else json_dump(data)  # 给了json优先
        r = requests.delete(self._url, json=json_data, headers=self._headers, params=kwargs,
                            verify=self._verify_ssl,
                            cert=self._cert)
        if self._direct_response:
            return r
        else:
            return self._json_obj(r)

    def url(self):
        return self._url


# 远程受保护的API调用
# 按照远程服务器的安全认证机制处理header，如果还没有获得服务器端的令牌，调用登录机制获得。
class AuthCall(RCall):
    EXPIRE_MINUTES = 20
    _secret_header = 'Token'
    _auth_token = None
    _last_login_time = None

    def __init__(self, url, header_builder=None):
        super().__init__(url)
        self._headers = self.default_headers()
        if header_builder:
            header_builder(self._headers)

    def has_expired(self):
        if self._last_login_time is None:
            return True
        return time_stamp(datetime.datetime.now()) - self._last_login_time > AuthCall.EXPIRE_MINUTES * 60

    # 处理安全机制
    def _auth(self):
        try:
            if AuthCall._auth_token and not self.has_expired():  # 已经有token了且未过期
                return
            else:  # 执行login
                AuthCall._auth_token = self._login()
                self._headers = self.default_headers()
        except Exception as e:
            raise RuntimeError('安全检查异常', e)

    def _login(self):
        user, mail, reg_code = get_profile()
        auth_code = read_settings('reg.auth', '')
        # login 需要post  multipart / from-data类型数据
        # 有两种方式：
        # 手动组建form-data并修改headers
        # 通过files参数传递form-data，推荐此种方式
        # form.username - 用户名/注册邮箱
        # form.password - 用户口令/授权码
        # form.client_id - 客户端标识/注册设备号
        files = {
            'username': (None, mail),
            "password": (None, auth_code),
            "client_id": (None, reg_code),
            "client_secret": (None, user),
        }
        response = requests.post(self.login_url(), files=files, verify=False)
        if response.status_code == 200:
            obj = response.json()
            AuthCall._last_login_time = time_stamp(datetime.datetime.now())
            return obj['access_token']
        else:
            raise RuntimeError(response.status_code, response.text)

    def login_url(self):
        url = urlparse(self.url())
        return fr"{url.scheme}://{url.hostname}:{url.port}/login"

    def get(self, obj_cls=None, **kwargs):
        self._auth()
        return super().get(obj_cls, **kwargs)

    def post(self, data=None, obj_cls=None, files=None, **kwargs):
        self._auth()
        return super().post(data, obj_cls, files, **kwargs)

    def put(self, data=None, obj_cls=None, json=None, **kwargs):
        self._auth()
        return super().put(data, obj_cls, **kwargs)

    def delete(self, data=None, **kwargs):
        self._auth()
        return super().delete(data, **kwargs)

    def default_headers(self):
        if AuthCall._auth_token:
            token = AuthCall._auth_token
            return {'authorization': f'Bearer {token}'}
        else:
            return {}
