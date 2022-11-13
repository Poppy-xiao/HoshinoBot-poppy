
from pathlib import Path
import time
import numpy
import cv2
from hoshino import Service, priv, aiorequests, R
import requests
import base64
from PIL import Image
from io import BytesIO
import time,calendar
import math
from .upcunet_v3 import generateImg
token = ''

sv_help = """ 
"""
sv = Service(
    name = "清晰术",  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = True, #可见性
    enable_on_default = True, #默认启用
    bundle = "娱乐", #分组归类
    help_ = sv_help #帮助说明
    )
 

save_image_path = R.img('real_cugan').path 
Path(save_image_path).mkdir(parents = True, exist_ok = True)

@sv.on_fullmatch("清晰术帮助")
async def send_help(bot, ev):
    await bot.send(ev, f'{sv_help}') 

@sv.on_prefix(("清晰术"))
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
    search_img = await aiorequests.get(file)
    i = await search_img.content 
    im = Image.open(BytesIO(i)) 
    img = cv2.cvtColor(numpy.asarray(im),cv2.COLOR_RGB2BGR)[:,:,[2,1,0]]  
    size = img.shape    
    if size[0] > 1920 or size[1] > 1080: 
        width = size[0] / 2
        hight = size[1] / 2
        img = cv2.resize(img,[int(width),int(hight)])
        await bot.send(ev, f"图片分辨率过大，压缩为{width}x{hight}") 
    elif size[0]< 128 or size[1] < 128:
        if (size[0] < size[1]):
            hight = 128 
            width = float(size[1]) / float(size[0]) * hight 
            img = cv2.resize(img,[int(width),int(hight)])
        else:
            width = 128 
            hight = float(size[0]) / float(size[1]) * width 
            img = cv2.resize(img,[int(width),int(hight)]) 
    size = img.shape  
    try: 
        datetime = calendar.timegm(time.gmtime())
        img_name= str(datetime)+'.png' 
        save = "/home/poppy/workspace/image/" + img_name # 拼接图片路径  
        read = "file:///" + save
        generate = generateImg(img)
        result = generate.generate()  
        cv2.imwrite(save,result)
        del generate
        await bot.send(ev, f"清晰后的图片如下：[CQ:image,file={read}]", at_sender=True)
    except Exception as e: 
        await bot.finish(ev, f"啊嘞，出错了。", at_sender=True)