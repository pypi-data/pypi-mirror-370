class RateLimitError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class CredentialsError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class NotFoundError(Exception):
    pass


class DeliveryFailureError(Exception):
    pass
