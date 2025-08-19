from enum import IntEnum

class ApprovalStatus(IntEnum):
    RESCAN = -2
    PENDING = -1
    FAILED = 0
    APPROVED = 1
    APPROVING = 999
