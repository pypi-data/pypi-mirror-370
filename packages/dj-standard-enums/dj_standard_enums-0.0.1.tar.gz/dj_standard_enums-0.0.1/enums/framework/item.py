class StandardEnumItem:
    """
    Represents a standard enumerated item with associated details.

    This class serves as a data structure to encapsulate an enumerated item's
    code, a human-readable name, and any additional data associated with it.
    It is designed to manage these details in a structured and consistent manner.

    :ivar code: A unique identifier representing the enumerated item.
    :type code: str
    :ivar visible_name: A human-readable name for the enumerated item.
        Defaults to the value of `code` if not provided.
    :type visible_name: str, optional
    :ivar extra_data: A dictionary containing additional information
        or metadata for the enumerated item. Defaults to an empty dictionary
        if not provided.
    :type extra_data: dict
    """

    def __init__(self, code, visible_name=None, extra_data=None):
        self.code = code
        self.visible_name = visible_name or self.code
        self.extra_data = extra_data or {}

    @property
    def all(self):
        return {
            "code": self.code,
            "visible_name": self.visible_name,
            "extra_data": self.extra_data,
        }
