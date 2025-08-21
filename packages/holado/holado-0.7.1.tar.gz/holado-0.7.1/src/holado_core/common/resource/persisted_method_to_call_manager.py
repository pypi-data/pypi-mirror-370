
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import json
from holado_core.common.resource.persisted_data_manager import PersistedDataManager
from holado_python.standard_library.typing import Typing
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)



class PersistedMethodToCallManager(PersistedDataManager):
    def __init__(self, data_name="method", table_name="method_to_call", db_name="default"):
        super().__init__(data_name=data_name, table_name=table_name, 
                         table_sql_create=self._get_default_table_sql_create(table_name), 
                         db_name=db_name)
    
    def initialize(self, resource_manager, expression_evaluator):
        super().initialize(resource_manager)
        self.__expression_evaluator = expression_evaluator
    
    def _get_default_table_sql_create(self, table_name):
        return f"""CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                function_qualname text NOT NULL,
                self_getter text,
                args text,
                kwargs text,
                use text NOT NULL,
                use_index integer NOT NULL
            )"""
    
    def add_function_to_call(self, function_qualname, args_list=None, kwargs_dict=None, use="default", use_index=0):
        """Add a function to call.
        @param function_qualname: Qualified name of function
        @param args_list: List of function args (default: None)
        @param kwargs_dict: Dict of function kwargs (default: None)
        @param use: Define persistent usage. It usually corresponds to a specific scope.
        @param use_index: use index, useable to order the functions to call. By default all are 0. If set to None, it is automatically set to max(use_index)+1.
        """
        self.add_method_to_call(function_qualname, None, args_list, kwargs_dict, use, use_index)
    
    def add_method_to_call(self, function_qualname, self_getter_eval_str, args_list=None, kwargs_dict=None, use="default", use_index=0):
        """Add a method to call.
        @param function_qualname: Qualified name of function
        @param self_getter_eval_str: String to eval in order to get the self instance to use when calling method 
        @param args_list: List of function args (default: None)
        @param kwargs_dict: Dict of function kwargs (default: None)
        @param use: Define persistent usage. It usually corresponds to a specific scope.
        @param use_index: use index, useable to order the functions to call. By default all are 0. If set to None, it is automatically set to max(use_index)+1.
        """
        if use_index is None:
            use_index = self.__get_use_next_index(use)
            
        data = {
            'function_qualname': function_qualname,
            'self_getter': self_getter_eval_str,
            'use': use,
            'use_index': use_index
            }
        if args_list is not None:
            data['args'] = json.dumps(args_list)
        if kwargs_dict is not None:
            data['kwargs'] = json.dumps(kwargs_dict)
            
        self.add_persisted_data(data)
    
    def __get_use_next_index(self, use):
        datas = self.get_persisted_datas({'use':use})
        if datas:
            return max(map(lambda x:x['a'], datas)) + 1
        else:
            return 0
    
    def call_functions_and_methods(self, use="default", use_index=None, delete_after_call=False):
        """Call methods of given use
        @param use: Define persistent usage. It usually corresponds to a specific scope.
        @param use_index: If defined, call only functions and methods of given index.
        @param delete_after_call: Define if function or method is deleted after call from persisted data.
        """
        # Get functions and methods to call
        filter_data = {'use':use}
        if use_index is not None:
            filter_data['use_index'] = use_index
        methods_data = self.get_persisted_datas(filter_data)
        
        # Call methods
        if methods_data:
            for meth_index, meth_data in enumerate(methods_data):
                do_delete = delete_after_call
                try:
                    self._call_function_or_method(meth_data)
                except Exception as exc:
                    msg_list = [f"Error while calling following method (use: '{use}' ; use index: {use_index} ; method index: {meth_index} ; delete after call: {delete_after_call}):"]
                    msg_list.append(Tools.represent_object(meth_data, 8))
                    msg_list.append("    Error:")
                    msg_list.append(Tools.represent_exception(exc, indent=8))
                    msg_list.append("  => Continue to process persisted methods")
                    msg_list.append("     WARNING: this method is removed from persisted methods to avoid recursive and blocking errors")
                    logger.error("\n".join(msg_list))
                    do_delete = True
                
                if do_delete:
                    self.__delete_function_or_method(meth_data)
    
    def __delete_function_or_method(self, function_or_method_data):
        filter_data = {'id':function_or_method_data['id']}
        self.delete_persisted_data(filter_data)
    
    def _call_function_or_method(self, function_or_method_data):
        _, func = self.__expression_evaluator.evaluate_python_expression(function_or_method_data['function_qualname'])
        if not Typing.is_function(func):
            raise TechnicalException(f"Failed to evaluate python expression '{function_or_method_data['function_qualname']}' as a function (obtained: {func} [type: {Typing.get_object_class_fullname(func)}] ; function data: {function_or_method_data})")
        
        func_self = None
        if function_or_method_data['self_getter'] is not None:
            _, func_self = self.__expression_evaluator.evaluate_python_expression(function_or_method_data['self_getter'])
        
        if function_or_method_data['args'] is not None:
            args = json.loads(function_or_method_data['args'])
        else:
            args = []
        if function_or_method_data['kwargs'] is not None:
            kwargs = json.loads(function_or_method_data['kwargs'])
        else:
            kwargs = {}
        
        if func_self is not None:
            func(func_self, *args, **kwargs)
        else:
            func(*args, **kwargs)
        
    
