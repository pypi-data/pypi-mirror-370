from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.module_loading import import_string

from flexi_tag import codes


def get_base_exception_class():
    """
    Get the base exception class from settings or use default.

    Returns:
        class: The base exception class to use for flexi-tag exceptions.
               Can be configured via FLEXI_TAG_BASE_EXCEPTION_CLASS setting.
    """
    base_exception_class_path = getattr(
        settings,
        "FLEXI_TAG_BASE_EXCEPTION_CLASS",
        "flexi_tag.exceptions.DefaultProjectBaseException",
    )

    if base_exception_class_path == "flexi_tag.exceptions.DefaultProjectBaseException":
        # Return the default class directly to avoid circular import
        return DefaultProjectBaseException
    else:
        # Import user's custom base exception class
        return import_string(base_exception_class_path)


class DefaultProjectBaseException(Exception):
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
        obj = super(DefaultProjectBaseException, cls).__new__(cls)
        obj.__init__(*args, **kwargs)
        try:
            getattr(cls.codes, "%s" % obj.code.get("code"))
        except AttributeError:
            pass
        return obj

    @property
    def codes(self):
        return codes


# Dynamic base class assignment
ProjectBaseException = get_base_exception_class()


# Tag-specific exceptions inherit from the dynamic base
class TagValidationException(ProjectBaseException):
    code = codes.tag_100_1

    def __init__(self, *args, **kwargs):
        # Extract flexi-tag specific parameters
        self.name = kwargs.pop("name", None)

        # Initialize our exception logic
        if not isinstance(self.code, dict):
            raise ValueError("parameter type must be a dict")
        code = self.code.get("code", "undefined")
        message = getattr(self.codes, "%s" % code)
        self.message = message.get("en")
        self.obj = kwargs.get("obj", None)
        self.target = kwargs.get("target", None)
        self.params = kwargs.get("params")

        # Handle name parameter for message formatting
        if self.name:
            self.params = {"name": self.name}

        if self.params and isinstance(self.params, dict):
            self.message = smart_str(self.message).format(**self.params)
        elif self.params and isinstance(self.params, (list, set, tuple)):
            self.message = smart_str(self.message).format(*self.params)

        formatted_message = smart_str("{0}:{1}").format(code, self.message)

        # Call parent class with the formatted message
        super().__init__(formatted_message, *args, **kwargs)

    @property
    def codes(self):
        return codes


class TagNotFoundException(ProjectBaseException):
    code = codes.tag_100_2

    def __init__(self, *args, **kwargs):
        # Extract flexi-tag specific parameters
        self.name = kwargs.pop("name", None)

        # Initialize our exception logic
        if not isinstance(self.code, dict):
            raise ValueError("parameter type must be a dict")
        code = self.code.get("code", "undefined")
        message = getattr(self.codes, "%s" % code)
        self.message = message.get("en")
        self.obj = kwargs.get("obj", None)
        self.target = kwargs.get("target", None)
        self.params = kwargs.get("params")

        # Handle name parameter for message formatting
        if self.name:
            self.params = {"name": self.name}

        if self.params and isinstance(self.params, dict):
            self.message = smart_str(self.message).format(**self.params)
        elif self.params and isinstance(self.params, (list, set, tuple)):
            self.message = smart_str(self.message).format(*self.params)

        formatted_message = smart_str("{0}:{1}").format(code, self.message)

        # Call parent class with the formatted message
        super().__init__(formatted_message, *args, **kwargs)

    @property
    def codes(self):
        return codes


class TagNotDefinedException(ProjectBaseException):
    code = codes.tag_100_3

    def __init__(self, *args, **kwargs):
        # Initialize our exception logic
        if not isinstance(self.code, dict):
            raise ValueError("parameter type must be a dict")
        code = self.code.get("code", "undefined")
        message = getattr(self.codes, "%s" % code)
        self.message = message.get("en")

        formatted_message = smart_str("{0}:{1}").format(code, self.message)

        # Call parent class with the formatted message
        super().__init__(formatted_message, *args, **kwargs)

    @property
    def codes(self):
        return codes


class ObjectIDsNotDefinedException(ProjectBaseException):
    code = codes.tag_100_4

    def __init__(self, *args, **kwargs):
        # Initialize our exception logic
        if not isinstance(self.code, dict):
            raise ValueError("parameter type must be a dict")
        code = self.code.get("code", "undefined")
        message = getattr(self.codes, "%s" % code)
        self.message = message.get("en")

        formatted_message = smart_str("{0}:{1}").format(code, self.message)

        # Call parent class with the formatted message
        super().__init__(formatted_message, *args, **kwargs)

    @property
    def codes(self):
        return codes
