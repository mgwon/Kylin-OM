"""
Filename: MetaGPT/examples/build_customized_multi_agents.py
Created Date: Wednesday, November 15th 2023, 7:12:39 pm
Author: garylin2099
"""
import re
import subprocess
import fire
import pymysql
import psutil
import pandas as pd
import time
import datetime
import argparse

from operation import linux_commands_running
from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team
from colletchange import collect_set1
from findbottleneck import getbottleneck
from workspace.getdata import get_mysql_data

def parse_code(rsp):
    pattern = r"```python(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    code_text = match.group(1) if match else rsp
    return code_text
 # info= 瓶颈的字典 函数 信息变字典
#多加一个agent
# 分析信息 得出优化方向
#Linux系统运行Mysql场景时，出现了瓶颈，信息为{info}，为了实现{idea}的linux系统调优，请给出修改Swappiness参数,TCP 参数{}等参数的数值的方向|
Init_info:list=[]
class SimpleWriteLysis(Action):

    #info : list = getbottleneck(time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfo.csv")

    name: str = "SimpleWriteLysis"
    PROMPT_TEMPLATE: str = """
    Linux系统运行Mysql场景时，出现了瓶颈，目前指标为"{information}"
    为了实现{idea}的linux系统调优，提高上述指标，请给出修改Swappiness参数,TCP 参数等参数数值的方向
    返回‘’‘修改参数的方向‘’‘,，
    用中文回答，修改参数的方向：
    """

    info: list = getbottleneck(time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfo.csv")
    information: str = ""
    info_index :list = ["I/O read", "I/O write", "qps", "tps"]


    async def run(self, idea: str):
        global Init_info
        Init_info=self.info

        for i in range(len(self.info)):
            self.information += self.info_index[i] + ':' + self.info[i] + ','

        prompt = self.PROMPT_TEMPLATE.format(idea=idea, information=self.information)

        rsp = await self._aask(prompt)

        code_txt = parse_code(rsp)

        return code_txt


class SimpleAnalyst(Role):
    name: str = "Marry"
    profile: str = "SimpleAnalyst"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([SimpleWriteLysis])

Instruction: str=""

class SimpleWriteCode(Action):

    #只写指令

    PROMPT_TEMPLATE: str = """
    目前已经有如下信息：{inform}。请以Human的信息为目标，跟据SimpleAnalyst给出的调优方向，生成linux终端的系统调参指令,并在每条指令开头加/i，结尾加上“/r”：
    返回’‘’生成的linux终端系统调参指令:‘’‘
    仅生成指令：
    """
    name: str = "SimpleWriteCode"

    async def run(self, inform: str):
        prompt = self.PROMPT_TEMPLATE.format(inform=inform)

        rsp = await self._aask(prompt)
        global Instruction
        Instruction=str(rsp)
        #print(rsp)
        #code_text = parse_code(rsp)

        return rsp


class SimpleCoder(Role):
    name: str = "Alice"
    profile: str = "SimpleCoder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([SimpleWriteLysis,SimpleWriteTest])
        self.set_actions([SimpleWriteCode])

errlist:list=[]
outlist:list=[]
runable_code:str=""
class SimpleWriteTest(Action):
    #print(str(SimpleWriteCode))
    # 直接测试 跑飞的函数 执行上面的指令

    PROMPT_TEMPLATE: str = """
    背景：{context}
    为SimpleWriteCode生成的linux指令经执行，终端返回报错信息为{err}，执行信息为{out}
    对其中无法执行的指令，作出修改，并返回所有指令。
    返回’‘’linux指令‘’‘不包含其他文本，
    linux指令：
    """
    result : str =" "

    name: str = "SimpleWriteTest"

    async def run(self, context: str, k: int = 3):
        code_text:str=""
        # 缺 监控终端 把结果扒回来
        # 使用 history 命令获取历史命令列表，并获取最后一条命令
        # context/ result
        global Instruction
        global errlist,outlist
        errlist=[]
        outlist=[]
        outlist,errlist=linux_commands_running(Instruction)
        errstring=""
        outstring=""
        for s in errlist:
            errstring+=s
            errstring+=","
        for s in outlist:
            outstring+=s
            outstring+=","
        prompt = self.PROMPT_TEMPLATE.format(context=context,err=errstring,out=outstring)
        rsp = await self._aask(prompt)

        code_text = parse_code(rsp)
        global runable_code
        runable_code=str(code_text)

        return code_text


class SimpleTester(Role):
    name: str = "Bob"
    profile: str = "SimpleTester"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteTest])
        # self._watch([SimpleWriteCode])
        self._watch([SimpleWriteCode, SimpleWriteReview])  # feel free to try this too

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        # context = self.get_memories(k=1)[0].content # use the most recent memory as context
        context = self.get_memories()  # use all memories as context

        code_text = await todo.run(context, k=5)  # specify arguments
        msg = Message(content=code_text, role=self.profile, cause_by=type(todo))

        return msg


class SimpleWriteReview(Action):


    PROMPT_TEMPLATE: str = """
    背景: {context}
    经测试SimpleTester给出的指令，执行结果为：qps：{qps},tps:{tps},IO写：{IO_w},IO读:{IO_r}    
    初始的性能为：qps：{qps_or},tps:{tps_or},IO写：{IO_w_or},IO读:{IO_r_or}  
    请判断，SimpleTester给出的指令是否优化了当前系统，并给出评价以便进一步优化系统的以上指标

    """

    name: str = "SimpleWriteReview"

    async def run(self, context: str):
        # qps tps I/O 再测一遍 小李
        # with open("start_end.txt","r") as file:
        #     last_line=None
        #     for line in file:
        #         last_line = line.strip()
        #     if last_line:
        #     start_time=
        #     end_time
        # collect_set1(start_time,end_time,1,0,0)
        global runable_code
        outls:list=[]
        errls: list = []
        result:bool=[]
        IO_w:float=0
        IO_r: float = 0
        tps:float=0
        qps:float=0

        outls,errls,result,IO_w,IO_r,tps,qps=get_mysql_data(runable_code)

        prompt = self.PROMPT_TEMPLATE.format(context=context,IO_w=IO_w,IO_r=IO_r,qps=qps,tps=tps,IO_w_or=Init_info[0],IO_r_or=Init_info[1],tps_or=Init_info[2],qps_or=Init_info[3])

        rsp = await self._aask(prompt)

        return rsp


class SimpleReviewer(Role):
    name: str = "Charlie"
    profile: str = "SimpleReviewer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteReview])
        self._watch([SimpleWriteTest])


async def main(
    idea: str = "Linux系统下，使用Mysql出现瓶颈，请生成可以优化系统tps，qps，磁盘I/O三个指标的的linux系统终端指令",
    investment: float = 3.0,
    n_round: int = 5,
    add_human: bool = False,
):
    logger.info(idea)

    team = Team()
    team.hire(
        [
            SimpleAnalyst(),
            SimpleCoder(),
            SimpleTester(),
            SimpleReviewer(is_human=add_human),
        ]
    )

    team.invest(investment=investment)
    team.run_project(idea)
    await team.run(n_round=5)


if __name__ == "__main__":
    fire.Fire(main)