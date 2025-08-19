class ClientError(Exception):
    message = 'HTTP{status_code} {method} {uri} \n<- {data} \n-> {result}'

    def __init__(
        self,
        method: str,
        uri: str,
        data: dict | None,
        result: dict | None,
        status_code: int
    ) -> None:

        self.method = method
        self.uri = uri
        self.data = data
        self.result = result
        self.status_code = status_code

        super().__init__(self.message.format(
            method=method,
            uri=uri,
            data=data,
            status_code=status_code,
            result=result,
        ))


class UnauthorizedError(ClientError):
    message = '{method} {uri} \n-> {result}'


class NoAccessError(ClientError):
    message = '{method} {uri} \n<- {data} \n-> {result}'


class InputDataError(ClientError):
    message = '{method} {uri} \n<- {data} \n-> {result}'


class MethodError(ClientError):
    message = '{method} undefined for {uri}'


class NotFoundError(ClientError):
    message = 'NotFound {uri}'


class TooManyRequestsError(ClientError):
    message = '{method} {uri}\n-> {result}'


class ServerError(ClientError):
    message = '{method} {uri} > HTTP{status_code}'


class RedirectError(ClientError):
    message = '{method} {uri}'
