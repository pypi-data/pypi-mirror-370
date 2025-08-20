# -*- coding:utf-8 -*-


import json,datetime
from typing import Any

class JSON_util(json.JSONEncoder):
    def default(self, obj: Any) -> Any:  
        if isinstance(obj, datetime.datetime):  return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, bytes): return str(obj, encoding='utf-8')
        elif isinstance(obj, int): return int(obj)
        elif isinstance(obj, float):return float(obj) 
        elif hasattr(obj,"__dict__"):  return obj.__dict__ 
        return None 
    