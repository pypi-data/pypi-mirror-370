class HandlerNotFoundError(Exception):

    def __init__(self, handler_name: str):
        super().__init__(handler_name)


class ExecutionError(Exception):

    def __init__(self, *args):
        super().__init__(*args)


class PayloadParseError(Exception):

    def __init__(self, *args):
        super().__init__(*args)


class ResponseParseError(Exception):

    def __init__(self, *args):
        super().__init__(*args)


class HandlerAlreadyExistsError(Exception):

    def __init__(self, *args):
        super().__init__(*args)
