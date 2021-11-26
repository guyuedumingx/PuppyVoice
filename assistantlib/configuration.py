import json
import os
from copy import deepcopy
from config.constants import *
import yaml

class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]

@Singleton
class Configuration:

    def __init__(self):
        self.configurations = {}
        self.devices = self.load_file(DEVICES_FILE)
        self.pet = None
        for file in USER_CONFIGURATIONS:
            self.userConfig = self.load_file(file)
            self.configurations = dict(self.configurations, **self.userConfig)

    def load_file(self, file):
        """
        加载配置文件的内容，并返回字典对象
        """
        try:
            with open(CONFIGURATION_PATH+os.sep+file, "r", encoding='utf-8') as f:
                res = f.read()
                _,type = os.path.splitext(file)
                if(".yml" == type or ".yaml" == type):
                    return yaml.load(res, Loader=yaml.Loader)
                else:
                    return json.loads(res)
        except:
            print("Can't not find: "+file)

    def load_configuration(self, key, default=None):
        res = self.configurations.get(key, default)
        if (type(res) == type({}) or type(res) == type([])):
            return deepcopy(res)
        else:
            return res
