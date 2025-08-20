# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.BooleanExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import six


# pragma mark - Define
# --------------------------------------------------------------------------------
TRUE_STRINGS = ('1', 't', 'true', 'on', 'y', 'yes')
FALSE_STRINGS = ('0', 'f', 'false', 'off', 'n', 'no')


def bool_from_string(subject, strict=False, default=False):
    """
    >>> 根据string判断布尔型
    :param {} subject:
    :param {Boolean} strict:
    :param {Boolean} default:
    """
    """Interpret a string as a boolean.

    A case-insensitive match is performed such that strings matching 't',
    'true', 'on', 'y', 'yes', or '1' are considered True and, when
    `strict=False`, anything else returns the value specified by 'default'.

    Useful for JSON-decoded stuff and config file parsing.

    If `strict=True`, unrecognized values, including None, will raise a
    ValueError which is useful when parsing values passed in from an API call.
    Strings yielding False are 'f', 'false', 'off', 'n', 'no', or '0'.
    """
    if not isinstance(subject, six.string_types):
        subject = six.text_type(subject)

    lowered = subject.strip().lower()

    if lowered in TRUE_STRINGS:
        return True
    elif lowered in FALSE_STRINGS:
        return False
    elif strict:
        acceptable = ', '.join(
            "'%s'" % s for s in sorted(TRUE_STRINGS + FALSE_STRINGS))
        msg = ("Unrecognized value '%(val)s', acceptable values are: %(acceptable)s") % {'val': subject, 'acceptable': acceptable}
        raise ValueError(msg)
    else:
        return default
