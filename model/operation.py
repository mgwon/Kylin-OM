import re
import subprocess


def extract_linux_commands(text):
    """
    从文本中提取可能的Linux指令。假设指令以回车分隔，并且指令后可能跟有其他文字。

    参数:
    text (str): 包含可能的Linux指令的文本。

    返回:
    list: 提取的Linux指令列表。
    """
    # 扩展正则表达式，包含更多常见的Linux指令和sudo指令
    pattern = re.compile(r'/i\s*(.*?)\s*/r')
    print("text:",text)
    commands = pattern.findall(text)

    # 去掉多余的空白字符
    commands = [cmd.strip() for cmd in commands]
    print("commands:",commands)
    return commands
def linux_commands_running(cmd_str):
    commands = extract_linux_commands(cmd_str)
    stdout_list = []
    stderr_list = []
    for tem in commands:
        result = subprocess.run(tem, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_list.append(result.stdout)
        stderr_list.append(result.stderr)

    print("errlist:",stderr_list)
    print("outlist:",stdout_list)
    return stdout_list,stderr_list



# 示例用法
#text = "下面是我的指令：/isudo ls -l /r/n /iecho hello world /r 我看看你怎么识别这种字符串， /isudo systemctl restart apache2/r"
#extracted_commands = extract_linux_commands(text)
#print("提取的Linux指令:", extracted_commands)