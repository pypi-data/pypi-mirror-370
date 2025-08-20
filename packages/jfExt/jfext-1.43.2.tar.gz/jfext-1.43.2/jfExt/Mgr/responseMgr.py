# -*- coding: utf-8 -*-
"""
jf-ext.Mgr.responseMgr.py
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import json
from flask import jsonify
from ..EncryptExt import *
from ..Time.TimeExt import *


class APIResponseType():
    """
    >>> API 业务响应类型
    """

    # 成功
    SUCCESS = 0
    # 错误
    # - 1xx
    ERROR_INTERNAL = 100                    # 内部错误
    ERROR_REQUEST_URL_FORMAT = 101          # URL未找到
    ERROR_REQUEST_PARAM_FORMAT = 102        # GET请求 参数错误
    ERROR_REQUEST_DATA_FORMAT = 103         # POST请求 JSON参数错误
    ERROR_REQUEST_DATA_MD5 = 104            # POST请求 MD5验证失败
    ERROR_VERIFICATION = 105                # 错误验证码
    ERROR_USER_EXIST = 106                  # 用户已存在
    ERROR_USER_NOT_EXIST = 107              # 用户不存在
    ERROR_USER_WRONG_PASSWD = 108           # 用户密码错误
    ERROR_NO_RESULT = 110                   # 无查询数据
    ERROR_AUTH_FAILURE = 120                # 授权失败
    ERROR_TOO_FAST = 130                    # 请求过快
    ERROR_LINK_EXPIRED = 135                # 链接已过期
    ERROR_UNDEFINED = 140                   # 未定义
    ERROR_DATA_EXIST = 150                  # 数据已存在
    ERROR_DATA_NOT_EXIST = 151              # 数据不存在存在
    ERROR_SEARCH_KEYWORD_TOO_SHORT = 160    # 搜索关键词太短
    ERROR_FILE_NOT_EXIST = 170              # 文件不存在
    # - 4xx
    ERROR_ERROR_TOKEN = 402                 # token 错误
    ERROR_NO_PERMISSION = 403               # 权限不足
    # - 6xx
    ERROR_SERVER_MAINTENANCE = 600          # 服务器维护
    # 业务代码 9XXX
    ERROR_BUSINESS_DOMAIN_NOT_FOUND = 9001      # 域名未找到
    ERROR_BUSINESS_STANDARD_SKU_EXIST = 9010    # 规格barcode已存在
    ERROR_BUSINESS_FILE_FORMAT = 9020           # 文件格式有问题
    # ---- 91xx
    ERROR_BUSINESS_NO_ORIGINAL_FILE = 9120      #
    ERROR_BUSINESS_NO_WECHAT_FILE = 9121        #
    ERROR_BUSINESS_NO_SAMPLE_FILE = 9122        #
    ERROR_BUSINESS_ORIGINAL_FILE_ERROR = 9123   #
    ERROR_BUSINESS_WECHAT_FILE_ERROR = 9124     #
    ERROR_BUSINESS_SAMPLE_FILE_ERROR = 9125     #
    ERROR_BUSINESS_PAYMENT_REMAINING = 9130     # 付款金额与应付金额不匹配
    # - 9999
    ERROR_SILENT = 9999                     # 错误静音


class APIResponse():

    @classmethod
    def error(cls, code, msg=None):
        """
        >>> 响应: error
        :param {Int} code: 业务错误状态码
        :param {String} msg: 业务错误描述
        :return {JSON}: 响应body
        """
        if code > 0:
            for key in APIResponseType.__dict__:
                standard_code = getattr(APIResponseType, key, -1)
                if standard_code == code and not msg:
                    msg = key
            print("%" * 50)
            print("error [{}] - {}".format(code, msg))
            data_json = json.dumps(
                {},
                separators=(',', ':'),
                ensure_ascii=False,
                sort_keys=True
            )
            return jsonify({
                'code': code,
                'msg': msg,
                'data': {},
                'md5': generate_md5(data_json),
            })

    @classmethod
    def success(cls, data):
        """
        >>> 响应: success
        :param {String} data: 响应数据
        :return {JSON}: 响应body
        """
        data_json = json.dumps(
            data,
            separators=(',', ':'),
            ensure_ascii=False,
            sort_keys=True
        )
        return jsonify({
            'code': APIResponseType.SUCCESS,
            'msg': "SUCCESS",
            'data': data,
            'md5': generate_md5(data_json),
            'timestamp': time_now_timestamp()
        })
