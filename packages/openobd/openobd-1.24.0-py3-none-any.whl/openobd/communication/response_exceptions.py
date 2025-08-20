from openobd.core.exceptions import OpenOBDStreamException


class ResponseException(OpenOBDStreamException):
    """
    Base class for all exceptions that can be raised during vehicle communication.
    """

    def __init__(self, request="", response="", request_id=0, response_id=0, **kwargs):
        self.request = request
        self.response = response
        self.request_id = request_id
        self.response_id = response_id
        super().__init__(**kwargs)

    def __str__(self):
        exception_info = self.__class__.__name__

        if self.request_id:
            exception_info += f" ({self.request_id:X}"
            if self.response_id:
                exception_info += f" -> {self.response_id:X}"
            exception_info += ")"
        if self.request:
            exception_info += f" request: {self.request}"
        if self.response:
            exception_info += f" response: {self.response}"

        return exception_info


class NoResponseException(ResponseException):
    """
    Did not receive a response from the vehicle in the specified time.
    """
    pass


class InvalidResponseException(ResponseException):
    """
    The response received from the vehicle does not have the correct format.
    """
    pass


class NegativeResponseException(ResponseException):
    """
    Base class for all exceptions that are raised because of a negative response received from the vehicle.
    """
    pass


class GeneralRejectException(NegativeResponseException):
    pass


class ServiceNotSupportedException(NegativeResponseException):
    pass


class SubFunctionNotSupportedException(NegativeResponseException):
    """
    For KWP2000, this exception means "subFunctionNotSupported-invalidFormat" according to ISO 14230-3:1996.
    """
    pass


class IncorrectMessageLengthOrInvalidFormatException(NegativeResponseException):
    pass


class ResponseTooLongException(NegativeResponseException):
    pass


class BusyRepeatRequestException(NegativeResponseException):
    pass


class ConditionsNotCorrectException(NegativeResponseException):
    """
    For KWP2000, this exception means "conditionsNotCorrect or requestSequenceError" according to ISO 14230-3:1996.
    """
    pass


class RequestSequenceErrorException(NegativeResponseException):
    pass


class NoResponseFromSubnetComponentException(NegativeResponseException):
    pass


class FailurePreventsExecutionOfRequestedActionException(NegativeResponseException):
    pass


class RequestOutOfRangeException(NegativeResponseException):
    pass


class SecurityAccessDeniedException(NegativeResponseException):
    pass


class AuthenticationRequiredException(NegativeResponseException):
    pass


class InvalidKeyException(NegativeResponseException):
    pass


class ExceedNumberOfAttemptsException(NegativeResponseException):
    pass


class RequiredTimeDelayNotExpiredException(NegativeResponseException):
    pass


class SecureDataTransmissionRequiredException(NegativeResponseException):
    pass


class SecureDataTransmissionNotAllowedException(NegativeResponseException):
    pass


class SecureDataVerificationFailedException(NegativeResponseException):
    pass


class CertificateVerificationFailedException(NegativeResponseException):
    """
    Base class for certificate verification negative response codes.
    """
    pass


class CertificateVerificationFailedInvalidTimePeriodException(CertificateVerificationFailedException):
    """
    For KWP2000, this exception means "uploadNotAccepted" according to ISO 14230-3:1996.
    """
    pass


class CertificateVerificationFailedInvalidSignatureException(CertificateVerificationFailedException):
    """
    For KWP2000, this exception means "improperUploadType" according to ISO 14230-3:1996.
    """
    pass


class CertificateVerificationFailedInvalidChainOfTrustException(CertificateVerificationFailedException):
    """
    For KWP2000, this exception means "can'tUploadFromSpecifiedAddress" according to ISO 14230-3:1996.
    """
    pass


class CertificateVerificationFailedInvalidTypeException(CertificateVerificationFailedException):
    """
    For KWP2000, this exception means "can'tUploadNumberOfBytesRequested" according to ISO 14230-3:1996.
    """
    pass


class CertificateVerificationFailedInvalidFormatException(CertificateVerificationFailedException):
    pass


class CertificateVerificationFailedInvalidContentException(CertificateVerificationFailedException):
    pass


class CertificateVerificationFailedInvalidScopeException(CertificateVerificationFailedException):
    pass


class CertificateVerificationFailedInvalidCertificateRevokedException(CertificateVerificationFailedException):
    pass


class OwnershipVerificationFailedException(CertificateVerificationFailedException):
    pass


class ChallengeCalculationFailedException(CertificateVerificationFailedException):
    pass


class SettingAccessRightsFailedException(CertificateVerificationFailedException):
    pass


class SessionKeyCreationDerivationFailedException(CertificateVerificationFailedException):
    pass


class ConfigurationDataUsageFailedException(CertificateVerificationFailedException):
    pass


class DeAuthenticationFailedException(CertificateVerificationFailedException):
    pass


class UploadDownloadNotAcceptedException(NegativeResponseException):
    pass


class TransferDataSuspendedException(NegativeResponseException):
    """
    For KWP2000, this exception means "transferSuspended" according to ISO 14230-3:1996.
    """
    pass


class GeneralProgrammingFailureException(NegativeResponseException):
    """
    For KWP2000, this exception means "transferAborted" according to ISO 14230-3:1996.
    """
    pass


class WrongBlockSequenceCounterException(NegativeResponseException):
    pass


class RequestCorrectlyReceivedResponsePendingException(NegativeResponseException):
    pass


class SubFunctionNotSupportedInActiveSessionException(NegativeResponseException):
    pass


class ServiceNotSupportedInActiveSessionException(NegativeResponseException):
    pass


