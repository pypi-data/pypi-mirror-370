#!/usr/bin/env python3


import time
import pytz
import datetime


class TimeUtils:
    
    @staticmethod
    def get_timestamp(now: bool=True) -> int:
        '''
        获取时间戳
        
        Args:
            now (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        '''
        if now:
            return int(time.time())
        else:
            return int(time.time() * 1000)
    
    @staticmethod
    def get_time_object(now: bool=True):
        '''
        获取当前时间, 加入了时区信息, 简单是存储在 Mongo 中时格式为 ISODate

        Returns:
            current_time(class): 时间, 格式: 2024-04-23 16:48:11.591589+08:00
        '''
        if now:
            return datetime.datetime.now(pytz.timezone('Asia/Shanghai'))