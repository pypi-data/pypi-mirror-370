#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import time
import paramiko

class GetHILData:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()


        # 初始化默认连接
        self.connect()

    def connect(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.ip, username=self.username, password=self.password)

    def destroy(self):
        self.client.close()

    def get_linux_data_can(self, ch, direction):
        """
        实验运行中才能取到数据
        @param ch: 通道下标, 从1开始
        @param direction: 方向
        """
        try:
            stdin, stdout, stderr = self.client.exec_command(f'echo "flexcan_{direction}_show()" > /sys/class/wrapcan/run ; cat /sys/class/wrapcan/log')
            time.sleep(1)
            # stdin, stdout1, stderr = self.client.exec_command(f'echo "flexcan_count_clr()" > /sys/class/wrapcan/run ;')
            result = stdout.read().decode()
            print(result)
            re_list = result.split("\n")
            re_list1 = str(re_list[ch + 2]).split("|")  # 3,4,5,6
            rere = []
            for i in re_list1:
                uu = i.replace(" ", "")
                rere.append(uu)
            if rere[2] == '-----------------':
                rere[2] = 0
            print("硬件单通道数量读取：", int(rere[2]))
            count = int(rere[2])
        except Exception as e:
            print(e.__str__())
            count = None
        finally:
            self.destroy()
        return count

    def get_linux_data_hil(self):
        try:

            stdin, stdout, stderr = self.client.exec_command(f'cat /tmp/indexToName.json')
            result = stdout.read().decode()
            index_can = json.loads(result)["can"]
            can_ch = ""
            # print(index_can)
            for index in index_can:
                if index['index'] == 0:
                    print(index)
                    can_ch = index['name']

            stdin, stdout1, stderr = self.client.exec_command(f'ifconfig {can_ch}')
            result1 = stdout1.read().decode()
            # print(result)
            re_list = result1.split("\n")
            re = re_list[-6:-1]
            rere = []
            for i in re:
                uu = i.replace("   ", "")
                uuu = uu.split(" ")
                rere.append(uuu)
            expect_v_d = {}
            for u in rere:
                if len(u) > 1:
                    k = str(u[2]) + "_" + str(u[3])
                    v = int(u[4])
                    expect_v_d[k] = v
            print(expect_v_d)
            count = expect_v_d

        except Exception as e:
            print(e.__str__())
            count = None
        finally:
            self.destroy()
        return count

    def get_linux_data_lin(self):
        """
        实验运行中才能取到数据
        """
        try:

            stdin, stdout1, stderr = self.client.exec_command(
                f'echo "lin_count_recv_show()" > /sys/class/lin/run ; cat /sys/class/lin/log')
            # stdin, stdout0, stderr = self.client.exec_command(
            #     f'echo "lin_count_recv_clr()" > /sys/class/lin/run ; cat /sys/class/lin/log')
            result = stdout1.read().decode()
            print(result)
            re_list = result.split("\n")
            re_list1 = str(re_list[4]).split("|")
            rere = []
            for i in re_list1:
                uu = i.replace(" ", "")
                rere.append(uu)
            if rere[1] == '-----------------':
                rere[1] = 0
            print("硬件单通道帧数", int(rere[1]))
            count = int(rere[1])
        except Exception as e:
            print(e.__str__())
            count = None
        finally:
            self.destroy()
        return count

    def get_linux_data_from_ifconfig(self, ch):
        if "eth" in ch and "rtpc" not in ch:
            ch = f"rtpc-{ch}"

        try:
            stdin, stdout1, stderr = self.client.exec_command(f'ifconfig {ch}')
            result1 = stdout1.read().decode()
            # print(result)
            re_list = result1.split("\n")
            re = re_list[-6:-1]
            rere = []
            for i in re:
                uu = i.replace("   ", "")
                uuu = uu.split(" ")
                rere.append(uuu)
            expect_v_d = {}
            for u in rere:
                if len(u) > 1:
                    k = str(u[2]) + "_" + str(u[3])
                    v = int(u[4])
                    expect_v_d[k] = v
            print(expect_v_d)
            count = [expect_v_d["TX_packets"], expect_v_d["TX_errors"], expect_v_d["RX_packets"], expect_v_d["RX_errors"]]

        except Exception as e:
            print(e.__str__())
            count = None
        finally:
            self.destroy()
        return count

    def get_linux_data_FlexRay(self):
        """
        实验运行中才能取到数据
        """
        try:
            stdin, stdout, stderr = self.client.exec_command(
                f'echo "flexray_frames_count(0)" > /sys/class/flexray/run ; cat /sys/class/flexray/log')
            result = stdout.read().decode()
            print(result)
            re_list = result.split("\n")
            re_tx = {}
            for i in re_list:
                i_list = i.split(" ")
                if "Tx" in i and "flexray0" in i and int(i_list[-1]) > 0:
                    ch = "flexray1_tx"
                    ch_msg = i_list[-1]
                    re_tx[ch] = ch_msg

            print(re_tx)

            stdin, stdout1, stderr = self.client.exec_command(
                f'echo "flexray_frames_count(1)" > /sys/class/flexray/run ; cat /sys/class/flexray/log')
            # stdin, stdout, stderr = client.exec_command(f'echo "flexcan_count_clr()" > /sys/class/wrapcan/run ;')
            result = stdout1.read().decode()
            print(result)
            re_list = result.split("\n")
            re_rx = {}
            for i in re_list:
                i_list = i.split(" ")
                if "Rx" in i and "flexray1" in i and int(i_list[-1]) > 0:
                    ch = "flexray2_rx"
                    ch_msg = i_list[-1]
                    re_rx[ch] = ch_msg
            print(re_rx)

            # arm_result = {"arm_flexray1_tx": int(re0['flexray1_tx']), "arm_flexray2_rx": int(re['flexray2_rx'])}
            arm_result = [int(re_tx['flexray1_tx']), int(re_rx['flexray2_rx'])]
            print(arm_result)
            # return arm_result

        except Exception as e:
            print(e.__str__())
            arm_result = None
        finally:
            self.destroy()
        return arm_result

    def get_linux_data_eth(self, ch):
        return self.get_linux_data_from_ifconfig(ch)

    def get_env_num(self):
        env_num = 0
        try:
            stdin, stdout1, stderr = self.client.exec_command(
                f'env LD_LIBRARY_PATH=/opt/mrtd/lib /opt/mrtd/bin/aarch64/drt_env_shm_dump')
            result1 = stdout1.read().decode()
            print("env_num:", result1)
            env_num = result1[result1.find(":")+1:]
        except Exception as e:
            print(e.__str__())
        finally:
            self.destroy()
        return env_num

if __name__ == '__main__':
    c = GetHILData("192.168.99.100", "root", "123456")
    co = c.get_linux_data_can(1,"tx")
    print(co)
