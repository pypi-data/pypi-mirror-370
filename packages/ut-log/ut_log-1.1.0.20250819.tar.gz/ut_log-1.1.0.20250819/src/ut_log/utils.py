from typing import Any
from collections.abc import Callable

import os
import time
import calendar
from datetime import datetime
import pytz
import logging
import logging.config
from logging import Logger
import psutil

from ut_ioc.jinja2_ import Jinja2_
from ut_pac.pacs import Pacs

TyAny = Any
TyCallable = Callable[..., Any]
TyDateTime = datetime
TyTimeStamp = int
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyDir = str
TyPath = str
TyLogger = Logger
TyStr = str

TnAny = None | Any
TnArr = None | TyArr
TnBool = None | bool
TnDic = None | TyDic
TnTimeStamp = None | TyTimeStamp
TnDateTime = None | TyDateTime
TnStr = None | TyStr


class Utils:

    @staticmethod
    def sh_username(kwargs: TyDic) -> str:
        """
        Show username
        """
        _log_type = kwargs.get('log_type', 'std')
        if _log_type == "usr":
            _username: str = psutil.Process().username()
        else:
            _username = ''
        return _username

    @classmethod
    def sh_dir_run(cls, kwargs: TyDic) -> TyPath:
        """
        Show dir_run
        """
        _app_data: str = kwargs.get('app_data', '/data')
        _tenant: str = kwargs.get('tenant', '')
        _cls_app = kwargs.get('cls_app')
        _package = _cls_app.__module__.split(".")[0]
        _username = cls.sh_username(kwargs)
        _cmd: TyStr = kwargs.get('cmd', '')
        _path: TyPath = os.path.join(
                _app_data, _tenant, 'RUN', _package, _username, _cmd)
        return _path

    @classmethod
    def sh_d_dir_run(cls, kwargs) -> TyDic:
        """
        Read log file path with jinja2
        """
        _dir_run = cls.sh_dir_run(kwargs)
        if kwargs.get('log_sw_single_dir', True):
            return {
                    'dir_run_debs': f"{_dir_run}/debs",
                    'dir_run_infs': f"{_dir_run}/logs",
                    'dir_run_wrns': f"{_dir_run}/logs",
                    'dir_run_errs': f"{_dir_run}/logs",
                    'dir_run_crts': f"{_dir_run}/logs",
            }
        return {
                'dir_run_debs': f"{_dir_run}/debs",
                'dir_run_infs': f"{_dir_run}/infs",
                'dir_run_wrns': f"{_dir_run}/wrns",
                'dir_run_errs': f"{_dir_run}/errs",
                'dir_run_crts': f"{_dir_run}/crts",
        }

    @classmethod
    def sh_path_log_cfg(cls_log, kwargs: TyDic, log) -> Any:
        """ show directory
        """
        _log_type = kwargs.get('log_type', 'std')
        _cls_app = kwargs.get('cls_app')
        _log_package = cls_log.__module__.split(".")[0]
        _app_package = _cls_app.__module__.split(".")[0]
        _packages = [_app_package, _log_package]
        _path = os.path.join('cfg', f"log.{_log_type}.yml")
        _path = Pacs.sh_path_by_path(_packages, _path, log)
        return _path

    @staticmethod
    def sh_calendar_ts(kwargs) -> Any:
        """Set static variable log level in log configuration handlers
        """
        _log_ts_type = kwargs.get('log_ts_type', 'ts')
        match _log_ts_type:
            case 'ts':
                return calendar.timegm(time.gmtime())
            case 'dt':
                # Example Unix timestamp (seconds since 1970-01-01 00:00:00 UTC)
                _timestamp = calendar.timegm(time.gmtime())
                # Convert timestamp to a naive datetime object in UTC
                _utc_time = datetime.utcfromtimestamp(_timestamp)
                # Localize the datetime object to UTC
                _utc_time = pytz.utc.localize(_utc_time)
                # Convert to a specific timezone (e.g., Europe/Berlin)
                _timezone = pytz.timezone('Europe/Berlin')
                localized_time = _utc_time.astimezone(_timezone)
                return localized_time
            case _:
                return calendar.timegm(time.gmtime())

    @staticmethod
    def sh_level(kwargs) -> int:
        _sw_debug = kwargs.get('sw_debug', False)
        if _sw_debug:
            return logging.DEBUG
        else:
            return logging.INFO

    @staticmethod
    def sh_app_module(kwargs) -> TyStr:
        _cls_app = kwargs.get('cls_app')
        _a_app_pacmod = _cls_app.__module__.split(".")
        if len(_a_app_pacmod) > 1:
            _module: TyStr = _a_app_pacmod[1]
        else:
            _module = _a_app_pacmod[0]
        return _module

    @classmethod
    def sh_d_log_cfg(cls, kwargs: TyDic, log) -> TyDic:
        """Read log file path with jinja2
        """
        _d_dir_run = cls.sh_d_dir_run(kwargs)
        if kwargs.get('log_sw_mkdirs', True):
            aopath: TyArr = list(_d_dir_run.values())
            for _path in aopath:
                os.makedirs(_path, exist_ok=True)

        _path_log_cfg = cls.sh_path_log_cfg(kwargs, log)
        _module = cls.sh_app_module(kwargs)
        _pid = os.getpid()
        _ts = cls.sh_calendar_ts(kwargs)

        _d_log_cfg: TyDic = Jinja2_.read(
                _path_log_cfg, module=_module, pid=_pid, ts=_ts, **_d_dir_run)
        _level = cls.sh_level(kwargs)
        _log_type = kwargs.get('log_type', 'std')
        logger_name = _log_type
        _d_log_cfg['handlers'][f"{logger_name}_debug_console"]['level'] = _level
        _d_log_cfg['handlers'][f"{logger_name}_debug_file"]['level'] = _level

        return _d_log_cfg
