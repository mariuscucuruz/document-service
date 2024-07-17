class CustomException(Exception):
    def __init__(self, message="there has been an unknown exception"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{type(self).__name__}: {self.message}"


class UnrecognizedTableException(CustomException):
    def __init__(self, message="table not recognised"):
        self.message = message
        super().__init__(self.message)


class MissingMandatoryFieldsException(CustomException):
    def __init__(self, message="mandatory input fields missing"):
        self.message = message
        super().__init__(self.message)


class MethodException(CustomException):
    def __init__(self, message="method not allowed"):
        self.message = message
        super().__init__(self.message)


class DbException(CustomException):
    def __init__(self, message="there was an error processing request"):
        self.message = message
        super().__init__(self.message)


class UnsuccessfulResponse(CustomException):
    @classmethod
    def unrecognized(
        cls, message="unable to process request, query or mutation not recognised"
    ):
        return {"status_code": 422, "message": message}

    @classmethod
    def graphql_syntax_error(
        cls, message="unable to process request, graphql syntax error"
    ):
        return {"status_code": 400, "message": message}


    @classmethod
    def empty_db_response(cls, message="there was an error processing request"):
        return {"status_code": 500, "message": message}


    @classmethod
    def failed_mandatory_checks(
        cls, message="unable to process request, mandatory fields missing"
    ):
        return {"status_code": 422, "message": message}


    @classmethod
    def table_name_unrecognised(
        cls,
        message="unable to process request, mutation does not contain a recognised table name",
    ):
        return {"status_code": 422, "message": message}


    @classmethod
    def unknown_exception(cls, message="an Exception has been raised"):
        return {"status_code": 500, "message": message}


    @classmethod
    def method_not_allowed(cls, message="method not allowed"):
        return {"status_code": 405, "message": message}


    @classmethod
    def attribute_error(
        cls, message="unable to extract necessary attributes from request"
    ):
        return {"status_code": 422, "message": message}


    @classmethod
    def id_validation_error(cls, message="unable to validate ID"):
        return {"status_code": 403, "message": message}


    @classmethod
    def id_not_found_error(cls, message="ID not found"):
        return {"status_code": 404, "message": message}


    @classmethod
    def duplication_error(cls, message="entry already exists"):
        return {"status_code": 409, "message": message}


    @classmethod
    def timeout_error(cls, message="request timed out"):
        return {"status_code": 408, "message": message}
