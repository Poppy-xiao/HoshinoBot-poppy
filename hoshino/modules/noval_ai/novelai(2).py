from pathlib import Path
from hoshino import Service, priv, aiorequests, R
import requests
import base64
from PIL import Image
from io import BytesIO
import math

token = ''

sv_help = """[ai绘图+关键词] 关键词仅支持英文，用逗号隔开
[以图绘图+关键字+图片] 注意图片尽量长宽都在765像素一下，不然会被狠狠地压缩
逗号分隔tag,%20为空格转义,加0代表增加权重,可以加很多个,有消息称加入英语句子识别(你们自己测)
可选参数
&shape=Portrait/Landscape/Square 默认Portrait竖图           
&scale=11                        默认11,只建议11-24,细节会提高,太高了会过曝
&seed=1111111                    随机生成不建议用,如果想在返回的原图上修改,在响应头里找到seed，请注意seed一脉单传,seed不会变,也不能倒退
"""
sv = Service(
    name = "二次元ai绘图",  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = True, #可见性
    enable_on_default = True, #默认启用
    bundle = "娱乐", #分组归类
    help_ = sv_help #帮助说明
    )

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76"
}

imgpath = R.img('novelai').path
Path(imgpath).mkdir(parents = True, exist_ok = True)

@sv.on_fullmatch("ai绘图帮助","AI绘图帮助")
async def send_help(bot, ev):
    await bot.send(ev, f'{sv_help}')

@sv.on_prefix(("ai绘图", "AI绘图"))
async def novelai_getImg(bot, ev):
    '''
    AI绘制二次元图片
    '''
    key_word = str(ev.message.extract_plain_text()).strip()
    await bot.send(ev, "正在绘图中，请稍后...")
    try:
        url = f"http://91.217.139.190:5010/got_image?tags={key_word}&token={token}"
        img_resp = await aiorequests.get(url, headers = headers, timeout = 30)
    except Exception as e:
        await bot.finish(ev, f"api请求超时，请稍后再试。{e}", at_sender=True)
    i = await img_resp.content
    seed = img_resp.headers['seed']
    img = 'base64://' + base64.b64encode(bytes(i)).decode()
    try:
        await bot.send(ev, f"根据关键词【{key_word}】绘制的图片如下：\n[CQ:image,file={img}]\nseed:{seed}", at_sender=True)
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
        if not tag:
            await bot.finish(ev, f"图呢，图呢", at_sender=True)
        else:
            return
    await bot.send(ev, "正在绘图中，请稍后...")
    try:
        search_img = await aiorequests.get(file)
        i = await search_img.content
        im = Image.open(BytesIO(i))
        w, h = im.size
        if w > h:
            n = math.ceil(w / 756)
        else:
            n = math.ceil(h / 756)
        im.thumbnail((w//n,h//n))
        buffer = BytesIO()
        im.save(buffer, format='PNG')
        e = buffer.getvalue()
        data = base64.b64encode(bytes(e)).decode()
        i = requests.post("http://91.217.139.190:5010/got_image2image"+ (f"?tags={tag}" if tag != "" else "?tags=lolicon")+f'&token={token}', data=data).content
        img = 'base64://' + base64.b64encode(bytes(i)).decode()
        await bot.send(ev, f"根据图片绘制的{tag}图片如下：\n[CQ:image,file={img}]\n", at_sender=True)
    except Exception as e:
        await bot.finish(ev, f"啊嘞，出错了。出错代码：{e}", at_sender=True)