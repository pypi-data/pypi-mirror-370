from enums.framework.enum import StandardEnum
from enums.framework.item import StandardEnumItem


class TestNewEnum(StandardEnum):
    PASSED = StandardEnumItem(code="PASSED")
    FAILED = StandardEnumItem(code="FAILED")
