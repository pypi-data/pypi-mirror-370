class ImageParseException(Exception):
    pass


class ExtraFilesNotFoundExcpetion(Exception):
    pass


class WrongFileExtensionException(Exception):
    pass


class ExceptionSwallowedByNativeLibraryError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "We suspect that an exception has been asynchronously raised inside a native library and then swallowed, "
            "we were unable to retrieve the contents of that exception."
        )


class StreamLengthError(Exception):
    pass


class InvalidPepperLenError(Exception):
    def __init__(self, length: int) -> None:
        super().__init__(f"The pepper should be 32 characters long. The current pepper is {length} characters long")


class InvalidPepperType(Exception):
    def __init__(self, pepper_type: type):
        super().__init__(f"The pepper should be a string. Currently pepper is a {pepper_type}.")
