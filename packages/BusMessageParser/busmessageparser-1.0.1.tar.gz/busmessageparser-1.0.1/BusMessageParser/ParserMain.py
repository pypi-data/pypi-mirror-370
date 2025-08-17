#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusMessageParser.CommonBasic import ParserCommonBasic


class Parser:
    """
    校验执行主入口
    """
    def __init__(self, files, bus_type, parser_type, file_type):
        self.files = files
        self.bus_type = bus_type.lower()
        self.parser_type = parser_type.lower()
        self.file_type = file_type.lower()

    def start(self):
        match self.bus_type:
            case "can":
                parser = ParserCommonBasic(self.files, self.parser_type, self.file_type)
                count = parser.run()
                return count
            case "lin":
                pass
            case "flexray":
                pass
            case "eth":
                pass
            case _:
                print(f"暂不支持的总线类型'{self.bus_type}'")