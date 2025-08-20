# -*- coding: utf-8 -*-
"""
jf-ext.IpExtend.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import validators
import geoip2.database


def ip_get_country(ip, db_dir="/var/lib/GeoIP/"):
    """
    >>> 获取ip地址所在国家
    @params {String} ip:
    @returns: {String} ip所属国家
    """
    try:
        # 验证 IP 有效性
        if not validators.ip_address.ipv4(ip):
            return '未知'
        reader = geoip2.database.Reader('{}/GeoLite2-Country.mmdb'.format(db_dir))
        ip_obj = reader.country(ip)
        return ip_obj.country.names['zh-CN']
    except Exception:
        return '未知'


def ip_get_city(ip, db_dir="/var/lib/GeoIP/"):
    """
    >>> 获取ip地址所在城市
    @params ip:
    :type ip: String
    @returns: {String} ip所属城市
    """
    try:
        # 验证 IP 有效性
        if not validators.ip_address.ipv4(ip):
            return '未知'
        reader = geoip2.database.Reader('{}/GeoLite2-City.mmdb'.format(db_dir))
        ip_obj = reader.city(ip)
        ip_names = ip_obj.city.names
        if ip_names.get('cn', None):
            return ip_names['cn']
        return ip_names['en']
    except Exception:
        return '未知'


def ip_get_time_zone(ip, db_dir="/var/lib/GeoIP/"):
    """
    >>> 获取ip地址所在时区
    @params {String} ip:
    @returns: {String} ip所属时区
    """
    try:
        # 验证 IP 有效性
        if not validators.ip_address.ipv4(ip):
            return '未知'
        reader = geoip2.database.Reader('{}/GeoLite2-City.mmdb'.format(db_dir))
        ip_obj = reader.city(ip)
        return ip_obj.location.time_zone
    except Exception:
        return '未知'


def ip_get_continent(ip, db_dir="/var/lib/GeoIP/"):
    """
    >>> 获取ip地址所在洲

    @params {String} ip:
    @returns: {String} ip所属洲
    """
    try:
        # 验证 IP 有效性
        if not validators.ip_address.ipv4(ip):
            return '未知'
        reader = geoip2.database.Reader('{}/GeoLite2-City.mmdb'.format(db_dir))
        ip_obj = reader.city(ip)
        ip_continent_names = ip_obj.continent.names
        if ip_continent_names.get('zh-CN', None):
            return ip_continent_names['zh-CN']
        return ip_continent_names['en']
    except Exception:
        return '未知'


def ip_get_location(ip, db_dir="/var/lib/GeoIP/"):
    """
    >>> 获取ip地址 经纬度

    @params {String} ip:
    @returns: {String} ip所属 经纬度
    """
    try:
        # 验证 IP 有效性
        if not validators.ip_address.ipv4(ip):
            return '未知'
        reader = geoip2.database.Reader('{}/GeoLite2-City.mmdb'.format(db_dir))
        ip_obj = reader.city(ip)
        return [ip_obj.location.longitude, ip_obj.location.latitude]
    except Exception:
        return '未知'
