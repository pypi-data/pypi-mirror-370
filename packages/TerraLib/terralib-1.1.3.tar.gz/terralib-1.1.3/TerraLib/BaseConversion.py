import re
import random
import sys


class BinValue:
    def __init__(self, origin, type, bin_t, width, isRandom=False):
        self.origin = origin
        self.type = type
        self.bin_t = bin_t
        self.binV = bin_t[2:] if bin_t else None
        self.width = int(width) if width else None
        self.isRandom = isRandom


class CommonMethodForAsic:
    @staticmethod
    def any2bin(value, width=8, info=""):
        value = str(value).strip().lower()  # it is very strange, 8'hFF have different result with 8'hff even with re.I
        value = value.replace("_", "")
        # so i add lower()
        # random

        if value == "rsvd" or value == "reserved":
            return BinValue("", None, None, None)

        # 0x12、3'b001、4'd1、10h、10b、10d
        # 4'b1100、2'o17、3'd12、8'hff
        reg_bin1 = "^(\d*)'?b([01]+)$"  # 4'b1100
        reg_bin2 = "^([01]+)b$"  # 1100b
        reg_bin3 = "^0b([01]+)$"  # 0b1100

        reg_oct1 = "^(\d*)'?o([0-7]+)$"  # 2'o17
        reg_oct2 = "^([0-7]+)o$"  # 17o
        reg_oct3 = "^0([0-7]+)$"  # 017

        reg_dec1 = "(^\d*)'?d(\d+)$"  # 3'd110
        reg_dec2 = "^([1-9]\d*)d?$"  # 110d
        reg_dec3 = "^0$"  # 0

        reg_hex1 = "^(\d*)'?h([0-9,abcdef]+)$"  # 2'h1f
        reg_hex2 = "^([0-9,abcdef]+)h$"  # 1fh
        reg_hex3 = "^0x([0-9,abcdef]+)$"  # 0x1f

        reg_rand = "^rand(om)?$"

        # random
        if re.match(reg_rand, value, re.I):
            r_value = random.randint(0, pow(2, 32) - 1)
            f = "0b{:0%sb}" % width
            val = f.format(int(r_value))
            return BinValue(value, "dec", val, None, True)
        # bin
        if re.match(reg_bin1, value, re.I):
            width = re.sub(reg_bin1, "\\1", value, re.I)
            val = re.sub(reg_bin1, "\\2", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 2))
            return BinValue(value, "bin", val, width)
        if re.match(reg_bin2, value, re.I):
            val = re.sub(reg_bin2, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 2))
            return BinValue(value, "bin", val, None)
        if re.match(reg_bin3, value, re.I):
            val = re.sub(reg_bin3, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 2))
            return BinValue(value, "bin", val, None)

        # oct
        if re.match(reg_oct1, value, re.I):
            width = re.sub(reg_oct1, "\\1", value, re.I)
            val = re.sub(reg_oct1, "\\2", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 8))
            return BinValue(value, "oct", val, width)
        if re.match(reg_oct2, value, re.I):
            val = re.sub(reg_oct2, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 8))
            return BinValue(value, "oct", val, None)
        if re.match(reg_oct3, value, re.I):
            val = re.sub(reg_oct3, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 8))
            return BinValue(value, "oct", val, None)

        # dec
        if re.match(reg_dec1, value, re.I):
            width = re.sub(reg_dec1, "\\1", value, re.I)
            val = re.sub(reg_dec1, "\\2", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val))
            return BinValue(value, "dec", val, width)
        if re.match(reg_dec2, value, re.I):
            val = re.sub(reg_dec2, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val))
            return BinValue(value, "dec", val, None)
        if re.match(reg_dec3, value, re.I):
            f = "0b{:0%sb}" % width
            val = f.format(int(0))
            return BinValue(value, "dec", val, None)

        # hex
        if re.match(reg_hex1, value, re.I):
            x = re.findall(reg_hex1, value, re.I)
            width = re.sub(reg_hex1, "\\1", value, re.I)
            val = re.sub(reg_hex1, "\\2", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 16))
            return BinValue(value, "hex", val, width)
        if re.match(reg_hex2, value, re.I):
            val = re.sub(reg_hex2, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 16))
            return BinValue(value, "hex", val, None)
        if re.match(reg_hex3, value, re.I):
            val = re.sub(reg_hex3, "\\1", value, re.I)
            f = "0b{:0%sb}" % width
            val = f.format(int(val, 16))
            return BinValue(value, "hex", val, None)
        if value != "" and value != "none":
            print(
                '[AsicCommonMethod][Error]:"%s" can not be recognized as any format, it can not be translate to bin! %s' % (
                    value, info))
            sys.exit(1)
        return BinValue(value, None, None, None, False)

    @staticmethod
    def bin2hex(value, width="", info=""):
        """
        bin translate to width'h1f format
        :param value:
        :param width:
        :return:
        """
        reg_bin1 = "^(\d*)'?b([01]+)$"  # 4'b1100
        reg_bin2 = "^([01]+)b$"  # 1100b
        reg_bin3 = "^0b([01]+)$"  # 0b1100

        value = str(value).strip()
        if re.match(reg_bin1, value, re.I):
            val = re.sub(reg_bin1, "\\2", value, re.I)
            f = "'h{:0%sx}" % width
            val = f.format(int(val, 2))
            return val
        if re.match(reg_bin2, value, re.I):
            val = re.sub(reg_bin2, "\\1", value, re.I)
            f = "'h{:0%sx}" % width
            val = f.format(int(val, 2))
            return val
        if re.match(reg_bin3, value, re.I):
            val = re.sub(reg_bin3, "\\1", value, re.I)
            f = "'h{:0%sx}" % width
            val = f.format(int(val, 2))
            return val

        if value != "" and value != "none":
            print(
                '[AsicCommonMethod][Error]:"%s" can not be recognized as any bin format, it can not be translate to hex! %s' % (
                    value, info))
            sys.exit(1)
        return value

    @staticmethod
    def any2bin_test(value, width=8, info=""):
        value = str(value).strip().lower()  # it is very strange, 8'hFF have different result with 8'hff even with re.I
        # so i add lower()
        # random
        if value == "rsvd" or value == "reserved":
            return False
        # 0x12、3'b001、4'd1、10h、10b、10d
        # 4'b1100、2'o17、3'd12、8'hff
        reg_bin1 = "^(\d*)'?b([01]+)$"  # 4'b1100
        reg_bin2 = "^([01]+)b$"  # 1100b
        reg_bin3 = "^0b([01]+)$"  # 0b1100

        reg_oct1 = "^(\d*)'?o([0-7]+)$"  # 2'o17
        reg_oct2 = "^([0-7]+)o$"  # 17o
        reg_oct3 = "^0([0-7]+)$"  # 017

        reg_dec1 = "(^\d*)'?d(\d+)$"  # 3'd110
        reg_dec2 = "^([1-9]\d*)d?$"  # 110d
        reg_dec3 = "^0$"  # 0

        reg_hex1 = "^(\d*)'?h([0-9,abcdef]+)$"  # 2'h1f
        reg_hex2 = "^([0-9,abcdef]+)h$"  # 1fh
        reg_hex3 = "^0x([0-9,abcdef]+)$"  # 0x1f

        reg_rand = "^rand(om)?$"

        if re.match(reg_rand, value):
            return True
        # bin
        if re.match(reg_bin1, value) or re.match(reg_bin2, value) or re.match(reg_bin3, value):
            return True
        # oct
        if re.match(reg_oct1, value) or re.match(reg_oct2, value) or re.match(reg_oct3, value):
            return True
        # dec
        if re.match(reg_dec1, value) or re.match(reg_dec2, value) or re.match(reg_dec3, value):
            return True
        # hex
        if re.match(reg_hex1, value) or re.match(reg_hex2, value) or re.match(reg_hex3, value):
            return True
        if value != "" and value != "none":
            return False
        return False

    @staticmethod
    def get_bit_width(val):
        return 1 if val == 0 else val.bit_length()


def test():
    test_list = ["10", "10b", "3'b001", "4'b1100", "2'o17", "017", "4'd1", "10d", "3'd12", "10h", "8'hff", "0x12"]
    print("Test Result: \n"
          "Value{:8}Type{:6}BinValue{:18}BinValue2{:21}Width{:10}\n"
          "____________________________________________________________________________________".format("", "", "", "",
                                                                                                        ""))
    for t in test_list:
        result = CommonMethodForAsic.any2bin(t)
        print("{:13}{:10}{:26}{:30}{:10}".format(result.origin, result.type, result.bin_t, result.binV,
                                                 str(result.width)))


if __name__ == '__main__':
    test()
    print(CommonMethodForAsic.bin2hex("0b1111", "2"))
    print(CommonMethodForAsic.bin2hex("1111b", "3"))
    print(CommonMethodForAsic.bin2hex("b1111", "2"))
