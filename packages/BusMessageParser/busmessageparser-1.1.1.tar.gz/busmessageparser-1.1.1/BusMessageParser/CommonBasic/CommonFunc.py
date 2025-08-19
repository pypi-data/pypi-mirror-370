#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import can
from BusMessageParser.OtherBasicFunc.NotCanAscFileRead import *


class _CommonBasic:
    def __init__(self, files, p_type, f_type):
        self.files = files
        self.p_type = p_type.lower()
        self.f_type = f_type.lower()
        self.all_files = []
        self.msgs = []
        self.msg_count = 0
        if self.files is None:
            print("asc文件路径不能为空")
            return
        try:
            if os.path.isfile(self.files):
                self.all_files.append(files)
            elif os.path.isdir(files):
                for root, ds, fs in os.walk(files):
                    AA = fs[0]
                    is_time = len(re.findall('-', AA))
                    is_num = len(re.findall('\d+', AA))
                    if is_time < 6 and 0 < is_num < 9:
                        fs.sort(key=lambda l: int(re.findall('\d+', l)[-1]))
                    for f in fs:
                        if self.f_type in ["asc", "blf", "pcap"]:
                            if f.endswith(f'.{self.f_type}'):
                                fullname = os.path.join(files, f)
                                self.all_files.append(fullname)
                        else:
                            raise Exception(f"暂不支持的文件类型'{f_type}'")
            else:
                raise FileNotFoundError(f"{files}路径非法! ")
        except FileNotFoundError as e:
            raise Exception(f"{f_type}文件路径传入有误：{e.__str__()}")

    def get_msgs(self, bus_type):
        if bus_type == "can":
            print(f"共有 {len(self.all_files)} 个文件，正在读取， 请稍后...")
            for num, file in enumerate(self.all_files):
                print(file)
                if self.f_type == "asc":
                    msgs = can.ASCReader(file)
                    for msg in msgs:
                        self.msg_count += 1
                        self.msgs.append(msg)
                elif self.f_type == "blf":
                    msgs = can.BLFReader(file)
                    self.msg_count += msgs.object_count
                    for msg in msgs:
                        self.msgs.append(msg)
                else:
                    raise Exception("暂不支持的文件类型")

        elif bus_type == "lin":
            for num, file in enumerate(self.all_files):
                print(file)
                if self.f_type == "asc":
                    msg_0 = LinAscRead(file)
                    self.msgs.append(msg_0)
                    self.msg_count += 1
                elif self.f_type == "blf":
                    print("'blf' 类型的'Lin'帧只支持统计帧数量!")
                    msgs = can.BLFReader(file)
                    self.msg_count += msgs.object_count
                    # self.msgs.append(msgs)
        elif bus_type == "flexray":
            for num, file in enumerate(self.all_files):
                print(file)
                if self.f_type == "blf":
                    print("'blf' 类型的'FlexRay'帧只支持统计帧数量!")
                    msgs = can.BLFReader(file)
                    self.msg_count += msgs.object_count
                elif self.f_type == "asc":
                    msg_0 = FlexRayAscRead(file)
                    self.msgs.append(msg_0)
                    self.msg_count += 1
        elif bus_type == "eth":
            for num, file in enumerate(self.all_files):
                print(file)
                if self.f_type == "blf":
                    print("'blf' 类型的 'eth' 帧只支持统计帧数量!")
                    msgs = can.BLFReader(file)
                    self.msg_count += msgs.object_count
                else:
                    raise Exception("'eth' 帧目前只支持统计 'blf' 类型文件的帧数量! ")
        else:
            raise Exception(f"不支持的总线类型: {bus_type}")

    def ParserFramesCount(self):
        counts = self.msg_count
        if counts == 0:
            for _ in self.msgs:
                if counts % 500000 == 0 and counts != 0:
                    print(f"已统计 {counts} 帧数据,请耐心等待...")
                counts += 1
        return counts


