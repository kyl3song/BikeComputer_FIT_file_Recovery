from enum import Enum

class RecordGlobalMessageNum(Enum):
    FILE_ID = 0
    CAPABILITIES = 1
    DEVICE_SETTINGS = 2
    USER_PROFILE = 3
    HRM_PROFILE = 4
    SDM_PROFILE = 5
    BIKE_PROFILE = 6
    ZONES_TARGET = 7
    HR_ZONE = 8
    POWER_ZONE = 9
    MET_ZONE = 10
    SPORT = 12
    GOAL = 15
    SESSION = 18
    LAP = 19
    RECORD = 20
    EVENT = 21
    DEVICE_INFO = 23
    WORKOUT = 26
    WORKOUT_STEP = 27
    SCHEDULE = 28
    WEIGHT_SCALE = 30
    COURSE = 31
    COURSE_POINT = 32
    TOTALS = 33
    ACTIVITY = 34
    SOFTWARE = 35
    FILE_CAPABILITIES = 37
    MESG_CAPABILITIES = 38
    FIELD_CAPABILITIES = 39
    FILE_CREATOR = 49
    BLOOD_PRESSURE = 51
    SPEED_ZONE = 53
    MONITORING = 55
    TRAINING_FILE = 72
    HRV = 78
    ANT_RX = 80
    ANT_TX = 81
    ANT_CHANNEL_ID = 82
    LENGTH = 101
    MONITORING_INFO = 103
    PAD = 105
    SLAVE_DEVICE = 106
    CONNECTIVITY = 127
    WEATHER_CONDITIONS = 128
    WEATHER_ALERT = 129
    CADENCE_ZONE = 131
    HR = 132
    SEGMENT_LAP = 142
    MEMO_GLOB = 145
    SEGMENT_ID = 148
    SEGMENT_LEADERBOARD_ENTRY = 149
    SEGMENT_POINT = 150
    SEGMENT_FILE = 151
    WORKOUT_SESSION = 158
    WATCHFACE_SETTINGS = 159
    GPS_METADATA = 160
    CAMERA_EVENT = 161
    TIMESTAMP_CORRELATION = 162
    GYROSCOPE_DATA = 164
    ACCELEROMETER_DATA = 165
    THREE_D_SENSOR_CALIBRATION = 167
    VIDEO_FRAME = 169
    OBDII_DATA = 174
    NMEA_SENTENCE = 177
    AVIATION_ATTITUDE = 178
    VIDEO = 184
    VIDEO_TITLE = 185
    VIDEO_DESCRIPTION = 186
    VIDEO_CLIP = 187
    OHR_SETTINGS = 188
    EXD_SCREEN_CONFIGURATION = 200
    EXD_DATA_FIELD_CONFIGURATION = 201
    EXD_DATA_CONCEPT_CONFIGURATION = 202
    FIELD_DESCRIPTION = 206
    DEVELOPER_DATA_ID = 207
    MAGNETOMETER_DATA = 208
    BAROMETER_DATA = 209
    ONE_D_SENSOR_CALIBRATION = 210
    SET = 225
    STRESS_LEVEL = 227
    DIVE_SETTINGS = 258
    DIVE_GAS = 259
    DIVE_ALARM = 262
    EXERCISE_TITLE = 264
    DIVE_SUMMARY = 268
    JUMP = 285
    CLIMB_PRO = 317
    DEVICE_AUX_BATTERY_INFO = 375
    MFG_RANGE_MIN = 0xFF00
    MFG_RANGE_MAX = 0xFFFE
    COUNT = 91

class RecordFieldName(Enum):
    TYPE = 0
    MANUFACTURER = 1
    PRODUCT = 2
    SERIAL_NUMBER = 3
    TIME_CREATED = 4
    NUMBER = 5
    PRODUCT_NAME = 8

class RecordDataType(Enum):
    ACTIVITY = 4
    WORKOUT = 5
    COURSE = 6


