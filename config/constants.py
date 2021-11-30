import socket

"""
全部配置
"""
# 监听的端口号
PORT = 8898

# 监听的主机地址(也就是本机的地址)
HOST = socket.gethostbyname(socket.gethostname())

# 临时的语音文件名
WAVFILENAME = "record.wav"

"""
配置加载
"""
USER_CONFIGURATIONS = ['alias/global.yml']
CONFIGURATION_PATH = 'config'
DEVICES_FILE = 'devices.yml'


"""
语音采集的信息
"""
CHANNELS = 2
RATE = 44100

"""
结巴分词 
"""
# 是否启用全匹配模式
CUT_ALL = True

"""
语音助手设置
"""
# 输出模式， 语音模式: voice 控制台书写模式: console 啥都不显示: none
OUTPUT_MODE = "voice"

"""
输入来源
"""
# 输出模式， 语音模式: voice 文本输入模式: text
INPUT_MODE = "voice"
# 输入的位置， 来自本地的输入: local 来自端口的输入: remote
INPUT_POSITION = "remote"

"""
使用百度语音识别
"""
BAIDU_APP_ID  = '25123957'
BAIDU_API_KEY = 'D6gNCAiOhubWF2BYCT9gKw1U'
BAIDU_SECRET_KEY = 'jGQGwtlu6cvkQh9rn4RkprN5mRgyRIpH'

"""
使用科大讯飞语音识别
"""
XUNFEI_APPID = '03ac0daa'
XUNFEI_SECRET_KEY = '3e5e986815478dde6d59b740576eef81'
LFASRHOST = 'http://raasr.xfyun.cn/api'

# 请求的接口名
API_PREPARE = '/prepare'
API_UPLOAD = '/upload'
API_MERGE = '/merge'
API_GET_PROGRESS = '/getProgress'
API_GET_RESULT = '/getResult'
# 文件分片大小10M
FILE_PIECE_SICE = 10485760

LFASR_TYPE = 0
# 是否开启分词
HAS_PARTICIPLE = 'false'
HAS_SEPERATE = 'true'
# 多候选词个数
MAX_ALTERNATIVES = 0
# 子用户标识
SUID = ''
