import os
from typing import Optional
from atk_common.interfaces import IEnvHandler
from atk_common.interfaces import ILogger

class EnvHandler(IEnvHandler):
    def __init__(self, logger: Optional[ILogger]): # type: ignore
        self.logger = logger

    def val_str(self, value):
        if value is None:
            return '<Empty>'
        if isinstance(value, str):
            if value.strip() == '' or value.lower() == 'null':
                return '<Null>'
            return value
        return str(value)

    def is_value_null_or_empty(self, value):
        if isinstance(value, str):
            return value.strip() == '' or value.lower() == 'null'
        return False

    def get_env_value(self, key, abort_on_error=True):
        val = os.environ.get(key)
        if self.logger:
            self.logger.info(key + ':' + self.val_str(val))
        if val is None and abort_on_error:
            err_msg = f"Environment variable '{key}' is not set."
            if self.logger:
                self.logger.error(err_msg)
            raise ValueError(err_msg)
        if self.is_value_null_or_empty(val):
            return None
        return val
    
    def set_logger(self, logger: ILogger):
        self.logger = logger
