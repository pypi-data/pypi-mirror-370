import os
import re
import sys
import configparser
import hashlib
import yagmail


def calculate_file_hash(file_path, algorithm="md5"):
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class Config:

    def __init__(self, config_file: str = "config.ini") -> None:
        self.config_file_name = config_file
        cfp = configparser.ConfigParser()
        cfp.read(config_file, encoding="utf-8")
        self._cfp = cfp
        self.md5_hash = calculate_file_hash(config_file)

    def update_config(self):
        md5_hash = calculate_file_hash(self.config_file_name)
        if md5_hash == self.md5_hash:
            return False

        self.md5_hash = md5_hash
        cfp = configparser.ConfigParser()
        cfp.read(self.config_file_name, encoding="utf-8")
        self._cfp = cfp
        return True

    def get_value(self, key: str, default_value: str = None) -> str:
        """
        key的格式: section.option

        [section]
        option=value
        """
        if "." in key:
            ll = key.split(".")
            section = ll[0]
            option = ll[1]
            if self._cfp.has_option(section, option):
                return self._cfp.get(section, option)
            return default_value
        return default_value

    def get_value_list(self, key: str, default_value: list = []) -> list:
        """
        key的格式: section.option
        返回同一个section下符合正则表达式的所有key的值

        [section]
        option1 = value1
        option2 = value2
        key3    = value3

        section.option* 输出 [value1,value2]

        """
        if "." in key:
            ll = key.split(".")
            section = ll[0]
            option = ll[1]
            if self._cfp.has_section(section):
                rt = []
                for i in self._cfp.options(section):
                    if re.match(option, i, flags=0) is not None:
                        rt.append(self._cfp.get(section, i))
                return rt
            return default_value
        return default_value

    def get_list(self, key: str, default_value: list = []) -> list:
        """
        key的格式: section.option

        [section]
        option=v1,v2,v3,v4
        @return [v1, v2, v3, v4]
        """
        str_val = self.get_value(key, "")
        if not str_val:
            return default_value
        str_list = [i.strip() for i in str_val.split(",") if i.strip()]
        return str_list

    def get_floatlist(self, key: str, default_value: list = []) -> list:
        """
        key的格式: section.option

        [section]
        option=v1,v2,v3,v4
        @return [v1, v2, v3, v4]
        """
        str_val = self.get_value(key, "")
        if not str_val:
            return default_value
        str_list = [float(i.strip()) for i in str_val.split(",") if i.strip()]
        return str_list

    def get_intlist(self, key: str, default_value: list = []) -> list:
        """
        key的格式: section.option

        [section]
        option=v1,v2,v3,v4
        @return [v1, v2, v3, v4]
        """
        str_val = self.get_value(key, "")
        if not str_val:
            return default_value
        str_list = [int(i.strip()) for i in str_val.split(",") if i.strip()]
        return str_list

    def get_floatvalue(self, key: str, default_value: float = None) -> float:
        """
        key的格式: section.option

        [section]
        option=value
        """
        if "." in key:
            ll = key.split(".")
            section = ll[0]
            option = ll[1]
            if self._cfp.has_option(section, option):
                return self._cfp.getfloat(section, option)
            return default_value
        return default_value

    def get_intvalue(self, key: str, default_value: int = None) -> int:
        """
        key的格式: section.option

        [section]
        option=value
        """
        if "." in key:
            ll = key.split(".")
            section = ll[0]
            option = ll[1]
            if self._cfp.has_option(section, option):
                return self._cfp.getint(section, option)
            return default_value
        return default_value

    def get_booleanvalue(self, key: str, default_value: bool = None) -> bool:
        """
        key的格式: section.option

        [section]
        option=value
        """
        if "." in key:
            ll = key.split(".")
            section = ll[0]
            option = ll[1]
            if self._cfp.has_option(section, option):
                return self._cfp.getboolean(section, option)
            return default_value
        return default_value


def send_email_with_attachment(subject, to, contents, attachments):
    CONFIG_FILE = os.path.expanduser("~/.config/mytot/config.ini")
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} is not exists")
        return
    cfg = Config(CONFIG_FILE)
    # 163邮箱的SMTP服务器地址
    smtp_server = cfg.get_value("email.smtp_server", "")
    username = cfg.get_value("email.username", "")
    password = cfg.get_value("email.password", "")
    if smtp_server == "":
        print("please set smtp_server")
        return
    if username == "":
        print("please set username")
        return
    default_to = cfg.get_value("email.default_to", username)

    yag = yagmail.SMTP(user=username, password=password, host=smtp_server)
    if to[0] == "":
        yag.send(
            to=[default_to], subject=subject, contents=contents, attachments=attachments
        )
    else:
        yag.send(to=to, subject=subject, contents=contents, attachments=attachments)
    yag.close()


def main():
    USAGE = "usage MAIL [email address] -s [subject] -a [attachments]"
    if len(sys.argv) < 2:
        print(USAGE)
        return
    to = sys.argv[1]
    if to[0] == "-":
        to = ""
    subject = []
    attachments = []
    begin_a = False
    begin_s = False
    for v in sys.argv:
        if v == "-s":
            begin_s = True
            begin_a = False
        elif v == "-a":
            begin_a = True
            begin_s = False
        else:
            if begin_a:
                attachments.append(v)
            if begin_s:
                subject.append(v)
    contents = ""
    send_email_with_attachment(subject, [to], contents, attachments)


if __name__ == "__main__":
    main()
