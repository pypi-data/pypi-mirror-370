# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 14:09
# @Author : 毛鹏
from ...data_processor import DataProcessor
from ...decorator import sync_method_callback
from ...exceptions import MangoToolsError
from ...exceptions.error_msg import ERROR_MSG_0061
from ...models import MethodModel


class CustomAssertion:
    """函数断言"""

    def __init__(self, test_data: DataProcessor):
        self.test_data = test_data

    @staticmethod
    @sync_method_callback('函数断言', '函数断言', 7, [
        MethodModel(f='func_str', p='请输入一个函数，在函数里面自己断言', d=True),
        MethodModel(f='func_name', p='请输入这个函数的名称', d=True), ])
    def ass_func(func_str, func_name='func'):
        """输入断言代码"""
        try:
            global_namespace = {}
            exec(func_str, global_namespace)
            return global_namespace[func_name]
        except (KeyError, SyntaxError, TypeError):
            import traceback
            traceback.print_exc()
            raise MangoToolsError(*ERROR_MSG_0061)
