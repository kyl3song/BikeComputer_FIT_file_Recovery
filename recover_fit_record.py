# -*- coding: utf-8 -*-

import re
import os
import sys
import DataType
import struct
import datetime
from Util import ConvertUtil, LogUtil


FILE_HEADER_SIZE = 1
RECORD_HEADER_SIZE = 1
RECORD_CONTENT_FIXED_SIZE = 5

class recoverRecord:
    def __init__(self, target_file, output_file):
        self.target_file = target_file
        self.output_file = output_file
        self.LOOKUP_TABLE_GMESG_ALL = {}
        self.LOOKUP_TABLE_GMESG_ONLY_RECORD = {}
        self.LOOKUP_TABLE_GMESG_NOT_RECORD = {}
        self.data_mesg_count = 0
        self.current_offset = 0
        self.autogen_regex_pattern_match_count = 0
        self.RECOVER_MINTIME_YYYYMMDD = None
        self.RECOVER_MAXTIME_YYYYMMDD = None
        self.RECOVER_TIMEDELTA_DAYS = 2
        self.convert_util = ConvertUtil()

        self.get_file_size()
        self.read_file_data()
        self.get_file_handler()
        self.get_output_file_handler()
        self.logger_flag = True
        self.log_util = LogUtil()
        log_path = os.path.dirname(target_file)
        _basename = os.path.basename(target_file)
        _basename = os.path.splitext(_basename)[0]
        log_name = _basename + '_FIT_Recover.log'
        self.logger = self.log_util.get_logger(log_path=log_path,
                                               log_name=log_name,
                                               log_level=LOG_LEVEL)
        self.first_parsed_arch = None

    def get_file_handler(self):
        """ Gets FIT file handler """
        self.fh_fit = open(self.target_file, mode='rb')

    def get_output_file_handler(self):
        """ Gets OUTPUT file handler """
        self.fh_dest = open(self.output_file, mode='w')

    def get_file_size(self):
        """ Gets FIT File Size """
        self.target_size = os.path.getsize(self.target_file)

    def read_file_data(self):
        """ Reads FIT file data """
        try:
            __target_size = os.path.getsize(self.target_file)
            with open(self.target_file, mode='rb') as fh_fit:
                self.fit_data = fh_fit.read()
        except Exception as e:
            print(e)
            sys.exit()

    def close_fit_handler(self):
        """ Closes FIT file handler """
        self.fh_fit.close()

    def close_output_file_handler(self):
        """ Closes output file handler """
        self.fh_dest.close()

    def get_file_pattern_info(self):
        """ Returns regex to match .FIT signature """
        pattern = b'\\x0E.{3,3}.{3,3}\\x00.FIT.{2,2}'
        pattern_size = 14 # 0xE

        return pattern, pattern_size

    def get_definition_msg_pattern(self):
        """ Returns regex to match Definition Message """
        # Field count limited to 100(0x64)
        # GLOBAL_MESG Number : 0x0000 ~ 0x0177
        pattern = b'[\\x40-\\x4F]\\x00\\x00([\\x00-\\xFF]\\x00|[\\x00-\\x77]\\x01)[\\x01-\\x64]'
        pattern_size = 6

        return pattern, pattern_size

    def search_with_regex(self, regx_pattern, buffer, pattern_size=None):
        """ Returns matched data list """
        regex = re.compile(regx_pattern, re.MULTILINE | re.DOTALL)
        matches = list(regex.finditer(buffer))

        return matches

    def parse_file_hdr(self):
        """ Parses FIT file header """
        self.fh_fit.seek(0)
        self.file_hdr_size = int.from_bytes(self.fh_fit.read(FILE_HEADER_SIZE), byteorder='little')
        _protocol_buf = int.from_bytes(self.fh_fit.read(1), byteorder='little')
        _profile_ver = int.from_bytes(self.fh_fit.read(2), byteorder='little')
        _data_size = int.from_bytes(self.fh_fit.read(4), byteorder='little')
        _sigature = self.fh_fit.read(4)
        _crc = int.from_bytes(self.fh_fit.read(2), byteorder='little')

        if _sigature != b'.FIT':
            raise "File Signature Mismatch"
        self.logger.info(f"[*] File Header: Data Size: {_data_size} | Signature - {_sigature} | CRC - {_crc}")


    def parse_record_hdr(self):
        """ Parses record header : Will be determined a Definition Message or Data Message according to header value) """
        lookup_table = {}

        # Record header: byteorder is not in use as it's one byte.
        record_hdr = int.from_bytes(self.fh_fit.read(RECORD_HEADER_SIZE), byteorder='little')
        # This is limited not have Developer Field in the header. (Refer to the spec for developer field in FIT format)
        if 0x40 <= record_hdr <= 0x4F:
            record_msg_type = 'DEFINITION_MESG'
        elif 0x00 <= record_hdr <= 0x0F:
            record_msg_type = 'DATA_MESG'
        else:
            # Ready for recovery
            self.logger.critical(f"[!] OFFSET: {hex(self.current_offset)} | RECORD HEADER: {hex(record_hdr)} - NOT VALID")
            return True

        # e.g. X1XX XXXX : Definition Message // X0XX XXXX : Data Message
        # 0xxxxxxx -> Normal Header // 1xxxxxxx -> Compressed Header
        # record_hdr_type = 'COMPRESSED_HDR' if ((record_hdr & 0b10000000) >> 7) == 1 else 'NORMAL_HDR'
        # record_msg_type = 'DEFINITION_MESG' if ((record_hdr & 0b01000000) >> 6) == 1 else 'DATA_MESG'
        # is_record_dev_data_flag = True if ((record_hdr & 0b00100000) >> 5) == 1 else False

        # Local Message Number
        local_msg_num = record_hdr & 0x0F

        # Definition Message
        if record_msg_type == "DEFINITION_MESG":
            record_fixed_content = self.fh_fit.read(RECORD_CONTENT_FIXED_SIZE)
            _reserved = record_fixed_content[0] # 예약 값 (필요 없음)
            self.architecture = 'little' if record_fixed_content[1] == 0 else 'big'

            if self.first_parsed_arch is None:
                self.first_parsed_arch = self.architecture

            if self.architecture != self.first_parsed_arch:
                self.logger.critical("[!] ARCHITECTURE from Definition Message: BIG")
                self.architecture = self.first_parsed_arch
                return False
                #raise "ARCHITECTURE: BIG"

            global_msg_num = int.from_bytes(record_fixed_content[2:4], byteorder=self.architecture)
            record_num_of_field = int(record_fixed_content[4])

            # Global Messages : FILE_ID, RECORDS, DEVICE_SETTINGS, DIVE_SETTINGS, CLIMB_PRO...
            try:
                global_message = DataType.RecordGlobalMessageNum(global_msg_num).name
            except:
                global_message = global_msg_num
                pass

            field_desc_list = self.parse_field_definition(record_num_of_field)
            msg = f"OFFSET : {hex(self.current_offset)} | " \
                  f"RECORD_HDR : {hex(record_hdr)} | " \
                  f"LOCAL_MESG : {hex(local_msg_num)} | " \
                  f"GLOBAL_MESG : {global_message} | " \
                  f"FIELD_COUNTS : {record_num_of_field} | " \
                  f"FIELD_SIZE : {sum([i[1] for i in field_desc_list])} | " \
                  f"ARCH : {self.architecture} | " \
                  f"Field Definition : {field_desc_list}"

            # Make lookup table that contains items defined in the definition message.
            lookup_table = {local_msg_num: {'OFFSET': hex(self.current_offset),
                                            'RECORD_HDR': hex(record_hdr),
                                            'LOCAL_MESG': hex(local_msg_num),
                                            'GLOBAL_MESG': global_message,
                                            'FIELD_COUNTS': record_num_of_field,
                                            # FIELD_SIZE needs for regex auto-generation
                                            'FIELD_SIZE': sum([i[1] for i in field_desc_list]),
                                            'ARCH': self.architecture,
                                            'FIELD_DESC': field_desc_list}}

            self.logger.debug(msg)
            #self.fh_dest.write(f'{msg}\n')

            # Lookup table update - RECORD Lookup Table: Global Message ALL
            self.LOOKUP_TABLE_GMESG_ALL.update(lookup_table)

            # Separate lookup tables into two. (Global Message: RECORD or Non-RECORD)
            self.LOOKUP_TABLE_GMESG_ONLY_RECORD.update(lookup_table) if global_message == 'RECORD' else self.LOOKUP_TABLE_GMESG_NOT_RECORD.update(lookup_table)

            return False

        # Record header: Data Message
        elif record_msg_type == 'DATA_MESG':
            self.decode_data_message(local_msg_num)


    def parse_field_definition(self, record_num_of_field):
        """ Parses Field Definition """
        # 3 bytes per each field
        field_desc_list = []

        try:
            for _ in range(record_num_of_field):
                _temp = []
                _record_content_variable = self.fh_fit.read(3)
                field_definition_num = _record_content_variable[0]
                defined_field_size = _record_content_variable[1]
                base_type = _record_content_variable[2]

                _temp.append(field_definition_num)
                _temp.append(defined_field_size)
                _temp.append(base_type)

                field_desc_list.append(_temp)
        except Exception as e:
            self.logger.critical(f"[ERROR][PARSE_FIELD_DEFINITION] {e}")
        finally:
            return field_desc_list

    def decode_data_message(self, local_msg_num):
        """ Decodes Data Message : Decode values based on the Definition Message """
        try:
            field_desc_list = self.LOOKUP_TABLE_GMESG_ALL[local_msg_num]['FIELD_DESC']
            global_mesg = self.LOOKUP_TABLE_GMESG_ALL[local_msg_num]['GLOBAL_MESG']
        except Exception as e:
            self.logger.critical(f"[!] LOOKUP_TABLE_GMESG error - {e}")
            return

        # Skip file pointer to the size of Field and return.
        if (global_mesg != 'RECORD') and (global_mesg != 'FILE_ID'):
            _ = self.fh_fit.read(self.LOOKUP_TABLE_GMESG_ALL[local_msg_num]['FIELD_SIZE'])
            return

        _tmp_field_size = self.LOOKUP_TABLE_GMESG_ALL[local_msg_num]['FIELD_SIZE']

        # Debugging purpose
        # if hex(self.current_offset) == '0x0000':
        #     print("STOP")

        _offset_msg = f"[*] Data Message Offset(Inc. HDR): {hex(self.current_offset)} ~ {hex(self.current_offset + _tmp_field_size)}"
        self.logger.debug(_offset_msg)
        self.fh_dest.write(f"{_offset_msg}\n")

        for field_name, field_size, base_type in field_desc_list:
            known_field = True
            try:
                field_name_converted = DataType.FIELD_NAME[global_mesg][field_name]
            except Exception:
                field_name_converted = f'Field_{field_name}'
                known_field = False

            base_type_converted = DataType.BASE_TYPE_DEFINITIONS[base_type]['type_code']
            invalid_val = DataType.BASE_TYPE_DEFINITIONS[base_type]['invalid']

            field_data = self.fh_fit.read(field_size)
            endianness = '<' if self.architecture == 'little' else '>'
            fmt = f'{endianness}{base_type_converted}'
            try:
                field_data = struct.unpack(fmt, field_data)[0]
                converted_val = self.convert_util.convert_value_by_field(field_name_converted, field_data, invalid_val, base_utc='+9')

                # Only need TIME_CREATED from 'FILE_ID' to make the base timestamp to recover.
                if (global_mesg == 'FILE_ID') and (field_name_converted == 'TIME_CREATED'):
                    _created_time = converted_val.split('(')[0].strip()
                    _created_time = datetime.datetime.strptime(_created_time, '%Y-%m-%d %H:%M:%S')
                    _min = _created_time - datetime.timedelta(days=self.RECOVER_TIMEDELTA_DAYS)
                    self.RECOVER_MINTIME_YYYYMMDD = int(f'{_min.year}{_min.month:02d}{_min.day:02d}')
                    _max = _created_time + datetime.timedelta(days=self.RECOVER_TIMEDELTA_DAYS)
                    self.RECOVER_MAXTIME_YYYYMMDD = int(f'{_max.year}{_max.month:02d}{_max.day:02d}')

                #self.logger.debug(f"    Field Data: {hex(field_data)}({field_data}) -> {converted_val}")
                field_name_converted = field_name_converted.capitalize()

                # e.g. Timestamp: 2023-01-01 00:00:00 (UTC+9) -> 20230101
                if field_name_converted == 'Timestamp':
                    _datetime = int(converted_val.split(' ')[0].replace('-',''))
                    if (_datetime < self.RECOVER_MINTIME_YYYYMMDD) or (_datetime > self.RECOVER_MAXTIME_YYYYMMDD):
                        self.logger.debug(f"TIMESTAMP INVALID: {converted_val} - SKIP")
                        self.logger.debug(f"{'='*50}")
                        return

                msg = f"{field_name_converted}: {converted_val}" if known_field else f"{field_name_converted}: {field_data}"
                self.fh_dest.write(f"[*] {msg}\n")

            except Exception as e:
                field_name_converted = field_name_converted.capitalize()
                converted_val = ''
                msg = f"[!] OFFSET: {hex(self.current_offset)} | {field_name_converted}: {field_data} - FIELD NAME CANNOT BE CONVERTED"
                self.logger.critical(msg)
                return

            self.logger.debug(f"[*] {msg}")
            #self.fh_dest.write(f"[*] {msg}\n")

            # For debugging purpose
            # if field_name_converted == 'Timestamp':
            #     DEBUG_FILE.write(f"{hex(self.current_offset)} ~ {hex(self.current_offset + _tmp_field_size)} | {converted_val}\n")

        if global_mesg != 'FILE_ID':
            self.data_mesg_count += 1

        self.logger.debug(f"{'='*50}")
        self.fh_dest.write(f"{'='*50}\n")

    def run(self):
        self.parse_file_hdr()
        self.file_size = os.path.getsize(self.target_file)

        # Defines regex and search for definition messages
        regx_pattern, pattern_size = self.get_definition_msg_pattern()
        matches = self.search_with_regex(regx_pattern, self.fit_data, pattern_size)
        match_counts = len(matches)
        self.logger.info(f"Definition Message Matched: {match_counts}")

        # Gets definition Messages' position
        def_mesg_offset_list = [_offset.start() for _offset in matches] if matches else []
        self.logger.debug("========================================")

        while True:
            self.current_offset = self.fh_fit.tell()
            if self.current_offset + 2 >= self.file_size: # CRC value
                self.logger.debug("END OF FILE")
                break
            invalid_header = self.parse_record_hdr()

            if invalid_header and def_mesg_offset_list:
                next_offset_list = list(filter(lambda x: x > self.current_offset, def_mesg_offset_list))
                if next_offset_list:
                    next_offset = next_offset_list[0]
                else: continue

                autogen_regex_list = []
                # Generate regex with the values from RECORD Lookup Table
                if self.LOOKUP_TABLE_GMESG_ONLY_RECORD:
                    for key, val in self.LOOKUP_TABLE_GMESG_ONLY_RECORD.items():
                        field_size = val['FIELD_SIZE']
                        _field_size = '.{' + str(field_size) + ',' + str(field_size) + '}'
                        _local_mesg = f'\\x{key:02X}'
                        _regex = _local_mesg + _field_size + '([\\x00-\\x0F]|[\\x40-\\x4F])'
                        autogen_regex_list.append(_regex.encode())

                    self.logger.debug(f"Auto Generated Regex : {autogen_regex_list}")

                    # Configure the target scan area and search with generated regex.
                    buffer = self.fit_data[self.current_offset:next_offset + 1]
                    for autogen_regex_pattern in autogen_regex_list:
                        matches = self.search_with_regex(autogen_regex_pattern, buffer)
                        match_counts = len(matches)
                        self.logger.debug(f"Auto Generated Regex Matched: {autogen_regex_pattern} | Counts: {match_counts}")

                        sub_offset_list = [(_offset.start(), _offset.end()) for _offset in matches] if matches else []
                        if sub_offset_list:
                            self.logger.info(f"Getting ready for sliding window pattern match...")
                            for start_offset, end_offset in sub_offset_list:
                                _keep_base_offset = self.current_offset
                                self.current_offset = self.current_offset + start_offset
                                self.fh_fit.seek(self.current_offset)
                                self.parse_record_hdr()
                                # current_offset back to where it was
                                self.current_offset = _keep_base_offset

                                ### Get ready for sliding window parttern match (Phase-3)
                                ######################################################
                                # Sliding starts
                                # ㅡㅡㅡㅡ Searched --------> if matched
                                #   ㅡㅡㅡㅡ (Slide 1) -----> potential match
                                #     ㅡㅡㅡㅡ (Slide 2) ---> potential match
                                #       ㅡㅡㅡㅡ (Slide 3)--> potential match
                                ######################################################
                                loop_count = end_offset - start_offset
                                for i in range(1, loop_count):
                                    _pushed_start_offset = start_offset + i
                                    _pushed_end_offset = end_offset + i
                                    
                                    # Checks if end offset is over file size while sliding.
                                    if self.file_size < _pushed_end_offset + 1: # FIT file size < _end_offset
                                        self.logger.critical(f"[!] END OFFSET : {_pushed_end_offset} is grater than target size")
                                        break

                                    # set the sub-buffer and search with it.
                                    _buffer = buffer[_pushed_start_offset:_pushed_end_offset]
                                    matches = self.search_with_regex(autogen_regex_pattern, _buffer, pattern_size)
                                    if matches:
                                        self.logger.debug(f"Sliding window pattern match counts: {len(matches)}")
                                        _keep_base_offset = self.current_offset
                                        self.current_offset = self.current_offset + _pushed_start_offset
                                        self.fh_fit.seek(self.current_offset)
                                        self.parse_record_hdr()
                                        # current_offset back to where it was
                                        self.current_offset = _keep_base_offset

                                        self.autogen_regex_pattern_match_count += 1

                # After scan recovery area, move to the next closest definition offset to continue parsing remaining data.
                self.fh_fit.seek(next_offset)


        self.logger.info(f"Job Finished..!!")
        self.logger.info(f"Total Data Message Counts : {self.data_mesg_count}")
        self.logger.info(f"Auto-generated Regex Pattern Match Counts : {self.autogen_regex_pattern_match_count}")
        self.logger.debug("======================WRAP UP========================")
        self.logger.debug(f"RECORD TABLE: {self.LOOKUP_TABLE_GMESG_ONLY_RECORD}")
        self.logger.debug(f"NOT RECORD TABLE: {self.LOOKUP_TABLE_GMESG_NOT_RECORD}")


        self.log_util.release_logger(self.logger)
        self.close_fit_handler()
        self.close_output_file_handler()



if __name__ == "__main__":

    LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    target_file = r'C:\DFRWS\YOUR_CORRUPTED_FIT_FILE.fit'
    output_file = os.path.splitext(target_file)[0] + '.txt'

    process = recoverRecord(target_file, output_file)
    process.run()

