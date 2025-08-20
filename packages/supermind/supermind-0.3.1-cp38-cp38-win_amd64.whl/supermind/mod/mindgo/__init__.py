# @Author: xiewenqian <int>
# @Date:   2018-05-07T10:10:33+08:00
# @Email:  wixb50@gmail.com
# @Last modified by:   int
# @Last modified time: 2018-05-07T16:27:14+08:00


import click
import pandas as pd
from mgquant import cli
from mgquant.events import EVENT


__config__ = {
    # 设置优先级最高
    "priority": 0,
    # 启动输出到kafka
    "enable_kafka_output": True,
    # 每日最后一个事件
    "daily_last_event": EVENT.POST_AFTER_TRADING,
    # 是否每日收集trade落库
    "daily_collect_trade": True,
    # 用于标记persist_provider
    "persist_provider": None,
    # 运行风格
    "style": "NORMAL",
}


def load_mod():
    from supermind.mod.mindgo.mod import MindgoMod
    return MindgoMod()


@cli.command()
def runserver(**kwargs):
    """
    Run mgquant as a daemonservice
    """
    from supermind.mod.mindgo.service import DaemonService
    click.echo("HxBacktest Start")
    DaemonService().run()
    click.echo("HxBacktest End")


@cli.command()
@click.help_option('-h', '--help')
@click.option('-sm', '--stock-market', 'stock_market', type=click.Choice(['STOCK', 'METAL', 'FOREX', 'FUND']), default="STOCK")
@click.option('-fq', '--frequency', 'frequency', type=click.Choice(['DAILY', 'MINUTE']), default="DAILY")
@click.option('-s', '--start-time', 'start_time', type=pd.Timedelta, required=True)
@click.option('-e', '--end-time', 'end_time', type=pd.Timedelta, required=True)
@click.option('-t', '--target-time', 'target_time', type=pd.Timedelta, multiple=True, help="指定运行某些时间点")
def runsimulate(target_time, **kwargs):
    """
    Run mgquant simulate as a daemonservice
    几种运行方式为(当前dt是否运行在mod内自行判断，支持跨天)：
    mgquant runsimulate -sm STOCK -fq DAILY -s 09:00:00 -e 15:30:00 -t 09:00:00 -t 09:30:00 # 检测运行股票的日级before_trading时间点和开盘时间点
    mgquant runsimulate -sm STOCK -fq MINUTE -s 09:00:00 -e 15:30:00 # 检测运行股票的分钟时间点
    mgquant runsimulate -sm STOCK -fq DAILY -s 09:00:00 -e 09:00:00 # 检测运行股票的日级before_trading时间点
    说明：第一种适用于一天内需要运行多个时间点；第二种适用于一天时间段内需要持续运行；第三种是第二种的DAILY体现(可用第一种替换)
    """
    from supermind.mod.mindgo.simulate import SimulateService
    click.echo("HxMGQuantBroker Start")
    if target_time:
        SimulateService(**kwargs).run_target(target_time)
    else:
        SimulateService(**kwargs).run()
    click.echo("HxMGQuantBroker End")
