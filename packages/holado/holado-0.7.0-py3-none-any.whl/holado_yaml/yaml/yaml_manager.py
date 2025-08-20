
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
from holado_core.common.tools.tools import Tools
from holado.common.context.session_context import SessionContext
from holado_core.common.exceptions.functional_exception import FunctionalException
from yaml.loader import BaseLoader, FullLoader, SafeLoader


logger = logging.getLogger(__name__)

try:
    import yaml
    with_yaml = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"YAML is not available. Initialization failed on error: {exc}")
    with_yaml = False


class YAMLManager(object):
    """
    Manage actions on YAML files.
    """
    
    @classmethod
    def is_available(cls):
        return with_yaml
    
    @classmethod
    def __get_path_manager(cls):
        return SessionContext.instance().path_manager
    
    @classmethod
    def load_file(cls, file_path, with_only_strings=False, with_full_yaml_features=False):
        if with_only_strings and with_full_yaml_features:
            raise FunctionalException(f"It is not possible to set both with_only_strings and with_full_yaml_features to True")
        
        if with_only_strings:
            loader = BaseLoader
        elif with_full_yaml_features:
            loader = FullLoader
        else:
            loader = SafeLoader
        
        with open(file_path, 'r') as file:
            res = yaml.load(file, Loader=loader)
        
        return res
    
    @classmethod
    def load_multiple_documents_file(cls, file_path, with_only_strings=False, with_full_yaml_features=False):
        if with_only_strings and with_full_yaml_features:
            raise FunctionalException(f"It is not possible to set both with_only_strings and with_full_yaml_features to True")
        
        if with_only_strings:
            loader = BaseLoader
        elif with_full_yaml_features:
            loader = FullLoader
        else:
            loader = SafeLoader
        
        with open(file_path, 'r') as file:
            res = list(yaml.load_all(file, Loader=loader))
        
        return res
    
    @classmethod
    def save_file(cls, data, file_path):
        cls.__get_path_manager().makedirs(file_path)
        with open(file_path, 'w') as file:
            yaml.dump(data, file)



