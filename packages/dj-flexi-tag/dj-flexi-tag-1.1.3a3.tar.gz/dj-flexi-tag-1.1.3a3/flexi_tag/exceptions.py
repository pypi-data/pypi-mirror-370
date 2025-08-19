from django.utils.encoding import smart_str

from flexi_tag import codes


class ProjectBaseException(Exception):
    code = codes.undefined

    def __init__(self, *args, **kwargs):
        if not isinstance(self.code, dict):
            raise Exception("parameter type must be a dict")
        code = self.code.get("code", "undefined")
        message = getattr(self.codes, "%s" % code)
        self.message = message.get("en")
        self.obj = kwargs.get("obj", None)
        self.target = kwargs.get("target", None)
        self.params = kwargs.get("params")
        if self.params and isinstance(self.params, dict):
            self.message = smart_str(self.message).format(**self.params)
        elif self.params and isinstance(self.params, (list, set, tuple)):
            self.message = smart_str(self.message).format(*self.params)

        Exception.__init__(self, smart_str("{0}:{1}").format(code, self.message))

    def __new__(cls, *args, **kwargs):
        obj = super(ProjectBaseException, cls).__new__(cls)
        obj.__init__(*args, **kwargs)
        try:
            getattr(cls.codes, "%s" % obj.code.get("code"))
        except AttributeError:
            pass
        return obj

    @property
    def codes(self):
        return codes


class TagValidationException(ProjectBaseException):
    code = codes.tag_100_1


class TagNotFoundException(ProjectBaseException):
    code = codes.tag_100_2


class TagNotDefinedException(ProjectBaseException):
    code = codes.tag_100_3


class ObjectIDsNotDefinedException(ProjectBaseException):
    code = codes.tag_100_4