FIELD_NAME = {
    "FILE_ID" : {
        0 : "TYPE",
        1 : "MANUFACTURER",
        2 : "PRODUCT",
        3 : "SERIAL_NUMBER",
        4 : "TIME_CREATED",
        5 : "NUMBER",
        8 : "PRODUCT_NAME"
    },
    "RECORD" : {
        253: "TIMESTAMP",
        0: "POSITION_LAT",
        1: "POSITION_LONG",
        5: "DISTANCE",
        11: "TIME_FROM_COURSE",
        19: "TOTAL_CYCLES",
        29: "ACCUMULATED_POWER",
        73: "ENHANCED_SPEED",
        78: "ENHANCED_ALTITUDE",
        2: "ALTITUDE",
        6: "SPEED",
        7: "POWER",
        9: "GRADE",
        28: "COMPRESSED_ACCUMULATED_POWER",
        32: "VERTICAL_SPEED",
        33: "CALORIES",
        39: "VERTICAL_OSCILLATION",
        40: "STANCE_TIME_PERCENT",
        41: "STANCE_TIME",
        51: "BALL_SPEED",
        52: "CADENCE256",
        54: "TOTAL_HEMOGLOBIN_CONC",
        55: "TOTAL_HEMOGLOBIN_CONC_MIN",
        56: "TOTAL_HEMOGLOBIN_CONC_MAX",
        57: "SATURATED_HEMOGLOBIN_PERCENT",
        58: "SATURATED_HEMOGLOBIN_PERCENT_MIN",
        59: "SATURATED_HEMOGLOBIN_PERCENT_MAX",
        3: "HEART_RATE",
        4: "CADENCE",
        8: "COMPRESSED_SPEED_DISTANCE",
        10: "RESISTANCE",
        12: "CYCLE_LENGTH",
        13: "TEMPERATURE",
        17: "SPEED_1S",
        18: "CYCLES",
        30: "LEFT_RIGHT_BALANCE",
        31: "GPS_ACCURACY",
        42: "ACTIVITY_TYPE",
        43: "LEFT_TORQUE_EFFECTIVENESS",
        44: "RIGHT_TORQUE_EFFECTIVENESS",
        45: "LEFT_PEDAL_SMOOTHNESS",
        46: "RIGHT_PEDAL_SMOOTHNESS",
        47: "COMBINED_PEDAL_SMOOTHNESS",
        48: "TIME128",
        49: "STROKE_TYPE",
        50: "ZONE",
        53: "FRACTIONAL_CADENCE",
        62: "DEVICE_INDEX",
    }

}

BASE_TYPE = {
    "ENUM": 0x00,
    "SINT8": 0x01,
    "UINT8": 0x02,
    "SINT16": 0x83,
    "UINT16": 0x84,
    "SINT32": 0x85,
    "UINT32": 0x86,
    "STRING": 0x07,
    "FLOAT32": 0x88,
    "FLOAT64": 0x89,
    "UINT8Z": 0x0A,
    "UINT16Z": 0x8B,
    "UINT32Z": 0x8C,
    "BYTE": 0x0D,
    "SINT64": 0x8E,
    "UINT64": 0x8F,
    "UINT64Z": 0x90
}

BASE_TYPE_DEFINITIONS = {
    0x00: {'size': 1, 'type': BASE_TYPE["ENUM"], 'signed': False, 'type_code': 'B', 'invalid': 0xFF},
    0x01: {'size': 1, 'type': BASE_TYPE["SINT8"], 'signed': True, 'type_code': 'b', 'invalid': 0x7F},
    0x02: {'size': 1, 'type': BASE_TYPE["UINT8"], 'signed': False, 'type_code': 'B', 'invalid': 0xFF},
    0x83: {'size': 2, 'type': BASE_TYPE["SINT16"], 'signed': True, 'type_code': 'h', 'invalid': 0x7FFF},
    0x84: {'size': 2, 'type': BASE_TYPE["UINT16"], 'signed': False, 'type_code': 'H', 'invalid': 0xFFFF},
    0x85: {'size': 4, 'type': BASE_TYPE["SINT32"], 'signed': True, 'type_code': 'i', 'invalid': 0x7FFFFFFF},
    0x86: {'size': 4, 'type': BASE_TYPE["UINT32"], 'signed': False, 'type_code': 'I', 'invalid': 0xFFFFFFFF},
    0x07: {'size': 1, 'type': BASE_TYPE["STRING"], 'signed': False, 'type_code': 's', 'invalid': 0x00},
    0x88: {'size': 4, 'type': BASE_TYPE["FLOAT32"], 'signed': True, 'type_code': 'f', 'invalid': 0xFFFFFFFF},
    0x89: {'size': 8, 'type': BASE_TYPE["FLOAT64"], 'signed': True, 'type_code': 'd', 'invalid': 0xFFFFFFFFFFFFFFFF},
    0x0A: {'size': 1, 'type': BASE_TYPE["UINT8Z"], 'signed': False, 'type_code': 'B', 'invalid': 0x00},
    0x8B: {'size': 2, 'type': BASE_TYPE["UINT16Z"], 'signed': False, 'type_code': 'H', 'invalid': 0x0000},
    0x8C: {'size': 4, 'type': BASE_TYPE["UINT32Z"], 'signed': False, 'type_code': 'I', 'invalid': 0x00000000},
    0x0D: {'size': 1, 'type': BASE_TYPE["BYTE"], 'signed': False, 'type_code': 'B', 'invalid': 0xFF},
    0x8E: {'size': 8, 'type': BASE_TYPE["SINT64"], 'signed': True, 'type_code': 'q', 'invalid': 0x7FFFFFFFFFFFFFFF},
    0x8F: {'size': 8, 'type': BASE_TYPE["UINT64"], 'signed': False, 'type_code': 'Q', 'invalid': 0xFFFFFFFFFFFFFFFF},
    0x90: {'size': 8, 'type': BASE_TYPE["UINT64Z"], 'signed': False, 'type_code': 'L', 'invalid': 0x0000000000000000},
}

NUMERIC_FIELD_TYPES = [
    "sint8",
    "uint8",
    "sint16",
    "uint16",
    "sint32",
    "uint32",
    "float32",
    "float64",
    "uint8z",
    "uint16z",
    "uint32z",
    "byte",
    "sint64",
    "uint64",
    "uint64z"
]
