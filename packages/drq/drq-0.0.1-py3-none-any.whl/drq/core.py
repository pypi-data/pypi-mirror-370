# -*- coding: utf-8 -*-
"""
多功能娱乐工具箱
用法：
    >>> import drq
    >>> drq.help()          # 查看全部功能
    >>> drq.idiom_chain("画龙点睛")
"""
from __future__ import annotations

import json
import random
import re
import sys
from typing import List, Dict, Any

import requests
from urllib.parse import quote

# ------------------------------------------------------------------
# 基础工具
# ------------------------------------------------------------------
def _get(url: str, timeout: int = 5) -> Dict[str, Any]:
    """统一 GET 请求，返回 json 字典；失败返回空字典。"""
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return {}

# ------------------------------------------------------------------
# 句子 / 毒鸡汤
# ------------------------------------------------------------------
def get_sentence() -> str:
    """每日一言，返回「句子 —— 来源」"""
    data = _get("https://v1.hitokoto.cn")
    sentence = data.get("hitokoto", "网络异常")
    source = data.get("from", "未知来源")
    return f"{sentence} —— {source}"

def toxic_soup() -> str:
    """毒鸡汤一句"""
    try:
        return requests.get(
            "https://api.ixiaowai.cn/ylapi/djtp.php", timeout=3
        ).text.strip()
    except Exception as e:
        return f"{e}"

# ------------------------------------------------------------------
# 成语接龙
# ------------------------------------------------------------------
def idiom_chain(prev: str) -> str:
    """根据上一个成语尾字返回可接龙的成语列表"""
    if not re.fullmatch(r"[\u4e00-\u9fa5]{4}", prev):
        return "请输入四字成语哦~"

    last = prev[-1]
    url = f"https://chengyu.911cha.com/so_{quote(last)}.html"
    try:
        html = requests.get(url, timeout=5).text
        ids = set(re.findall(r">([\u4e00-\u9fa5]{4})<", html))
        if not ids:
            return f"没有找到以「{last}」开头的成语"
        ids = sorted(ids)[:5]
        return f"可接龙：{' / '.join(ids)}（共{len(ids)}+ 个，展示前 5）"
    except Exception as e:
        return f"接口调用失败：{e}"

# ------------------------------------------------------------------
# 天气
# ------------------------------------------------------------------
def weather(city: str) -> str:
    """查询城市实时天气"""
    data = _get(f"https://wttr.in/{quote(city)}?format=j1")
    try:
        cur = data["current_condition"][0]
        desc = cur["weatherDesc"][0]["value"]
        t_c, t_f = cur["temp_C"], cur["temp_F"]
        wind = cur["windspeedKmph"]
        hum = cur["humidity"]
        return (
            f"{city} 当前天气：{desc}\n"
            f"温度：{t_c}°C / {t_f}°F\n"
            f"风速：{wind} km/h\n"
            f"湿度：{hum}%"
        )
    except (KeyError, TypeError):
        return f"未查询到「{city}」的天气信息，请检查城市名"

# ------------------------------------------------------------------
# 小游戏
# ------------------------------------------------------------------
def guess_number() -> None:
    """猜数字：1-100，6 次机会"""
    secret = random.randint(1, 100)
    for i in range(6, 0, -1):
        try:
            n = int(input(f"还剩{i}次，猜："))
            if n == secret:
                print("恭喜猜对！🎉")
                return
            print("猜大了！" if n > secret else "猜小了！")
        except ValueError:
            print("请输入整数！")
    print(f"机会用完，答案是 {secret}")

def rps() -> None:
    """石头剪刀布：三局两胜"""
    name = ["石头", "剪刀", "布"]
    win_msg = ((0, 1), (1, 2), (2, 0))  # 谁赢谁
    u, c = 0, 0
    while u < 2 and c < 2:
        try:
            user = int(input("0石头 1剪刀 2布："))
            if user not in (0, 1, 2):
                continue
        except ValueError:
            continue
        pc = random.randint(0, 2)
        print(f"你：{name[user]}  电脑：{name[pc]}")
        if (user, pc) in win_msg:
            u += 1
            print("你赢这局！")
        elif user == pc:
            print("平局")
        else:
            c += 1
            print("电脑赢这局！")
    print("最终结果：你赢了🎉" if u == 2 else "电脑赢了😢")

# ---------- 附加彩蛋 ----------
def p_x() -> None:
    """父母性别查询器：在终端循环读取输入，直到空行结束"""
    try:
        while (s := input("输入称呼（父亲/母亲，空行退出）：").strip()):
            print("男" if s == "父亲" else "女" if s == "母亲" else "?")
    except (EOFError, KeyboardInterrupt):
        pass

def nonsense() -> str:
    """随机生成一句废话"""
    prefix = ["其实吧，", "说真的，", "仔细想想，", "说白了，"]
    middle = ["这事儿吧，它就是那么个事儿", "你懂的，也就那样", "该怎么样还怎么样", "反正结果都差不多"]
    suffix = ["，对吧？", "罢了。", "而已。", "啦~"]
    return random.choice(prefix) + random.choice(middle) + random.choice(suffix)


# 帮助系统
def help() -> None:
    """打印所有公开函数的功能与用法示例"""
    docs = {
        "get_sentence": "获取一句随机文艺句子",
        "toxic_soup": "获取一句毒鸡汤",
        "idiom_chain(prev: str)": "成语接龙：给出上一成语，返回可接龙列表",
        "weather(city: str)": "查询城市天气",
        "guess_number()": "终端小游戏：猜数字",
        "rps()": "终端小游戏：石头剪刀布",
        "p_x()": "终端彩蛋：输入“父亲/母亲”返回性别",
        "nonsense()": "随机生成一句废话",
        "help()": "打印本帮助",
    }
    for sig, desc in docs.items():
        print(f"{sig:<35} {desc}")


if __name__ == "__main__":
    help()