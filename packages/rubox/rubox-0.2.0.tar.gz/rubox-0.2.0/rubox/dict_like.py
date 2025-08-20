# rubox/dict_like.py

from dataclasses import asdict, fields
from typing import Any, Dict

class DictLike:
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        for field in fields(self):
            value = getattr(self, field.name)
            
            if value is None:
                continue
                
            if isinstance(value, list):
                if not value:
                    continue
                if hasattr(value[0], 'to_dict'):
                    result[field.name] = [item.to_dict() for item in value]
                else:
                    result[field.name] = value
            elif hasattr(value, 'to_dict'):
                result[field.name] = value.to_dict()
            else:
                result[field.name] = value
                
        return result
    
    def find_key(self, key: str) -> Any:
        def _search(obj, target_key):
            if hasattr(obj, 'to_dict'):
                data = obj.to_dict()
            elif isinstance(obj, dict):
                data = obj
            else:
                return None
                
            if target_key in data:
                return data[target_key]
                
            for value in data.values():
                if isinstance(value, (dict, DictLike)):
                    result = _search(value, target_key)
                    if result is not None:
                        return result
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, (dict, DictLike)):
                            result = _search(item, target_key)
                            if result is not None:
                                return result
            return None
            
        return _search(self, key)