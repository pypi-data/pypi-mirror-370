from pathlib import Path
import json

import nonebot
from nonebot import get_plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, ActionFailed
from nonebot.exception import MatcherException
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin.on import on_message, on_keyword
from nonebot.rule import to_me
from typing_inspection.typing_objects import alias

from .config import Config
from nonebot import on_command
import httpx  # 替换 requests 用的 httpx

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-simple-setu",
    description="一个简单到不能再简单的色图插件",
    usage="通过指令获取setu",
    type="application",
    homepage="https://github.com/nomdn/nonebot-plugin-simple-setu",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

config = get_plugin_config(Config)

# 创建一个异步客户端
http_client = httpx.AsyncClient()

setu = on_command("setu", aliases={"色图", "来份色图"})

@setu.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    if config.simple_setu_enable == 1:
        # 判断功能是否开启
        if config.simple_setu_api_url == 0:
            # 判断api的类型
            if tag := args.extract_plain_text():
                # 检测是否传入tag
                sender_qq = event.get_user_id()
                # 使用 httpx 替换 requests
                try:
                    response = await http_client.get(f"https://api.lolicon.app/setu/v2?tag={tag}")
                    # 获取色图api的json文件
                    json_dict = response.json()
                    # 解析文件 格式参考example.json
                    title = json_dict["data"][0]["title"]
                    pid = json_dict["data"][0]["pid"]
                    author = json_dict["data"][0]["author"]
                    url = json_dict["data"][0]["urls"]["original"]
                    # 发送消息 格式： @qq + 标题 + pid + 作者 + 图片
                    await setu.send(MessageSegment.at(sender_qq)+f"\n标题:{title}\nPID:{pid}\n作者:{author}\n"+MessageSegment.image(f"{url}"))
                except MatcherException:
                    raise
                except Exception as e:
                    await setu.finish(f"发生错误：{e}")
            else:
                # 无tag传入则不加入tag参数获取json文件
                try:
                    sender_qq = event.get_user_id()
                    response = await http_client.get(f"https://api.lolicon.app/setu/v2")
                    json_dict = response.json()
                    #同上
                    title = json_dict["data"][0]["title"]
                    pid = json_dict["data"][0]["pid"]
                    author = json_dict["data"][0]["author"]
                    url = json_dict["data"][0]["urls"]["original"]
                    await setu.send(MessageSegment.at(sender_qq) + f"\n标题:{title}\nPID:{pid}\n作者:{author}\n"+MessageSegment.image(f"{url}"))
                except MatcherException:
                    raise
                except Exception as e:
                    await setu.finish(f"发生错误：{e}")
        elif config.simple_setu_api_url == 1:
            #jitsu api
            if tag := args.extract_plain_text():
                try:
                    sender_qq = event.get_user_id()
                    response = await http_client.get(f"https://image.anosu.top/pixiv/json?keyword={tag}")
                    json_dict = response.json()
                    title = json_dict[0]["title"]
                    pid = json_dict[0]["pid"]
                    author = json_dict[0]["user"]
                    url = json_dict[0]["url"]
                    await setu.finish(MessageSegment.at(sender_qq)+f"\n标题:{title}\nPID:{pid}\n作者:{author}\n"+MessageSegment.image(f"{url}"))
                except MatcherException:
                    raise
                except Exception as e:
                    await setu.finish(f"发生错误：{e}")
            else:
                try:
                    sender_qq = event.get_user_id()
                    response = await http_client.get("https://image.anosu.top/pixiv/json")
                    json_dict = response.json()  # 注意：这里可能需要异常处理
                    title = json_dict[0]["title"]
                    pid = json_dict[0]["pid"]
                    author = json_dict[0]["user"]
                    url = json_dict[0]["url"]
                    await setu.finish(MessageSegment.at(sender_qq)+f"\n标题:{title}\nPID:{pid}\n作者:{author}\n"+MessageSegment.image(f"{url}"))
                except MatcherException:
                    raise
                except Exception as e:
                    await setu.finish(f"发生错误：{e}")
        else:
            setu.finish("你的配置有误！")
    elif config.simple_girl_enable == 0:
        setu.finish("setu功能已关闭！")
    else:
        setu.finish("你的配置有误")

leg = on_command("leg", aliases={"腿子", "来份腿子"})

@leg.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    # 提取参数纯文本作为地名，并判断是否有效
    if config.simple_setu_on_command_leg_enable == 1:
        try:
            sender_qq_leg = event.get_user_id()
            # 获取腿子图api json 文件
            response_leg = await http_client.get("https://api.lolimi.cn/API/meizi/api.php?type=json")
            json_dict_leg = response_leg.json()
            # 该api只返回url和code
            image_leg = json_dict_leg["text"]
            at_segment_leg = MessageSegment.at(user_id=sender_qq_leg)
            # 发送消息 格式： @qq+图片
            await leg.finish(at_segment_leg+MessageSegment.image(image_leg))
        except MatcherException:
            raise
        except Exception as e:
            await leg.finish(f"发生错误：{e}")
    elif config.simple_setu_on_command_leg_enable == 0:
        leg.finish("腿子图功能已关闭！")
    else:
        leg.finish("你的配置有误！")

girl = on_command("girl", aliases={"少女写真", "来份写真"})

@girl.handle()
async def handle_function(event: MessageEvent, args: Message = CommandArg()):
    # 提取参数纯文本作为地名，并判断是否有效
    if config.simple_setu_girl_enable == 1:
        try:
            # 该部分与腿子图相同
            sender_qq_girl = event.get_user_id()
            response_girl = await http_client.get("https://api.lolimi.cn/API/meinv/api.php?type=json")
            json_dict_girl = response_girl.json()
            # 只不过api多了个嵌套
            image_girl = json_dict_girl["data"]["image"]
            at_segment_girl = MessageSegment.at(user_id=sender_qq_girl)
            await girl.finish(at_segment_girl+MessageSegment.image(image_girl))
        except MatcherException:
            raise
        except Exception as e:
            await girl.finish(f"发生错误：{e}")
    elif config.simple_setu_girl_enable == 0:
        girl.finish("少女写真功能已关闭")
    else:
        girl.finish("你的配置有误！")
fake_cross_dresser = on_keyword({"看看腿"},rule=to_me())
# 等同于腿子图
@fake_cross_dresser.handle()
async def handle_function(event: MessageEvent):
    if config.simple_setu_on_keyword_leg_enable == 1:

        try:
            sender_qq_fake = event.get_user_id()
            response_fake = await http_client.get("https://api.lolimi.cn/API/meizi/api.php?type=json")
            json_dict_fake = response_fake.json()
            image_fake = json_dict_fake["text"]
            at_segment_fake = MessageSegment.at(user_id=sender_qq_fake)
            await fake_cross_dresser.finish(at_segment_fake+"\n"+MessageSegment.image(image_fake))
        except MatcherException:
            raise
        except Exception as e:
            await fake_cross_dresser.finish(f"发生错误：{e}")
    elif config.simple_setu_on_keyword_leg_enable == 0:
        fake_cross_dresser.finish("at获取腿子图已关闭")
    else:
        fake_cross_dresser.finish("你的配置有误")