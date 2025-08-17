#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import can


class ParserCommonBasic:
    """
    can报文文件解析
    """
    def __init__(self, files, p_type, f_type):

        self.files = files
        self.p_type = p_type.lower()
        self.f_type = f_type.lower()
        self.all_files = []
        self.msgs = None
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
                        if self.f_type.lower() == "asc":
                            if f.endswith('.asc'):
                                fullname = os.path.join(files, f)
                                self.all_files.append(fullname)
                        elif self.f_type.lower() == "blf":
                            if f.endswith('.blf'):
                                fullname = os.path.join(files, f)
                                self.all_files.append(fullname)
                        else:
                            raise Exception(f"暂不支持的文件类型'{f_type}'")
            else:
                raise FileNotFoundError(f"{files}路径非法! ")
        except FileNotFoundError as e:
            raise Exception(f"{f_type}文件路径传入有误：{e.__str__()}")

        self.get_msgs()

    def get_msgs(self):
        print(f"共有 {len(self.all_files)} 个文件，正在读取， 请稍后...")
        for num, file in enumerate(self.all_files):
            print(file)
            if self.f_type.lower() == "asc":
                self.msgs = can.ASCReader(file)

            elif self.f_type.lower() == "blf":
                self.msgs = can.BLFReader(file)

    def ParserFramesReverse(self, ParserCH, is_IdentifyID):

        def only_channel_read(read_msg, data_dict_one, reverse_count, is_assertID):
            # region """单通道"""
            key_ch = str(read_msg.channel)
            if key_ch not in data_dict_one:
                data_dict_one[key_ch] = (read_msg.timestamp, read_msg.arbitration_id)
            else:
                last_ts = data_dict_one[key_ch][0]
                if is_assertID=="true":
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
                if is_assertID != "true":
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

                if ParserCH == "单通道":
                    """单通道"""
                    datas_dict = {}
                    if num == 0:
                        print("正在校验单通道逆序情况， 请稍后...")
                    only_channel_read(msg, datas_dict, re_count, is_IdentifyID)

                elif ParserCH == "全通道":
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

    def ParserFramesDuplicate(self):
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

    def ParserFramesCount(self):
        if self.f_type == "blf":
            counts = self.msgs.object_count
            if counts == 0:
                for _ in self.msgs:
                    if counts % 500000 == 0 and counts != 0:
                        print(f"已统计 {counts} 帧数据,请耐心等待...")
                    counts += 1

        elif self.f_type == "asc":
            counts = 0
            for _ in self.msgs:
                if counts % 500000 == 0 and counts != 0:
                    print(f"已统计 {counts} 帧数据,请耐心等待...")
                counts += 1
        else:
            print(f"暂不支持的文件类型: {self.f_type}")
            counts = 0
        return counts

    def run(self, *args):
        if self.p_type == "count":
            count = self.ParserFramesCount()
        elif self.p_type == "reverse":
            if type(args)!=tuple:
                raise Exception("当检验逆序帧时, 需传入'单通道或双通道及是否校验ID的元组'")
            else:
                try:
                    ParserCH = args[0].lower()
                    is_IdentifyID = args[1].lower()
                except IndexError:
                    raise Exception("检验逆序帧时, 传入参数数量不正确, 请确保传入参数为2个!")
                except AttributeError:
                    raise Exception("检验逆序帧时, 传入参数类型不正确, 若参数中使用了(), 请在前面加上*")
            count = self.ParserFramesReverse(ParserCH, is_IdentifyID)
        elif self.p_type == "duplicate":
            count = self.ParserFramesDuplicate()
        else:
            raise Exception(f"不支持的校验方式: {self.p_type}")
        return count


