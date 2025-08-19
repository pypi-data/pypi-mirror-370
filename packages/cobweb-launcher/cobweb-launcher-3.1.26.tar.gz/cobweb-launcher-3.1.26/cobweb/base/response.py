

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

