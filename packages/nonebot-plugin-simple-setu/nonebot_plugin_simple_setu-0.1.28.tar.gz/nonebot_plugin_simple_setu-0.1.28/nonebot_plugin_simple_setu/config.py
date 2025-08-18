from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    #选择色图api
    #0为lolicon
    #1为jitsu
    #在某些情况下jitsu比lolicon快
    simple_setu_api_url :int= 0
    #功能管理
    #setu功能 1为开启0为关闭
    simple_setu_enable :int=1
    #少女写真功能 1为开启0为关闭
    simple_setu_girl_enable :int=1
    #指令获取腿子图 1为开启0为关闭
    simple_setu_on_command_leg_enable :int=1
    #at获取腿子图 1为开启0为关闭
    simple_setu_on_keyword_leg_enable :int=1
