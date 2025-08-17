# BusMessageParser Package

# Example:

# 1.校验can总线报文文件中是否丢帧:
from BusMessageParser.ParserMain import *

can_parser = Parser('../文件路径', 'can', 'count', 'blf')

count = can_parser.start()

assert count == 110

# 2.校验can总线报文文件中是否有重复帧:
from BusMessageParser.ParserMain import *

can_parser = Parser('../文件路径', 'can', 'duplicate', 'blf')

count = can_parser.start()

assert count == 110