class CanMsgParserCommonBasic(_CommonBasic):
    """
    can报文文件解析
    """
    def __init__(self, files, p_type, f_type):
        super().__init__(files, p_type, f_type)

        # 获取帧详情
        self.get_msgs("can")

    def _ParserFramesReverse(self, is_OneCH, is_IdentifyID):

        def only_channel_read(read_msg, data_dict_one, reverse_count, is_assertID):
            # region """单通道"""
            key_ch = str(read_msg.channel)
            if key_ch not in data_dict_one:
                data_dict_one[key_ch] = (read_msg.timestamp, read_msg.arbitration_id)
            else:
                last_ts = data_dict_one[key_ch][0]
                if is_assertID:
                    last_msg = data_dict_one[key_ch][1]
                    if read_msg.timestamp < last_ts and read_msg.arbitration_id == last_msg:
                        reverse_count += 1
                    else:
                        data_dict_one[key_ch] = (read_msg.timestamp, read_msg.arbitration_id)
                else:
                    if read_msg.timestamp < last_ts:
                        reverse_count += 1
                    else:
                        data_dict_one[key_ch] = (read_msg.timestamp, read_msg.arbitration_id)
            # endregion

        def all_channel_read(read_msg, data_dict_all, reverse_count, is_assertID):
            # region """全通道"""
            if read_msg.timestamp < data_dict_all["all"][0]:
                if is_assertID:
                    reverse_count += 1
                else:
                    if read_msg.arbitration_id == data_dict_all["all"][1]:
                        reverse_count += 1
                    else:
                        data_dict_all["all"] = (read_msg.timestamp, read_msg.arbitration_id, read_msg.channel)
            else:
                data_dict_all["all"] = (read_msg.timestamp, read_msg.arbitration_id, read_msg.channel)
            # endregion

        try:
            re_count = 0
            for num, msg in enumerate(self.msgs):
                if num == 0:
                    print("正在校验逆序， 请稍后...")

                if is_OneCH:
                    """单通道"""
                    datas_dict = {}
                    if num == 0:
                        print("正在校验单通道逆序情况， 请稍后...")
                    only_channel_read(msg, datas_dict, re_count, is_IdentifyID)

                else:
                    """全通道"""
                    datas_dict = {"all": (0, 0, 0)}
                    if num == 0:
                        print("正在校验全通道逆序情况， 请稍后...")
                    all_channel_read(msg, datas_dict, re_count, is_IdentifyID)


                if num % 1000000 == 0 and num != 0:
                    print(f"已校验完 {num} 帧数据...")
                if num + 1 == len(self.msgs):
                    print(f"已校验完 {len(self.msgs)} 帧数据...")
            return re_count
        except Exception as e:
            raise Exception(f"校验'{self.f_type}'文件逆序帧时出现异常: {e.__str__()}")

    def _ParserFramesDuplicate(self):
        duplicate_count = 0
        try:
            data_dict = {}
            for num, msg in enumerate(self.msgs):
                if num == 0:
                    print("正在校验， 请稍后...")
                msg_x = "rx" if msg.is_rx else "tx"
                # key = str(msg.channel) + "_" + str(msg.arbitration_id) + "_" + msg_x + "_" + str(msg.data.hex())
                key = str(msg.channel) + "_" + str(msg.arbitration_id) + "_" + msg_x
                if key not in data_dict:
                    data_dict[key] = {}
                else:
                    if msg.timestamp not in data_dict[key]:
                        data_dict[key][msg.timestamp] = 0
                    else:
                        duplicate_count += 1
            return duplicate_count
        except Exception as e:
            raise Exception(f"校验'{self.f_type}'文件重复帧时出现异常: {e.__str__()}")

    def run(self, *args):
        if self.p_type == "count":
            count = self.ParserFramesCount()
        elif self.p_type == "reverse":
            ParserCH = args[0]
            is_IdentifyID = args[1]
            count = self._ParserFramesReverse(ParserCH, is_IdentifyID)
        elif self.p_type == "duplicate":
            count = self._ParserFramesDuplicate()
        else:
            raise Exception(f"不支持的校验方式: {self.p_type}")
        return count


class LinMsgParserCommonBasic(_CommonBasic):
    """
    lin报文文件解析
    """
    def __init__(self, files, p_type, f_type):
        super().__init__(files, p_type, f_type)
        # 获取帧详情
        self.get_msgs("lin")

    def _ParserFramesReverse(self, is_OneCH, is_IdentifyID):
        try:
            re_count = MotCanAscReverse(self.msgs, is_OneCH, is_IdentifyID)
            return re_count
        except Exception as e:
            raise Exception(f"校验'{self.f_type}'文件逆序帧时出现异常: {e.__str__()}")

    def _ParserFramesDuplicate(self):
        try:
            duplicate_count = NotCanAscDuplicate(self.msgs)
            return duplicate_count
        except Exception as e:
            raise Exception(f"校验'{self.f_type}'文件重复帧时出现异常: {e.__str__()}")

    def run(self, *args):
        if self.p_type == "count":
            count = self.ParserFramesCount()
        else:
            if self.f_type.lower() == "asc":
                if self.p_type == "reverse":
                    ParserCH = args[0]
                    is_IdentifyID = args[1]
                    count = self._ParserFramesReverse(ParserCH, is_IdentifyID)
                elif self.p_type == "duplicate":
                    count = self._ParserFramesDuplicate()
                else:
                    raise Exception(f"不支持的校验方式: {self.p_type}")
            else:
                raise Exception(f"文件类型为'{self.f_type}'时, 只支持统计帧数, 请确认传参是否正确! ")
        return count


class EthMsgParserCommonBasic(_CommonBasic):
    """
    eth报文文件解析
    """
    def __init__(self, files, p_type, f_type):
        super().__init__(files, p_type, f_type)
        # 获取帧详情
        self.get_msgs("eth")

    def run(self, *args):
        if self.p_type == "count":
            count = self.ParserFramesCount()
        else:
            raise Exception(f"'eth' 报文只支持统计 'blf' 类型的帧数量!")
        return count


class FlexRayMsgParserCommonBasic(_CommonBasic):
    """
    FlexRay报文文件解析
    """
    def __init__(self, files, p_type, f_type):
        super().__init__(files, p_type, f_type)
        # 获取帧详情
        self.get_msgs("FlexRay")

    def _ParserFramesReverse(self, is_OneCH, is_IdentifyID):

        try:
            re_count = MotCanAscReverse(self.msgs, is_OneCH, is_IdentifyID)
            return re_count
        except Exception as e:
            raise Exception(f"校验'{self.f_type}'文件逆序帧时出现异常: {e.__str__()}")

    def _ParserFramesDuplicate(self):

        try:
            duplicate_count = NotCanAscDuplicate(self.msgs)
            return duplicate_count
        except Exception as e:
            raise Exception(f"校验'{self.f_type}'文件重复帧时出现异常: {e.__str__()}")

    def run(self, *args):
        if self.p_type == "count":
            count = self.ParserFramesCount()
        else:
            if self.f_type.lower() == "asc":
                if self.p_type == "reverse":
                    ParserCH = args[0]
                    is_IdentifyID = args[1]
                    count = self._ParserFramesReverse(ParserCH, is_IdentifyID)
                elif self.p_type == "duplicate":
                    count = self._ParserFramesDuplicate()
                else:
                    raise Exception(f"不支持的校验方式: {self.p_type}")
            else:
                raise Exception(f"文件类型为'{self.f_type}'时, 只支持统计帧数, 请确认传参是否正确! ")
        return count

