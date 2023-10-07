class FinnotechException(Exception):
    def __init__(self, message, logger):
        """
        :param message: error message
        """
        self.message = message
        logger.error(f"Finnotech api error: {message}")


class FinnotechHttpException(Exception):
    def __init__(self, response, logger, underlying_exception: Exception = None):
        """
        :param response: return value of `requests` http call
        """
        message = response.content.decode()
        if underlying_exception is not None:
            message += f"\n Underlying exception: {underlying_exception}"
        self.message = message
        self.status_code = response.status_code

        try:
            self.data = response.json()
        except ValueError:
            self.data = None

        logger.error(
            f"Finnotech http api status code: {self.status_code}, error: {message}",
            extra={"status": self.status_code, "data": self.data},
        )
