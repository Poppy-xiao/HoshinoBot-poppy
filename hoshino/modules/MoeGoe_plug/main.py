from pathlib import Path
from hoshino import Service, priv, aiorequests, R
import requests
import base64
from PIL import Image 
from io import BytesIO
import math
import time,calendar
import aiohttp
from .MoeGoe.commons import *
from .MoeGoe.MoeGoe import MoeGoe
from nonebot import MessageSegment
from lxml import etree
token = ''

sv_help = """ 
"""
sv = Service(
    name = "ai语音生成",  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = True, #可见性
    enable_on_default = True, #默认启用
    bundle = "娱乐", #分组归类
    help_ = sv_help #帮助说明
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
        async with session.post('https://www.ltool.net/chinese-simplified-and-traditional-characters-pinyin-to-katakana-converter-in-simplified-chinese.php', headers=headers, data=data, cookies=cookies,verify_ssl=False) as resp:
            a = await resp.text()
    html = etree.HTML(a)
    text = html.xpath("/html//form/div[5]/div/text()")
    text_full = ""
    for it in text:
        text_full = text_full + it
    #print(text_full)
    return text_full

@sv.on_fullmatch("ai语音生成帮助","AI语音生成帮助")
async def send_help(bot, ev):
    await bot.send(ev, f'{sv_help}')

@sv.on_prefix(("ai语音生成", "AI语音生成"))
async def novelai_getImg(bot, ev): 
    key_word = str(ev.message.extract_plain_text()).strip() 
    datetime = calendar.timegm(time.gmtime())
    img_name= str(datetime)+'.wav'
    voice = MoeGoe(key_word,img_name)
    out_path = voice.generate_voice() 
    rec = MessageSegment.record(f'file:///{out_path}')
     
    try:
        await bot.send(ev, rec)
    except Exception as e:
        await bot.finish(ev, f"语音发送失败{e}", at_sender=True) 

@sv.on_prefix(("ai中文语音生成", "AI中文语音生成"))
async def novelai_getImg(bot, ev): 
    key_word = str(ev.message.extract_plain_text()).strip() 
    datetime = calendar.timegm(time.gmtime())
    img_name= str(datetime)+'.wav'
    text = await chinese2katakana(key_word)
    voice = MoeGoe(text,img_name)
    out_path = voice.generate_voice() 
    rec = MessageSegment.record(f'file:///{out_path}')
     
    try:
        await bot.send(ev, rec)
    except Exception as e:
        await bot.finish(ev, f"语音发送失败{e}", at_sender=True) 
 