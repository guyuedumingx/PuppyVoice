# 内置的module
from copy import deepcopy
from assistantlib.configuration import Configuration
import jieba

configuration = Configuration()


class MetaModule:

    def __init__(self, config):
        self.build({})
        self.name = config.get('name', '')
        self.keywords = config.get('keywords',[])
        self.initialize(config)
    
    def build(self, operations):
        """
        类内部的初始化过程
        这个过程中会读取配置文件
        """
        try:
            self.index
        except:
            self.mro = self.__class__.mro()
            self.index = len(self.mro) - 2

        cls = self.mro[self.index]
        hasScan = True 
        try:
            if(cls.clsName) != cls.__name__:
                hasScan = False
        except:
            hasScan = False
        if not hasScan:
            self.build_configuration(cls, operations)
        self.index -= 1
        if self.index >= 0:
            self.mro[self.index].build(self,deepcopy(cls.operations))

    def build_configuration(self, cls, operations):
        """
        关键词配置初始化
        """
        configs = configuration.load_configuration(cls.__name__, {}).get('operations',[])
        cls.operations = {}
        # 展开配置
        for item in configs:
            cls.operations = dict(cls.operations, **self.build_sub(item))
        # 合并父配置
        for key,value in cls.operations.items():
            if operations.__contains__(key):
                value.merge(operations.get(key))
            operations[key] = value
        cls.operations = operations
        cls.clsName = cls.__name__

    def build_sub(self, item):
        operations = {}
        if item.__contains__('operations'):
            for sub in item['operations']:
                operas = self.build_sub(sub)
                for key in item['keys']:
                    jieba.add_word(key)
                    operations[key] = ModuleOperation(key, sub=operas)
        else:
            for key in item['keys']:
                jieba.add_word(key)
                operations[key] = ModuleOperation(key, method=item.get('method'))
        return operations
    
    def handle(self, handler):
        if self.operations.__contains__(handler.opera):
            print(self.operations[handler.opera])

    def initialize(self, config):
        """
        自定义的初始化过程
        """


class ModuleOperation:

    def __init__(self, keyword, method=None, sub=None):
        # 字符串列表
        self.keyword = keyword
        # 方法名
        self.method = ''
        # ModuleConfigureItem列表
        self.sub = {}
        if method != None:
            self.method = method
        if sub != None:
            self.sub = sub
    
    def hasSub(self):
        return len(self.sub) != 0
    
    def hasMethod(self):
        return self.method != ''
    
    def getKeyWord(self):
        return self.keyword
    
    def merge(self, moduleOperations):
        if moduleOperations.hasSub() and self.hasSub():
            self.merge_sub(self,moduleOperations)
    
    def merge_sub(self, module1, module2):
           for key, value in module2.sub.items():
               if not module1.sub.__contains__(key):
                   module1.sub[key] = value
               elif module1.sub[key].hasSub():
                   module1.sub[key].merge(value)
    
    def __str__(self):
        return "\nmethod:{}\nsub:{}\n".format(self.method, self.sub)
    __repr__ = __str__


class Window(MetaModule):
    pass


class NormalWindow(Window):
    pass


class ExternalDevice(MetaModule):

    def initialize(self, config):
        self.host = config.get('host','')
        self.port = config.get('port',10000)
