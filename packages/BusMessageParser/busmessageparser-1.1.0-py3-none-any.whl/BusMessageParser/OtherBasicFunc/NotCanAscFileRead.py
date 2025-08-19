#!/usr/bin/python
# -*- coding: UTF-8 -*-

def LinAscRead(file):
    msg_0 = []
    with open(file, 'r') as asc_f:
        # 按行读取文本内容
        lines = asc_f.readlines()
        for line in lines:
            if 'checksum =' in line:
                new_line = line.replace(" ", ",")
                new_line1 = new_line.replace(",,,", ",")
                new_line2 = new_line1.replace(",,", ",")
                msg0 = new_line2.split(",")
                new_msg0 = list(filter(None, msg0))
                # msg_list0.append(new_msg0)
                len_data = int(new_msg0[4])
                msg_0 = new_msg0[:5]
                msg_1 = new_msg0[5:]
                msg_2 = msg_1[:len_data]
                msg_3 = ''.join(msg_2)
                msg_0.append(msg_3)

    return msg_0


def FlexRayAscRead(file):
    fr_ch = {
        "1": "A",
        "2": "B",
        "3": "AB"
    }
    msg_0 = []
    with open(file, 'r') as asc_f:
        # 按行读取文本内容
        lines = asc_f.readlines()
        for line in lines:
            if 'RMSG' in line and "Fr" in line:
                new_line = line.replace(" ", ",")
                new_line1 = new_line.replace(",,,", ",")
                new_line2 = new_line1.replace(",,", ",")
                msg0 = new_line2.split(",")
                new_msg0 = list(filter(None, msg0))
                # msg_list0.append(new_msg0)
                msg_timestamp = new_msg0[0]
                msg_CH_num = new_msg0[5]
                msg_CH_str = new_msg0[6]
                msg_CH = f"FlexRay{msg_CH_num}: {fr_ch[msg_CH_str]}"

                msg_id = new_msg0[7]
                msg_id_cycle = new_msg0[8]
                msg_direction = new_msg0[9]
                data_len = int(new_msg0[17])
                msg_0 = [msg_timestamp, msg_CH, msg_id, msg_id_cycle, msg_direction, data_len]
                msg_1 = new_msg0[18:]
                msg_2 = msg_1[:data_len]
                msg_3 = ' '.join(msg_2)
                msg_0.append(msg_3)

    return msg_0


def NotCanAscDuplicate(msgs):
    data_dict = {}
    duplicate_count = 0
    for num, msg in enumerate(msgs):
        if num == 0:
            print("正在校验， 请稍后...")
        # key = str(msg.channel) + "_" + str(msg.arbitration_id) + "_" + msg_x + "_" + str(msg.data.hex())
        key = str(msg[1]) + "_" + str(msg[2]) + "_" + msg[3] + "_" + str(msg[5])
        if key not in data_dict:
            data_dict[key] = {}
        else:
            if msg[0] not in data_dict[key]:
                data_dict[key][msg[0]] = 0
            else:
                duplicate_count += 1
    return duplicate_count

def MotCanAscReverse(msgs, is_OneCH, is_IdentifyID):

    def only_channel_read(read_msg, data_dict_one, reverse_count, is_assertID):
        # region """单通道"""
        key_ch = str(read_msg[1])
        if key_ch not in data_dict_one:
            data_dict_one[key_ch] = (read_msg[0], read_msg[2])
        else:
            last_ts = data_dict_one[key_ch][0]
            if is_assertID:
                last_msg = data_dict_one[key_ch][1]
                if float(read_msg[0]) < float(last_ts) and read_msg[2] == last_msg:
                    reverse_count += 1
                else:
                    data_dict_one[key_ch] = (read_msg[0], read_msg[2])
            else:
                if float(read_msg[0]) < float(last_ts):
                    reverse_count += 1
                else:
                    data_dict_one[key_ch] = (read_msg[0], read_msg[2])
        # endregion
    def all_channel_read(read_msg, data_dict_all, reverse_count, is_assertID):
        # region """全通道"""
        if float(read_msg[0]) < data_dict_all["all"][0]:
            if is_assertID:
                reverse_count += 1
            else:
                if read_msg[2] == data_dict_all["all"][1]:
                    reverse_count += 1
                else:
                    data_dict_all["all"] = (read_msg[0], read_msg[2], read_msg[1])
        else:
            data_dict_all["all"] = (read_msg[0], read_msg[2], read_msg[1])
        # endregion

    re_count = 0
    for num, msg in enumerate(msgs):
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
        if num + 1 == len(msgs):
            print(f"已校验完 {len(msgs)} 帧数据...")
    return re_count
