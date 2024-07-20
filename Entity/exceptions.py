class CustomException(Exception):
    """
    CustomException class exceptions
    """
    def __init__(self, message="there has been an unknown exception"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{type(self).__name__}: {self.message}"


class UnrecognizedTableException(CustomException):
    """
    UnrecognizedTableException class exceptions
    """
    def __init__(self, message="table not recognised"):
        self.message = message
        super().__init__(self.message)


class MissingMandatoryFieldsException(CustomException):
    """
    MissingMandatoryFieldsException class exceptions
    """
    def __init__(self, message="mandatory input fields missing"):
        self.message = message
        super().__init__(self.message)


class MethodException(CustomException):
    """
    MethodException class exceptions
    """
    def __init__(self, message="method not allowed"):
        self.message = message
        super().__init__(self.message)


class DbException(CustomException):
    """
    DbException class exceptions
    """
    def __init__(self, message="there was an error processing request"):
        self.message = message
        super().__init__(self.message)


class UnsuccessfulResponse(CustomException):
    """
    UnsuccessfulResponse class exceptions
    """
    @classmethod
    def unrecognized(
        cls, message="unable to process request, query or mutation not recognised"
    ):
        """
        Unrecognized class exceptions
        """
        return {"status_code": 422, "message": message}

    @classmethod
    def graphql_syntax_error(
        cls, message="unable to process request, graphql syntax error"
    ):
        """
        GraphqlSyntaxError class exceptions
        """
        return {"status_code": 400, "message": message}


    @classmethod
    def empty_db_response(cls, message="there was an error processing request"):
        """
        EmptyDbResponse class exceptions
        """
        return {"status_code": 500, "message": message}


    @classmethod
    def failed_mandatory_checks(
        cls, message="unable to process request, mandatory fields missing"
    ):
        """
        FailedMandatoryChecks class exceptions
        """
        return {"status_code": 422, "message": message}


    @classmethod
    def table_name_unrecognised(
        cls,
        message="unable to process request, mutation does not contain a recognised table name",
    ):
        """
        TableNameUnrecognised class exceptions
        """
        return {"status_code": 422, "message": message}


    @classmethod
    def unknown_exception(cls, message="an Exception has been raised"):
        """
        UnknownException class exceptions
        """
        return {"status_code": 500, "message": message}


    @classmethod
    def method_not_allowed(cls, message="method not allowed"):
        """
        MethodNotAllowed class exceptions
        """
        return {"status_code": 405, "message": message}


    @classmethod
    def attribute_error(
        cls, message="unable to extract necessary attributes from request"
    ):
        """
        AttributeError class exceptions
        """
        return {"status_code": 422, "message": message}


    @classmethod
    def id_validation_error(cls, message="unable to validate ID"):
        """
        IdValidationError class exceptions
        """
        return {"status_code": 403, "message": message}


    @classmethod
    def id_not_found_error(cls, message="ID not found"):
        """
        IdNotFoundError class exceptions
        """
        return {"status_code": 404, "message": message}


    @classmethod
    def duplication_error(cls, message="entry already exists"):
        """
        DuplicationError class exceptions
        """
        return {"status_code": 409, "message": message}


    @classmethod
    def timeout_error(cls, message="request timed out"):
        """
        TimeoutError class exceptions
        """
        return {"status_code": 408, "message": message}
