from pathlib import Path
from hoshino import Service, priv, aiorequests, R
import requests
import base64
from PIL import Image
from io import BytesIO
import math
import random
import hoshino
import asyncio
from hoshino import Service, priv, aiorequests, R

token = ''

sv_help = """[ai绘图+关键词] 关键词仅支持英文，用逗号隔开 
"""
sv = Service(
    name="二次元ai绘图",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76"
}

imgpath = R.img('novelai').path
Path(imgpath).mkdir(parents=True, exist_ok=True)


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
        hoshino.logger.error('[ERROR]发送失败')
        await hoshino.get_bot().send(ev, f'啊咧，出错了...')
    await asyncio.sleep(1)
    return result_list


@sv.on_fullmatch("ai绘图帮助", "AI绘图帮助")
async def send_help(bot, ev):
    await bot.send(ev, f'{sv_help}')


async def generate():
    endpoint = "http://192.168.1.3:4315/generate"
    data = {"prompt": "masterpiece, best quality, miku", "seed": random.randint(
        0, 2**32), "n_samples": 1, "sampler": "k_euler", "width": 512, "height": 768, "scale": 11, "steps": 28, "uc": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"}
    req = requests.post(endpoint, json=data).json()
    output = req["output"]

    for x in output:
        img = base64.b64decode(x)


@sv.on_prefix(("ai绘图", "AI绘图"))
async def novelai_getImg(bot, ev):
    '''
    AI绘制二次元图片
    '''
    key_word = str(ev.message.extract_plain_text()).strip()
    await bot.send(ev, "正在绘图中，请稍后...")
    try:
        endpoint = "http://192.168.1.3:4315/generate"
        seed = random.randint(0, 2**32)
        data = {"prompt": "masterpiece, best quality," + key_word, "seed": seed, "n_samples": 1, "sampler": "k_euler_ancestral", "width": 512, "height": 768, "scale": 11, "steps": 28,
                "uc": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"}
        i = requests.post(endpoint, json=data).json()
    except Exception as e:
        await bot.finish(ev, f"api请求超时，请稍后再试。{e}", at_sender=True)
    data = i["output"]
    for x in data:
        img = 'base64://' + x
        try:
            msg_list = []
            mes = f"根据关键词【{key_word}】绘制的图片如下：\n[CQ:image,file={img}]\nseed:{seed}"
            msg_list.append(mes)
            await send_msg(msg_list, ev)
        except Exception as e:
            await bot.finish(ev, f"图片发送失败。{e}", at_sender=True)


@sv.on_prefix(("以图绘图", "AI以图绘图", "以图生图", "ai画图", "画图"))
async def novelai_drawImg(bot, ev):
    file = ''
    tag = ev.message.extract_plain_text()
    for m in ev.message:
        if m.type == 'image':
            file = m.data['url']
            break
    if not file:
        await bot.finish(ev, f"图呢，图呢", at_sender=True)
        if not tag:
            await bot.finish(ev, f"请输入tag", at_sender=True)
        else:
            return
    await bot.send(ev, "正在绘图中，请稍后...")
    try:
        search_img = await aiorequests.get(file)
        i = await search_img.content
        im = Image.open(BytesIO(i))
        w, h = im.size
        width = 0
        height = 0
        if (w / h) < 1.1 and (w / h) > 0.9:
            width = 512
            height = 512
        elif (w / h) > 1.1:
            width = 768
            height = 512
        else:
            width = 512
            height = 768
        buffer = BytesIO()
        im.save(buffer, format='PNG')
        e = buffer.getvalue()
        data = base64.b64encode(bytes(e)).decode()
        endpoint = "http://192.168.1.3:4315/generate-stream"
        seed = random.randint(0, 2**32)
        data = {"prompt": "masterpiece, best quality," + tag, "seed": seed, "n_samples": 1, "sampler": "k_euler_ancestral", "width": width, "height": height, "scale": 12, "steps": 28,"image":data,
                "uc": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"}
        i = requests.post(endpoint, json=data).text.split("\n")[2].replace("data:", "")
    except Exception as e:
        await bot.finish(ev, f"api请求超时，请稍后再试。{e}", at_sender=True) 
    try: 
        msg_list = []
        print(type(i))
        img = 'base64://' + i
        mes = f"根据关键词【{tag}】以图绘图的图片如下：\n[CQ:image,file={img}]\nseed:{seed}"
        msg_list.append(mes)
        await send_msg(msg_list, ev)
    except Exception as e:
        await bot.finish(ev, f"图片发送失败。{e}", at_sender=True)
