# -*- coding: utf-8 -*-

import datetime
import os
import DataType
import logging

class ConvertUtil:
    def __init__(self):
        self.result = 0
    def convert_value_by_field(self, field_name, value, invalid_val, base_utc=None):
        self.field_name = field_name
        self.value = value
        self.invalid_val = invalid_val
        self.base_utc = base_utc
        _is_valid = self.is_valid() # Checks if data is defined as invalid

        if (self.field_name == 'TIMESTAMP') or (self.field_name == 'TIME_CREATED'):
            self.unit = 'UTC0' if self.base_utc is None else f'UTC{base_utc}'
            self.convert_to_utc_timstamp()
            self.result = f'{self.value if _is_valid else "-"} ({self.unit})'

        elif (self.field_name == 'POSITION_LAT') or (self.field_name == 'POSITION_LONG'):
            # 2^32 / 360 = 11930465
            # Ref. https://gis.stackexchange.com/questions/122186/convert-garmin-or-iphone-weird-gps-coordinates
            # ex) [LATITUDE] raw_value = 446971978 | 37.46475749268784 -> 37.464757
            # ex) [LONGDITUDE] raw_value = 1515472765 | 127.02545667750586 -> 127.025457
            self.unit = '°'
            self.value = round(self.value/11930465, 6) if _is_valid else "-" # 소수점 6번째 자리 반올림 처리
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'DISTANCE':
            # centimeters to meters
            self.unit = 'm'
            self.value = f'{self.value/100:.2f}' if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'ACCUMULATED_POWER':
            self.unit = 'watts'
            self.value = self.value if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'ALTITUDE':
            self.unit = 'm'
            # Saved altitude val: (measured val x 5) + 500
            self.value = ((self.value / 5) - 500) if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'SPEED':
            self.unit = 'm/s'
            self.value = self.value / 1000  if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'POWER':
            self.unit = 'watts'
            self.value = self.value if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'HEART_RATE':
            self.unit = 'bpm'
            self.value = self.value if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'CADENCE':
            self.unit = 'rpm'
            self.value = self.value if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'TEMPERATURE':
            self.unit = '°C'
            self.value = self.value if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'LEFT_RIGHT_BALANCE':
            self.value = self.value if _is_valid else "-"
            self.result = f'{self.value}'

        elif self.field_name == 'LEFT_TORQUE_EFFECTIVENESS':
            self.unit = 'percent'
            self.value = self.value / 2 if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'RIGHT_TORQUE_EFFECTIVENESS':
            self.unit = 'percent'
            self.value = self.value / 2 if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'LEFT_PEDAL_SMOOTHNESS':
            self.unit = 'percent'
            self.value = self.value / 2 if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'RIGHT_PEDAL_SMOOTHNESS':
            self.unit = 'percent'
            self.value = self.value / 2 if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'FRACTIONAL_CADENCE':
            self.unit = 'rpm'
            self.value = self.value / 128 if _is_valid else "-"
            self.result = f'{self.value} ({self.unit})'

        elif self.field_name == 'SERIAL_NUMBER':
            self.result = f'{self.value}'

        elif self.field_name == 'PRODUCT':
            self.result = f'{self.value}'

        elif self.field_name == 'TYPE':
            self.result = DataType.FILE_ID_DataType(self.value).name

        elif self.field_name == 'MANUFACTURER':
            self.result = DataType.FILE_ID_Manufacturer(self.value).name


        else:
            self.result = f'{self.value}'

        return self.result

    def is_valid(self):
        # will not parse if read data is defined as INVALID_VALUE
        if self.value == self.invalid_val:
            return False
        else:
            return True

    def convert_to_utc_timstamp(self):
        EPOCH_BASE_TS = 631065600

        ts_utc = datetime.datetime.utcfromtimestamp((self.value if self.value else 0) + EPOCH_BASE_TS)

        if (self.base_utc is None) or (self.base_utc == 0):
            self.base_utc = 0
            self.value = ts_utc
        else:
            ts_operator = self.base_utc[0]
            bias = int(self.base_utc[1])
            ts_bias = datetime.timedelta(hours=bias)

            if ts_operator == '+':
                self.value = ts_utc + ts_bias
            elif ts_operator == '-':
                self.value = ts_utc - ts_bias
            else:
                raise "base_utc value error"


class LogUtil:
    def get_logger(self, log_path, log_name, log_level="DEBUG"):
        """ Configure Logger and Returns Handler """

        os.makedirs(log_path, exist_ok=True)
        log_file = os.path.join(log_path, log_name)

        logger = logging.getLogger()
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if log_level == "INFO":
            logger.setLevel(logging.INFO)
        elif log_level == "WARNING":
            logger.setLevel(logging.WARNING)
        elif log_level == "ERROR":
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.DEBUG)

        logger.setLevel(log_level)

        return logger

    def release_logger(self, logger):
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)



