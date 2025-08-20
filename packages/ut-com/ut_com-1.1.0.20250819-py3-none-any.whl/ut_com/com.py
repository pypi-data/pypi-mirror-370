# import os
import time
import calendar
from datetime import datetime

import ut_arr.aoeq.AoEq as AoEq
import ut_log.log.Log as Log

from typing import Any
TyAny = Any
TyDateTime = datetime
TyTimeStamp = int
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]

TnAny = None | Any
TnArr = None | TyArr
TnDic = None | TyDic
TnTimeStamp = None | TyTimeStamp
TnDateTime = None | TyDateTime
TnStr = None | str


class Com:
    """
    Communication Class
    """
    cmd: TnStr = None
    sw_init: bool = False

    com_a_mod = None
    com_pac = None
    app_a_mod = None
    app_pac = None
    tenant: TnStr = None

    ts: TnTimeStamp
    d_timer: TyDic = {}

    Log: Any = None
    cfg: TnDic = None
    # App: Any = None
    # Exit: Any = None

    @classmethod
    def init(cls, kwargs: TyDic):
        # def init(cls, cls_app, kwargs: TyDic):
        """
        initialise static variables of Com class
        """
        if cls.sw_init:
            return
        cls.sw_init = True
        cls.cmd = kwargs.get('cmd')
        cls.com_a_mod = cls.__module__.split(".")
        cls.com_pac = cls.com_a_mod[0]
        _cls_app = kwargs.get('cls_app')
        cls.app_a_mod = _cls_app.__module__.split(".")
        cls.app_pac = cls.app_a_mod[0]
        cls.tenant = kwargs.get('tenant')
        cls.ts = calendar.timegm(time.gmtime())

        cls.Log = Log.sh(**kwargs)
        # cls.Cfg = Cfg.sh(cls, **kwargs)
        # cls.App = App.sh(cls, **kwargs)
        # cls.Exit = Exit.sh(**kwargs)

    @classmethod
    def sh_kwargs(cls, cls_app, cls_parms, *args) -> TyDic:
        """
        show keyword arguments
        """
        _kwargs: TyDic = AoEq.sh_d_eq(*args, d_parms=cls_parms.d_eq)
        _kwargs['cls_app'] = cls_app
        _kwargs['com'] = cls

        cls.init(_kwargs)
        return _kwargs
