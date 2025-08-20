
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
from holado.common.handlers.object import DeleteableObject, Object
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.element_exception import ElementNotFoundException
from holado_python.standard_library.typing import Typing

logger = None

def initialize_logger():
    global logger
    logger = logging.getLogger(__name__)


class Context(DeleteableObject):
    """
    @summary: Mother class for any context class
    """
    
    def __init__(self, name):
        super().__init__(name)
        self.on_delete_call_gc_collect = True
        
        self.__objects = {}
        self.__on_delete_objects = []
        
    def get_context_name(self):
        return Object.name(self)
    
    def _delete_object(self):
        # Remove all objects
        self.remove_all_objects()
    
    def remove_all_objects(self):
        from holado_core.common.exceptions.functional_exception import FunctionalException
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        keys = set(self.__objects.keys())
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Removing {len(keys)} objects: {keys}")
        for index, key in enumerate(keys):
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"[{self.name}] Removing object {index+1}/{len(keys)}: '{key}' (type: {Typing.get_object_class_fullname(self.get_object(key))})")
            try:
                self.remove_object(key)
            except FunctionalException as exc:
                raise TechnicalException() from exc
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Finished to remove {len(keys)} objects: {keys}")
                
    def remove_object(self, name):
        if not self.has_object(name):
            from holado_core.common.exceptions.technical_exception import TechnicalException
            raise TechnicalException("Context doesn't contain object '{}'".format(name))
        self._remove(name, True)
        
    def _remove(self, name, remove_from_lifetime_manager):
        obj = self.get_object(name)
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[{self.name}] Removing object '{name}' (type: {Typing.get_object_class_fullname(obj)})")
        if name in self.__on_delete_objects:
            if isinstance(obj, DeleteableObject):
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"[{self.name}] Deleting object '{name}'")
                try:
                    obj.delete_object()
                except Exception:
                    logger.exception(f"[{self.name}] Catched exception while deleting object '{name}'")
                else:
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"[{self.name}] Deleted object '{name}'")
            self.__on_delete_objects.remove(name)
            
        if self.has_object(name):
            del self.__objects[name]
#         if remove_from_lifetime_manager:
#             from holado.common.context.session_context import SessionContext
#             SessionContext.instance().get_object_lifetime_manager().remove_object_lifetime(name, self)
        
    def set_object(self, name, obj, raise_if_already_set = True):
        from holado_core.common.exceptions.functional_exception import FunctionalException
        from holado_core.common.exceptions.technical_exception import TechnicalException
        
        if obj is None:
            if self.has_object(name):
                try:
                    self.remove_object(name)
                except FunctionalException as e:
                    raise TechnicalException() from e
        else:
            if raise_if_already_set and self.has_object(name):
                raise TechnicalException(f"[{self.name}] Context already contains object '{name}'")
            self._put(name, obj)
                    
    def _put(self, name, obj):
        self.__objects[name] = obj
        self.__on_delete_objects.append(name)
        
    def get_object(self, name):
        if not self.has_object(name):
            from holado_core.common.exceptions.technical_exception import TechnicalException
            raise TechnicalException(f"[{self.name}] Context doesn't contain object '{name}'")
        return self.__objects[name]

    def has_object(self, name):
        return name in self.__objects
    
    def get_object_name(self, obj):
        for name, value in self.__objects.items():
            if value is obj:
                return name
        return None
        
    def remove_lifetimed_object(self, object_id):
        self._remove(object_id, False)
        
    def get_or_create_initilizable_object_by_class(self, object_class):
        raise NotImplementedError()
        
    def get_or_create_object_by_class(self, object_class):
        raise NotImplementedError()
    
    def get_object_getter_eval_string(self, obj, raise_not_found=True):
        name = self.get_object_name(obj)
        if name is not None:
            return f"{Typing.get_object_class_fullname(self)}.instance().get_object('{name}')"
        
        if raise_not_found:
            raise ElementNotFoundException(f"[{self.name}] Failed to find object of id {id(obj)}")
        else:
            return None


