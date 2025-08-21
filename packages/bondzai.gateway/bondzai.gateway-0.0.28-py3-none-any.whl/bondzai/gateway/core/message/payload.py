class MessagePayload(object):
    @classmethod
    def from_array(cls, operation: int, raw_data: list) -> "MessagePayload":
        raise NotImplemented

    @classmethod
    def from_json(cls, operation: int, raw_data: list) -> "MessagePayload":
        raise NotImplemented

    def to_dict(self) -> dict:
        raise NotImplemented
