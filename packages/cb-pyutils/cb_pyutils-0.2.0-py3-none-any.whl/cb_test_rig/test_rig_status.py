from enum import Enum


class TestRigStatusEnumValue():
    def __init__(self, rank, color):
        self.rank = rank
        self.color = color


class TestRigStatus(Enum):
    CLEAR = TestRigStatusEnumValue(0, (0xff, 0x00, 0xff))  # Magenta
    IDLE = TestRigStatusEnumValue(1, (0x00, 0xff, 0xff))  # Cyan
    PASS = TestRigStatusEnumValue(2, (0x00, 0xff, 0x00))  # Green
    WARNING = TestRigStatusEnumValue(3, (0xff, 0xff, 0x00))  # Yellow
    FAIL = TestRigStatusEnumValue(4, (0xff, 0x00, 0x00))  # Red

    @staticmethod
    def list():
        return list(map(lambda ts: ts, TestRigStatus))

    @staticmethod
    def list_name():
        return list(map(lambda ts: ts.name, TestRigStatus))

    @staticmethod
    def list_value():
        return list(map(lambda ts: ts.value, TestRigStatus))
