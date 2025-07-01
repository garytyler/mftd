class _CachedClassProperty:
    def __init__(self, f):
        self.f, self.name = f, f.__name__

    def __get__(self, obj, cls):
        if self.name not in cls.__dict__:
            setattr(cls, self.name, self.f(cls))
        return cls.__dict__[self.name]


cached_classproperty = _CachedClassProperty
