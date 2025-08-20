# -*- coding: utf-8 -*-
"""
jfExt.Mgr.mailMgr.py
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from flask_mail import Mail, Message

from ..SingletonExt import Singleton


@Singleton
class MailMgr():
    """
    >>> Mail Manager
    """

    def __init__(self):
        self._mail = None

    @property
    def mail(self):
        assert(self._mail)      # ❗️❗️未初始化 Mail Client # noqa
        return self._mail

    @mail.setter
    def mail(self, mail):
        if isinstance(mail, Mail):
            self._mail = mail

    def send_email(self, title, body, sender, recipients=[], bcc=[], files=None):
        """
        >>> 发送邮件
        :param {String} title: 邮件标题
        :param {String} body: 邮件内容
        :param {list<String>} recipients: 收件人列表
        :return {Boolean}: 发送结果状态
        """
        try:
            msg = Message(
                title,
                sender=sender,
                recipients=recipients,
                bcc=bcc
            )
            msg.html = body
            if files:
                for file in files:
                    file_path = file['file_path']
                    file_name = file['file_name']
                    file_type = file['file_type']
                    with open(file_path, 'r') as fp:
                        msg.attach(file_name, file_type, fp.read())
            self.mail.send(msg)
            return True
        except Exception:
            import traceback
            traceback.print_exc()
            return False
