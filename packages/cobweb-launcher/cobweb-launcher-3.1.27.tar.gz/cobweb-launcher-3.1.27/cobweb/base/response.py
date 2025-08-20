from typing import Any


class Response:

    def __init__(
            self,
            seed,
            response,
            **kwargs
    ):
        self.seed = seed
        self.response = response

        for k, v in kwargs.items():
            self.__setattr__(k, v)

    @property
    def to_dict(self):
        _dict = self.__dict__.copy()
        _dict.update(self.seed.to_dict)
        _dict.pop('seed')
        _dict.pop('response')
        return _dict

    def __getattr__(self, name: str) -> Any:
        """动态获取未定义的属性，返回 None"""
        return None

    def __getitem__(self, key: str) -> Any:
        """支持字典式获取属性"""
        return getattr(self, key, None)
