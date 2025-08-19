import pickle

import redis


# Write a class that extends redis.Redis and add the methods you need to override set and get to serialize and deserialize using pickle
class FSAIRedis(redis.Redis):
    def pset(self, name, value, *args, **kwargs):
        return super().set(name, pickle.dumps(value), *args, **kwargs)

    def pget(self, name, *args, **kwargs):
        value = super().get(name, *args, **kwargs)
        if value is None:
            return value
        return pickle.loads(value)
