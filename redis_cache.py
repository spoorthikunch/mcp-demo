import json
import redis
from case_manager import get_case
import os
r=redis.Redis(
    host=os.getenv("REDIS_HOST","localhost"),
    port=os.getenv("REDIS_PORT","6379"),
    decode_responses=True,
)

def set_cache(key:str,value:dict,ttl:int=60):
    return r.set(key,json.dumps(value),ex=ttl)
def get_cache(key:str):
    value=r.get(key)
    if value is None:
        return None
    return json.loads(value)
def delete_cache(key:str):
    return r.delete(key)

def get_case_cached(case_id:str):
    key=f"case:{case_id}"
    cache_case=get_cache(key)
    if cache_case is not None:
        print("Cache Hit")
        return cache_case
    print("Cache Miss")
    case=get_case(case_id)
    if case is None:
        return None
    set_cache(key,case,ttl=60)
    return case






    
