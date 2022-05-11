from handler import Handler
import socket 
from pyaudio import *
import wave
import socket
from config.constants import *
from assistantlib.voice_handler import *

handler = Handler()
# 把地址绑定到套接字
sk = socket.socket()
print("server run at: " + HOST+":"+str(PORT))

sk.bind((HOST, PORT))
# 监听链接
sk.listen()
p = PyAudio()

def deal_remote_text(conn, addr):
    while "text" == INPUT_MODE and "remote" == INPUT_POSITION:
        msg = conn.recv(1024)
        handler.handle(msg.decode('utf-8'))
        if msg == b'bye':
            break

def deal_remote_voice(conn, addr):
    wf = wave.open(WAVFILENAME,"wb")
    wf.setnchannels(2)
    wf.setsampwidth(p.get_sample_size(p.get_format_from_width(2)))
    wf.setframerate(RATE)
    ret = conn.recv(1024)
    while ret != b'':
        wf.writeframes(ret)
        ret = conn.recv(1024)
    wf.close()
    conn.close()

    recognition = VoiceToText()
    words = recognition.baiduRecognition()
    handler.handle(words)

def deal_local_voice():
    #TODO
    """
    实现电脑本地录音转换为指令
    """
    pass

def deal_local_text():
    while "text" == INPUT_MODE and "local" == INPUT_POSITION:
        msg = input(">>>")    
        handler.handle(msg)

while True:
    if "remote" == INPUT_POSITION:
        conn, addr = sk.accept()
        if "text" == INPUT_MODE:
            deal_remote_text(conn, addr)
        elif "voice" == INPUT_MODE:
            deal_remote_voice(conn, addr)
    elif "local" == INPUT_POSITION:
        if "text" == INPUT_MODE:
            deal_local_text()
        elif "voice" == INPUT_MODE:
            deal_local_voice()
    else:
        handler.output("模式配置错误!")
        break

