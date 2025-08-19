class TuxbakeError(Exception):
    """Base class for all Tuxbuild exceptions"""

    error_help = ""
    error_type = ""


class TuxbakeRunCmdError(TuxbakeError):
    error_help = "Process call failed"
    error_type = "Configuration"


class TuxbakeParsingError(TuxbakeError):
    error_help = "Error while parsing API arguments"
    error_type = "Validation"


class TuxbakeValidationError(TuxbakeError):
    error_help = "Error while validating API arguments"
    error_type = "Validation"


class UnsupportedMetadata(TuxbakeParsingError):
    error_help = "Unsupported metadata"
    error_type = "Parsing"


class UnsupportedMetadataType(TuxbakeParsingError):
    error_help = "Unsupported metadata type: {name}"
    error_type = "Validation"
