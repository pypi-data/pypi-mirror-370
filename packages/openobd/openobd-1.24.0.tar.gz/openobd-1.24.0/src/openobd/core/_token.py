#!/usr/bin/env python3
import time


TOKEN_EXPIRY_BUFFER_SECONDS = 30    # How many seconds before expiry a new token should be requested


class Token:
    """
    A generic token object that automatically refreshes its token when it is needed and near its expiry time.
    """

    def __init__(self, request_function, lifetime_seconds):
        self._value = None
        self.expiry_time = 0

        # Constants
        self.request_function = request_function
        self.lifetime_seconds = lifetime_seconds

    def get_value(self):
        # If the token has (almost) expired, request a new one
        if time.time() >= (self.expiry_time - TOKEN_EXPIRY_BUFFER_SECONDS):
            self.set_value(self.request_function())

        return self._value

    def set_value(self, value):
        # Sets the new token value and resets its expiry time
        self._value = value
        self.expiry_time = time.time() + self.lifetime_seconds
