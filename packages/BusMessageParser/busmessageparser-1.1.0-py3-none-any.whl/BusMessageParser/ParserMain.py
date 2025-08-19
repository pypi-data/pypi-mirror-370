#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusMessageParser.CommonBasic.CommonFunc import CanMsgParserCommonBasic as CanMsgP
from BusMessageParser.CommonBasic.CommonFunc import LinMsgParserCommonBasic as LinMsgP
from BusMessageParser.CommonBasic.CommonFunc import FlexRayMsgParserCommonBasic as FrMsgP
from BusMessageParser.CommonBasic.CommonFunc import EthMsgParserCommonBasic as EthMsgP


def ParserStart(files, bus_type, parser_type, file_type, *args):
    bus_type = bus_type.lower()
    parser_type = parser_type.lower()
    file_type = file_type.lower()

    if parser_type == "reverse":
        if type(args) != tuple:
            raise Exception("当检验逆序帧时, 需传入'是否是单通道及是否校验ID的元组'")
        else:
            try:
                if type(args[0]) == str:
                    ParserCH = eval(args[0].capitalize())
                else:
                    ParserCH = args[0]
                if type(args[1]) == str:
                    is_IdentifyID = eval(args[1].capitalize())
                else:
                    is_IdentifyID = args[1]
                if type(ParserCH) != bool or type(is_IdentifyID) != bool:
                    raise Exception("检验逆序帧时, 传入参数均需要传入True或者False")
            except IndexError:
                raise Exception("检验逆序帧时, 传入参数数量不正确, 请确保传入参数为2个!")
            except AttributeError:
                raise Exception("检验逆序帧时, 传入参数类型不正确, 若参数中使用了(), 请在前面加上*")

    if bus_type == "eth":
        if file_type != "blf":
            raise Exception(f"eth类型报文只支持统计blf类型的文件帧数! ")
        else:
            if parser_type != "count":
                raise Exception(f"eth类型报文只支持统计 'count'! ")

    match bus_type:
        case "can":
            parser = CanMsgP(files, parser_type, file_type)
            count = parser.run(*args)
            return count
        case "lin":
            parser = LinMsgP(files, parser_type, file_type)
            count = parser.run(*args)
            return count
        case "flexray":
            parser = FrMsgP(files, parser_type, file_type)
            count = parser.run(*args)
            return count
        case "eth":
            parser = EthMsgP(files, parser_type, file_type)
            count = parser.run(*args)
            return count
        case _:
            print(f"暂不支持的总线类型'{bus_type}'")