class SpecificConditionNotCorrectException(NegativeResponseException):
    """
    Base class for specific conditions negative response codes.
    """
    pass


class RpmTooHighException(SpecificConditionNotCorrectException):
    pass


class RpmTooLowException(SpecificConditionNotCorrectException):
    pass


class EngineIsRunningException(SpecificConditionNotCorrectException):
    pass


class EngineIsNotRunningException(SpecificConditionNotCorrectException):
    pass


class EngineRunTimeTooLowException(SpecificConditionNotCorrectException):
    pass


class TemperatureTooHighException(SpecificConditionNotCorrectException):
    pass


class TemperatureTooLowException(SpecificConditionNotCorrectException):
    pass


class VehicleSpeedTooHighException(SpecificConditionNotCorrectException):
    pass


class VehicleSpeedTooLowException(SpecificConditionNotCorrectException):
    pass


class ThrottlePedalTooHighException(SpecificConditionNotCorrectException):
    pass


class ThrottlePedalTooLowException(SpecificConditionNotCorrectException):
    pass


class TransmissionRangeNotInNeutralException(SpecificConditionNotCorrectException):
    pass


class TransmissionRangeNotInGearException(SpecificConditionNotCorrectException):
    pass


class BrakeSwitchesNotClosedException(SpecificConditionNotCorrectException):
    pass


class ShifterLeverNotInParkException(SpecificConditionNotCorrectException):
    pass


class TorqueConverterClutchLockedException(SpecificConditionNotCorrectException):
    pass


class VoltageTooHighException(SpecificConditionNotCorrectException):
    pass


class VoltageTooLowException(SpecificConditionNotCorrectException):
    pass


class ResourceTemporarilyNotAvailableException(SpecificConditionNotCorrectException):
    pass


class UnknownNegativeResponseException(NegativeResponseException):
    pass


# Based on ISO 14229-1:2020
negative_response_code_exceptions = {
    # 01-0F: ISOSAEReserved
    "10": GeneralRejectException,
    "11": ServiceNotSupportedException,
    "12": SubFunctionNotSupportedException,
    "13": IncorrectMessageLengthOrInvalidFormatException,
    "14": ResponseTooLongException,
    # 15-20: ISOSAEReserved
    "21": BusyRepeatRequestException,
    "22": ConditionsNotCorrectException,
    # 23: ISOSAEReserved
    "24": RequestSequenceErrorException,
    "25": NoResponseFromSubnetComponentException,
    "26": FailurePreventsExecutionOfRequestedActionException,
    # 27-30: ISOSAEReserved
    "31": RequestOutOfRangeException,
    # 32: ISOSAEReserved
    "33": SecurityAccessDeniedException,
    "34": AuthenticationRequiredException,
    "35": InvalidKeyException,
    "36": ExceedNumberOfAttemptsException,
    "37": RequiredTimeDelayNotExpiredException,
    "38": SecureDataTransmissionRequiredException,
    "39": SecureDataTransmissionNotAllowedException,
    "3A": SecureDataVerificationFailedException,
    # 3B-4F: ISOSAEReserved
    "50": CertificateVerificationFailedInvalidTimePeriodException,
    "51": CertificateVerificationFailedInvalidSignatureException,
    "52": CertificateVerificationFailedInvalidChainOfTrustException,
    "53": CertificateVerificationFailedInvalidTypeException,
    "54": CertificateVerificationFailedInvalidFormatException,
    "55": CertificateVerificationFailedInvalidContentException,
    "56": CertificateVerificationFailedInvalidScopeException,
    "57": CertificateVerificationFailedInvalidCertificateRevokedException,
    "58": OwnershipVerificationFailedException,
    "59": ChallengeCalculationFailedException,
    "5A": SettingAccessRightsFailedException,
    "5B": SessionKeyCreationDerivationFailedException,
    "5C": ConfigurationDataUsageFailedException,
    "5D": DeAuthenticationFailedException,
    # 5E-6F: ISOSAEReserved
    "70": UploadDownloadNotAcceptedException,
    "71": TransferDataSuspendedException,
    "72": GeneralProgrammingFailureException,
    "73": WrongBlockSequenceCounterException,
    # 74-77: ISOSAEReserved
    "78": RequestCorrectlyReceivedResponsePendingException,
    # 79-7D: ISOSAEReserved
    "7E": SubFunctionNotSupportedInActiveSessionException,
    "7F": ServiceNotSupportedInActiveSessionException,
    # 80: ISOSAEReserved
    "81": RpmTooHighException,
    "82": RpmTooLowException,
    "83": EngineIsRunningException,
    "84": EngineIsNotRunningException,
    "85": EngineRunTimeTooLowException,
    "86": TemperatureTooHighException,
    "87": TemperatureTooLowException,
    "88": VehicleSpeedTooHighException,
    "89": VehicleSpeedTooLowException,
    "8A": ThrottlePedalTooHighException,
    "8B": ThrottlePedalTooLowException,
    "8C": TransmissionRangeNotInNeutralException,
    "8D": TransmissionRangeNotInGearException,
    # 8E: ISOSAEReserved
    "8F": BrakeSwitchesNotClosedException,
    "90": ShifterLeverNotInParkException,
    "91": TorqueConverterClutchLockedException,
    "92": VoltageTooHighException,
    "93": VoltageTooLowException,
    "94": ResourceTemporarilyNotAvailableException,
    # 95-EF: reservedForSpecificConditionsNotCorrect
    # F0-FE: vehicleManufacturerSpecificConditionsNotCorrect
    # FF: ISOSAEReserved
}
