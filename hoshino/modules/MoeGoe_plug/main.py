from pathlib import Path
from hoshino import Service, priv, aiorequests, R
import requests
import base64
from PIL import Image
from io import BytesIO
import math
import time
import calendar
import aiohttp
from .MoeGoe.commons import *
from .MoeGoe.MoeGoe import MoeGoe
from nonebot import MessageSegment
from lxml import etree
import hoshino
import asyncio
token = ''

sv_help = """请输入ai语音生成 角色id 想要说的话 ,如果要说中文片假名，就改成ai中文语音生成 角色id+想要说的话
例如 
ai语音生成 0[空格]こんばんは　将会生成宁宁说的こんばんは
ai中文语音生成 0[空格]晚上好　将会生成宁宁说的晚上好
角色id表
id: 0:绫地宁宁  15:ルイズ       30:キュルケ 45:稲叢莉音
    1:因幡爱瑠  16:ティファニア 31:ウェザリー 46:ニコラ
    2:朝武芳乃  17:イルククゥ   32:サイト 47:荒神小夜
    3:常陸茉子  18:アンリエッタ 33:ギーシュ 48:大房ひよ里
    4:丛雨      19:タバサ      34:コルベール 49:淡路萌香
    5:鞍马小春  20:シエスタ     35:オスマン 50:アンナ
    6:在原七海  21:ハルナ       36:デルフリンガー 51:倉端直太
    7:和泉妃愛  22:少女リシュ   37:テクスト 52:枡形兵馬
    8:常盤華乃  23:リシュ       38:ダンプリメ 53:扇元樹
    9:錦あすみ  24:アキナ       39:ガレット
    10:鎌倉詩桜 25:クリス       40:スカロン
    11:竜閑天梨 26:カトレア 41:矢来美羽
    12:和泉里   27:エレオノール 42:布良梓
    13:新川広夢 28:モンモランシー 43:エリナ
    14:聖莉々子 29:リーヴル 44:エリナ  
"""
sv_cjks = """中日韩梵:
ai语音生成 54[空格][ZH]晚上好[ZH]　将会生成宁宁说的晚上好
ai语音生成 54[空格][JA]こんばんは[JA]　将会生成宁宁说的こんばんは
ai语音生成 54[空格][KO]안녕하세요[KO]　将会生成宁宁说的안녕하세요
ai语音生成 54[空格][SA]ॐ मणिपद्मे हूं [SA]　将会生成宁宁说的ॐ मणिपद्मे हूं 
id:
54      綾地寧々
55      朝武芳乃
56      在原七海
57      ルイズ
58      金色の闇
59      モモ
60      結城美柑
61      小茸
62      唐乐吟
63      小殷
64      花玲
65      八四
66      수아
67      미미르
68      아린
69      유화
70      연화
71      SA1
72      SA2
73      SA3
74      SA4
75      SA5
76      SA6
"""
sv = Service(
    name="ai语音生成",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)

outputPath = ""


async def chinese2katakana(text):
    cookies = {
        '__gads': 'ID=0913d7b7838088a9-22d4a86186d500c8:T=1660228904:RT=1660228904:S=ALNI_MYLAxIRws8hObfvoeF5wkg6F8_1qg',
        '__gpi': 'UID=00000880c2f1ffa9:T=1660228904:RT=1660228904:S=ALNI_ManV7rXnEUgMAuUxsLEFkSYonxQRQ',
        '__utmc': '79062217',
        '__utmz': '79062217.1660228909.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        '__utmt': '1',
        '__utma': '79062217.169553450.1660228904.1660228904.1660228904.1',
        '__utmb': '79062217.4.10.1660228909',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Origin': 'https://www.ltool.net',
        'Referer': 'https://www.ltool.net/chinese-simplified-and-traditional-characters-pinyin-to-katakana-converter-in-simplified-chinese.php',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Microsoft Edge";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'contents': f'{text}',
        'firstinput': 'OK',
        'option': '1',
        'optionext': 'zenkaku',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://www.ltool.net/chinese-simplified-and-traditional-characters-pinyin-to-katakana-converter-in-simplified-chinese.php', headers=headers, data=data, cookies=cookies, verify_ssl=False) as resp:
            a = await resp.text()
    html = etree.HTML(a)
    text = html.xpath("/html//form/div[5]/div/text()")
    text_full = ""
    for it in text:
        text_full = text_full + it
    # print(text_full)
    return text_full


def render_forward_msg(msg_list: list, uid=2854196306, name='小冰'):
    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
            "type": "node",
            "data": {
                    "name": str(name),
                "uin": str(uid),
                "content": msg
            }
        })
    return forward_msg


async def send_msg(msg_list, ev):
    result_list = []
    forward_msg = render_forward_msg(msg_list)
    try:
        result_list.append(await hoshino.get_bot().send_group_forward_msg(group_id=ev.group_id, messages=forward_msg))
    except:
        hoshino.logger.error('[ERROR]语音发送失败')
        await hoshino.get_bot().send(ev, f'啊咧，出错了...')
    await asyncio.sleep(1)
    return result_list


@sv.on_fullmatch("ai语音生成帮助", "AI语音生成帮助")
async def send_help(bot, ev):
    msg_list = []
    mes = f'{sv_help}'
    msg = f'{sv_cjks}'
    msg_list.append(mes)
    msg_list.append(msg)
    await send_msg(msg_list, ev)


@sv.on_prefix(("ai语音生成", "AI语音生成"))
async def novelai_getImg(bot, ev):
    key_word = str(ev.message.extract_plain_text()).strip()
    if len(key_word) > 150:
        bot.finish(ev, f"您的话太多啦", at_sender=True)
    if " " not in key_word:
        return bot.send(ev, f'{sv_help}')
    id = key_word.split(" ")
    datetime = calendar.timegm(time.gmtime())
    img_name = str(datetime)+'.wav'
    voice = MoeGoe(int(id[0]), key_word[2:], img_name)
    out_path = voice.generate_voice()
    rec = MessageSegment.record(f'file:///{out_path}')
    try:
        await bot.send(ev, rec)
    except Exception as e:
        await bot.finish(ev, f"语音发送失败{e}", at_sender=True)


@sv.on_prefix(("ai中文语音生成", "AI中文语音生成"))
async def novelai_getImg(bot, ev):
    key_word = str(ev.message.extract_plain_text()).strip()
    if len(key_word) > 150:
        bot.finish(ev, f"您的话太多啦", at_sender=True)
    if " " not in key_word:
        return bot.send(ev, f'{sv_help}')
    id = key_word.split(" ")
    datetime = calendar.timegm(time.gmtime())
    img_name = str(datetime) + '.wav'
    text = await chinese2katakana(key_word[2:])
    voice = MoeGoe(int(id[0]), text, img_name)
    out_path = voice.generate_voice()
    rec = MessageSegment.record(f'file:///{out_path}')
    try:
        await bot.send(ev, rec)
    except Exception as e:
        await bot.finish(ev, f"语音发送失败{e}", at_sender=True)
