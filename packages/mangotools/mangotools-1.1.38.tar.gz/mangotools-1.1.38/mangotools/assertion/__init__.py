# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏
import json
import re


from mangotools.exceptions import MangoToolsError
from .custom import CustomAssertion
from .file import FileAssertion, ExcelAssertion, TxtAssertion
from .sql import SqlAssertion
from .text import TextAssertion
from ..data_processor import DataProcessor
from ..database import MysqlConnect
from ..exceptions.error_msg import ERROR_MSG_0019, ERROR_MSG_0021



class MangoAssertion(CustomAssertion, FileAssertion, SqlAssertion, TextAssertion):

    def __init__(self, mysql_conn: MysqlConnect | None = None, test_data: DataProcessor | None = None):
        SqlAssertion.__init__(self, mysql_conn)
        CustomAssertion.__init__(self, test_data)

    def ass(self, method: str, actual, expect=None) -> str:
        if callable(getattr(TextAssertion, method, None)):
            if expect is not None:
                return getattr(self, method)(actual, expect)
            else:
                return getattr(self, method)(actual)
        elif callable(getattr(ExcelAssertion, method, None)):
            try:
                if isinstance(actual, str):
                    try:
                        actual_strip = actual.strip()
                        if actual_strip.startswith('{') or actual_strip.startswith('['):
                            actual = json.loads(actual)
                    except json.decoder.JSONDecodeError:
                        fixed_actual = re.sub(r'\\', r'\\\\', actual)
                        actual = json.loads(fixed_actual)
                if isinstance(expect, str):
                    expect_strip = expect.strip()
                    if expect_strip.startswith('{') or expect_strip.startswith('['):
                        expect = json.loads(expect)
            except json.decoder.JSONDecodeError:
                raise MangoToolsError(*ERROR_MSG_0019)
            return getattr(self, method)(actual, expect)
        elif callable(getattr(SqlAssertion, method, None)):
            if self.mysql_connect is None:
                raise MangoToolsError(*ERROR_MSG_0021)
            try:
                if isinstance(expect, str):
                    expect_strip = expect.strip()
                    if expect_strip.startswith('{') or expect_strip.startswith('['):
                        expect = json.loads(expect)
            except json.decoder.JSONDecodeError:
                expect = expect
            if expect:
                return getattr(self, method)(actual, expect)
            else:
                return getattr(self, method)(actual)
        elif callable(getattr(CustomAssertion, method, None)):
            return getattr(self, method)(actual)
        else:
            return getattr(self, method)(actual, expect)


__all__ = [
    'MangoAssertion',
    'TextAssertion',
    'FileAssertion',
    'SqlAssertion',
    'CustomAssertion',
]
