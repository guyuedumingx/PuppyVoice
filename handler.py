from assistantlib.configuration import Configuration
from assistantlib.build_in import *
import re

configuration = Configuration()

class Handler:
    """
    self.words : 分词前的完整语句
    self.opera : 分词后的关键词集合
    self.matchs : 匹配到的关键词列表
    """

    def __init__(self):
        self.outputVoiceEngine = Puppy({
            "keywords":["小狗"],
            "instruction": "我是一个语言助手哦"
        })
        self.devices = [self.outputVoiceEngine]
        for name,config in configuration.devices.items():
            config['name'] = name
            if config.__contains__('type'):
                if config.__contains__('superType'):
                    cls = type(config['type'], (eval(config['superType'])(config).__class__,),{})
                    self.devices.append(cls(config))
                else:
                    self.devices.append(eval(config['type'])(config))

        self.add_keywords_to_jieba()

    
    def add_keywords_to_jieba(self):
        """
        把关键词加入结巴分词词库
        """
        for device in self.devices:
            for key in device.keywords:
                jieba.add_word(key)
    
    def output(self, msg, mode='voice'):
        if 'voice' == mode:
            self.outputVoiceEngine.show(msg)
        elif 'console' == mode:
            print(msg)

    def wordSegmentation(self, words):
        """
        分词
        """
        words = words.strip()
        words = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*()]+", " ", words)
        # 分词前的完整语句
        self.words = words
        res=set(jieba.cut(words,cut_all=True))
        print(res)
        return res
    
    def handle(self, words):
        # 分词后的关键词集合
        self.opera = self.wordSegmentation(words)
        flag = False
        for device in self.devices:
            match = self.opera & device.keywords
            if len(match) > 0:
                # 匹配的关键词
                self.matchs = [match.pop()]
                flag = device.action(self)
                if flag:
                    self.lastMatchDevice = device
        if not flag:
            try:
                flag = self.lastMatchDevice.action(self)
            except:
                pass
        if not flag:
            self.output("执行命令:{}, 失败!".format(self.words))

    
    

        
