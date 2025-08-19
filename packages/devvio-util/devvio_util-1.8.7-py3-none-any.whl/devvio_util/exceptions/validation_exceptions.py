from marshmallow import ValidationError


class SerializeError(ValueError):
    pass


class DeserializeError(ValueError):
    pass


class InputValidationError(ValidationError):
    def __init__(self, ve: ValidationError):
        super().__init__(ve.messages, ve.field_name, ve.data, ve.valid_data)


class OutputValidationError(ValidationError):
    def __init__(self, ve: ValidationError):
        super().__init__(ve.messages, ve.field_name, ve.data, ve.valid_data)


class InternalInputValidationError(ValidationError):
    pass


class InternalOutputValidationError(ValidationError):
    pass
