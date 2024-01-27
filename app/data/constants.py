
from enum import Enum, IntEnum

class MessageType(str, Enum):
    CONFIGURE_CALLBACK               = "configureCallBack"
    RECEIVED_JSON                    = "receivedJson"
    CONFIGURE_TRACK_OBJECT_INFO      = "configureTrackObjectInfo"
    CONFIGURE_STOP_TRACK_OBJECT_INFO = "configureStopTrackObjectInfo"
    SEND_STRING                      = "sendString"
    USING_FULL_SCREEN_CHANGED        = "usingFullScreenChanged"
    SCREEN_SIZE                      = "screenSize"

class KeyInput(Enum):
    UP                 = 1
    DOWN               = 2
    MOUSE_CLICK        = 3
    MOUSE_BOX          = 4
    MOUSE_DOUBLE_CLICK = 5
    MOUSE_UP           = 6

class KeyModifier(Enum):
    NONE  = 0
    SHIFT = 1
    CTRL  = 2
    ALT   = 3

class KeyTarget(Enum):
    TILE = 1
    GOB  = 2

class ServerType(Enum):
    LIVE = 0
    DEV  = 1

class BuildType(Enum):
    DEBUG   = 0
    RELEASE = 1
    PROFILE = 2
    MEMORY  = 3

class ClientAction(str, Enum):
    LOAD_WINDOW  = "loadWindow"
    CLOSE_WINDOW = "closeWindow"
    PAYLOAD      = "jsonPayload"

class EventType(str, Enum):
    PLAY_ACTION = "playAction"
    IMMEDIATE   = "immediateAction"

class Phase(str, Enum):
    MOVE = "Move"
    ATTACK = "Attack"
    CARD = "Card"
    HEAL = "Heal"
    CONFIRM = "Confirm"
    MEMBER_CARD = "MemberCard"

class MirrorMode(IntEnum):
    NONE = 0
    X = 1
    Y = 2
    XY = 3

class OriginMode(IntEnum):
    NONE = 0
    CENTER = 1
    BOTTOM_MIDDLE = 2
    TOP_LEFT = 3

POLICY_FILE = "<cross-domain-policy><allow-access-from domain='*' to-ports='*' /></cross-domain-policy>"
