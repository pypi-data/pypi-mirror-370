from typing import Any

import logging
import logging.config
from logging import Logger

import ut_log.util.Utils as Utils

TyDic = dict[Any, Any]
TyPath = str
TyLogger = Logger
TyStr = str


class LogEq:
    """Logging Class
    """
    @staticmethod
    def sh_eq(key: Any, value: Any) -> TyStr:
        return f"{key} = {value}"

    @classmethod
    def debug(cls, key: Any, value: Any) -> None:
        Log.debug(cls.sh_eq(key, value), stacklevel=3)

    @classmethod
    def info(cls, key: Any, value: Any) -> None:
        Log.info(cls.sh_eq(key, value), stacklevel=3)

    @classmethod
    def warning(cls, key: Any, value: Any) -> None:
        Log.warning(cls.sh_eq(key, value), stacklevel=3)

    @classmethod
    def error(cls, key: Any, value: Any) -> None:
        Log.error(cls.sh_eq(key, value), stacklevel=3)

    @classmethod
    def critical(cls, key: Any, value: Any) -> None:
        Log.critical(cls.sh_eq(key, value), stacklevel=3)


class LogDic:

    @classmethod
    def debug(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.debug(key, value)

    @classmethod
    def info(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.info(key, value)

    @classmethod
    def warning(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.warning(key, value)

    @classmethod
    def error(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.error(key, value)

    @classmethod
    def critical(cls, dic: TyDic) -> None:
        for key, value in dic.items():
            LogEq.critical(key, value)


class Log:

    sw_init: bool = False
    sw_debug: bool = False
    log: TyLogger = logging.getLogger('dummy_logger')

    @classmethod
    def debug(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.debug(*args, **kwargs)

    @classmethod
    def info(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.info(*args, **kwargs)

    @classmethod
    def warning(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.warning(*args, **kwargs)

    @classmethod
    def error(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.error(*args, **kwargs)

    @classmethod
    def critical(cls, *args, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs['stacklevel'] = kwargs.get('stacklevel', 2)
        cls.log.critical(*args, **kwargs)

    @classmethod
    def init(cls, **kwargs) -> None:
        """Set static variable log level in log configuration handlers
        """
        if cls.sw_init:
            return
        cls.sw_init = True
        _d_log_cfg: TyDic = Utils.sh_d_log_cfg(kwargs, cls.log)
        logging.config.dictConfig(_d_log_cfg)
        _log_type = kwargs.get('log_type', 'std')
        cls.log = logging.getLogger(_log_type)
        cls.sw_debug = kwargs.get('sw_debug', False)

    @classmethod
    def sh(cls, **kwargs) -> Any:
        if cls.sw_init:
            return cls
            # return cls.log
        cls.init(**kwargs)
        return cls
