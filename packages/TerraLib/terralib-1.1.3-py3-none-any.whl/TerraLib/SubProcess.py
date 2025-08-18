# coding=utf-8
import enum
import os
import subprocess


class RC_CODE(enum.Enum):
    RC_PASS = 0
    RC_FAIL = 1
    RC_EXCEPTION = -1


class RunCMD():
    def __init__(self):
        self.active_info = False
        self.use_mylog = False
        self.show_cmd = True
        self.silent = False
        self.encoding = "utf-8"

    def __bytes2str(self, bytes_data):
        """
        bytes to str
        :param bytes_data:
        :return:
        """
        try:
            return bytes_data.decode(self.encoding)
        except:
            return bytes_data.decode("gbk", "ignore")

    def run_command(self, command, cwd=os.getcwd(), skip_blank_lines=False):
        if self.show_cmd:
            print(f"Run command:{command} at '{cwd}'")
        if self.active_info:
            lines = []
            p = None
            try:
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     universal_newlines=False, cwd=cwd)
                while p.poll() is None:
                    line = self.__bytes2str(p.stdout.readline())
                    if skip_blank_lines and not line.strip():
                        continue
                    if not self.silent:
                        print(line.strip())
                    lines.append(line)
                try:
                    last_line = self.__bytes2str(p.stdout.readline())
                    if not self.silent:
                        print(last_line.strip())
                    lines.append(last_line)
                except:
                    pass

                if p.returncode == 0:
                    return RC_CODE.RC_PASS, lines
                else:
                    return RC_CODE.RC_FAIL, lines

            except Exception as ex:
                print(str(ex))
                lines.append(str(ex))
                return RC_CODE.RC_EXCEPTION, lines
            finally:
                try:
                    p.terminate()
                except:
                    pass
        else:
            lines = []
            p = None
            try:
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     universal_newlines=False, cwd=cwd)
                out, err = p.communicate()
                lines = [x + "\n" for x in self.__bytes2str(out).split('\n')]
                if p.returncode == 0:
                    if not self.silent:
                        for line in lines:
                            print(line.strip())
                    return RC_CODE.RC_PASS, lines
                else:
                    for line in lines:
                        print(line.strip())
                    return RC_CODE.RC_FAIL, lines
            except Exception as ex:
                print(str(ex))
                lines.append(str(ex))
                return RC_CODE.RC_EXCEPTION, lines
            finally:
                try:
                    p.terminate()
                except:
                    pass
