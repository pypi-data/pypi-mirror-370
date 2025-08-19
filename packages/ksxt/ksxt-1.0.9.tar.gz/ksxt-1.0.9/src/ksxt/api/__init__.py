import types


class Entry:
    def __init__(self, security_type, path, config):
        # equity, derivative, oversea_equity, oversea_derivative
        self.security_type = security_type

        # function key
        self.path = path

        self.config = config

        def unbound_method(_self, params={}):
            return _self.request(self.path, self.security_type, params, config=self.config)

        self.unbound_method = unbound_method

    def __get__(self, instance, owner):
        if instance is None:
            return self.unbound_method
        else:
            return types.MethodType(self.unbound_method, instance)

    def __set_name__(self, owner, name):
        self.name = name
