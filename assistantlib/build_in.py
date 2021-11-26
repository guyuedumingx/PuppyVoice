# 内置的module
from copy import deepcopy
import re
from assistantlib.configuration import Configuration
from pywinauto.keyboard import send_keys
import jieba
import win32gui
import win32con
import pyttsx3
import cv2
import mediapipe as mp
import threading
import os

configuration = Configuration()


class MetaModule:

    def __init__(self, config):
        self._build({})
        self.name = config.get('name', '')
        self.keywords = set(config.get('keywords',[self.name]))
        self.instruction = config.get('instruction','这是一个组件')
        self.initialize(config)
    
    def _build(self, operations):
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
            self._build_configuration(cls, operations)
        self.index -= 1
        if self.index >= 0:
            self.mro[self.index]._build(self,deepcopy(cls.operations))

    def _build_configuration(self, cls, operations):
        """
        关键词配置初始化
        """
        configs = configuration.load_configuration(cls.__name__, {}).get('operations',[])
        cls.operations = {}
        # 展开配置
        for item in configs:
            cls.operations = dict(cls.operations, **self._build_sub(item))
        # 合并父配置
        for key,value in cls.operations.items():
            if operations.__contains__(key):
                value.merge(operations.get(key))
            operations[key] = value
        cls.operations = operations
        cls.clsName = cls.__name__

    def _build_sub(self, item):
        operations = {}
        if item.__contains__('operations'):
            operas = {}
            for sub in item['operations']:
                operas = dict(operas, **self._build_sub(sub))
            for key in item['keys']:
                jieba.add_word(key)
                operations[key] = ModuleOperation(key, sub=operas)
        else:
            for key in item['keys']:
                jieba.add_word(key)
                if item.__contains__('method'):
                    operations[key] = ModuleOperation(key, method=item.get('method'))
                elif item.__contains__('shotkeys'):
                    operations[key] = ModuleOperation(key, shotkeys=item.get('shotkeys'))
        return operations
    
    def action(self, handler):
        return self._execHandle(handler, self.operations)
    
    def _execHandle(self, handler, operations):
        match = handler.opera & set(operations.keys())
        if len(match) > 0:
            key = match.pop()
            handler.matchs.append(key)
            opera = operations[key]
            if opera.hasSub():
                return self._execHandle(handler, opera.sub)
            elif opera.hasMethod():
                return eval(opera.method)(handler)
            elif opera.hasShotKeys():
                try:
                    # 调用了子类Window的方法，有很大的隐患
                    return self.send_keys_to_window(handler, opera.shotkeys)
                except:
                    return False

        return False

    def initialize(self, config):
        """
        自定义的初始化过程
        """
    
    def show_instruction(self, handler):
        handler.output(self.instruction)


class ModuleOperation:

    def __init__(self, keyword, method=None, sub=None, shotkeys=None):
        # 字符串列表
        self.keyword = keyword
        # 方法名
        self.method = ''
        # ModuleConfigureItem列表
        self.sub = {}
        # 发送快捷键列表
        self.shotkeys = []
        if method != None:
            self.method = method
        if sub != None:
            self.sub = sub
        if shotkeys != None:
            self.shotkeys = shotkeys

    def hasShotKeys(self):
        return len(self.shotkeys) != 0
    
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


class Puppy(MetaModule):
    """
    小狗语音助手
    """
    def initialize(self, config):
        self.engine = pyttsx3.init()

    def show(self, msg):
        self.engine.say(msg)
        self.engine.runAndWait()
    
    def get_all_voices(self):
        return self.engine.getProperty("voices")
    
    def rate_up(self, handler):
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate',rate+50)
        handler.output(handler.matchs[-1]+handler.matchs[-2]+"成功!")
        return True

    def rate_down(self, handler):
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate',rate-50)
        handler.output(handler.matchs[-1]+handler.matchs[-2]+"成功!")
        return True
    
    def volume_up(self, handler):
        volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', volume+0.5)
        handler.output(handler.matchs[-1]+handler.matchs[-2]+"成功!")
        return True

    def volume_down(self, handler):
        volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', volume-0.25)
        handler.output(handler.matchs[-1]+handler.matchs[-2]+"成功!")
        return True


class Window(MetaModule):
    """
    windows的窗口模块，可以用来操作windows窗口
    """
    hwnd_title = dict()

    def initialize(self, config):
        super().initialize(config)
        Window._load()
        self.searchWord = config.get('searchWord',self.name)

    @classmethod
    def _load(cls, refresh=False):
        if(len(cls.hwnd_title.keys()) == 0 or refresh):
            cls.hwnd_title.clear()
            win32gui.EnumWindows(Window.get_all_hwnd, 0)

    @classmethod
    def get_all_hwnd(cls, hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            cls.hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})
    
    def do_window_action(self, handler, type):
        """
        执行窗口操作
        """
        key = handler.matchs[-1]
        try:
            h = self.handle
        except:
            success, h = self.get_handle(handler)
            if not success:
                handler.output("{}窗口, 失败!".format(key+self.name))
                return True
        win32gui.ShowWindow(h, type)
        handler.output("{}窗口, 成功!".format(key+self.name))
        return True
    
    def send_keys_to_window(self, handler, keys):
        try:
            h = self.handle
        except:
            success, h = self.get_handle(handler)
        win32gui.SetActiveWindow(h)
        win32gui.BringWindowToTop(h)
        send_keys('%')
        win32gui.SetForegroundWindow(h)
        for key in keys:
            send_keys(key)
        return True
    
    def post_message_to_window(self, handler, type):
        """
        发送信息到窗口
        """
        key = handler.matchs[-1]
        try:
            handle = self.handle
        except:
            self._load(refresh=True)
            success, handle = self.get_handle(handler)
            if not success:
                handler.output("{}窗口, 失败!".format(key+self.name))
                return False
        try:
            win32gui.PostMessage(handle,type)
            handler.output("{}窗口, 成功!".format(key+self.name))
            return True
        except:
            handler.output("{}窗口, 失败!请确认窗口是否存在!".format(key+self.name))
            return False

    def window_exit(self, handler):
        back = self.post_message_to_window(handler, win32con.WM_CLOSE)
        self.hwnd_title.pop(self.handle)
        try:
            delattr(self, "handle")
        except:
            pass 
        return back
    
    def get_handle(self, handler):
        """
        子类只需要复写这个方法就好了
        """
        success, h = self.get_handle_by_keyword(self.searchWord)
        if success:
            self.handle = h
            return True, h
        return False, h
    
    def get_handle_by_keyword(self, searchWord, repl=True):
        searchWord = searchWord.strip()
        """
        根据关键词获取窗口句柄
        repl: 是否使用正则表达式来搜索句柄中的字串
        """
        if searchWord in ["", " "]:
            return False, -1
        self._load(refresh=True)
        for h, t in self.__class__.hwnd_title.items():
            if t != '':
                if repl:
                    try:
                        if re.search(searchWord, t,re.I):
                            return True, h
                    except:
                        continue
                elif searchWord in t:
                    return True, h

        return False, -1

    def window_show(self, handler):
        return self.do_window_action(handler,win32con.SW_SHOWNORMAL)

    def window_hide(self, handler):
        return self.do_window_action(handler, win32con.SW_SHOWMINIMIZED)
    
    def window_maximize(self, handler):
        return self.do_window_action(handler, win32con.SW_SHOWMAXIMIZED)
    
    # def show_all(self, handler, key):
    #     self._load(refresh=True)
    #     for h,t in Window.hwnd_title.items():
    #         if t != "":
    #             handler.output((h,t), 'console') 


class Software(Window):
    """
    windows的软件模块，可以用来操作软件
    """
    def initialize(self, config):
        super().initialize(config)
        self.execPath = config.get('execPath','')

    def launch(self, handler):
        os.startfile(self.execPath)
        handler.output("{},{} 成功!".format(handler.matchs[-1], self.name))
        return True


class Camera(Window):

    def initialize(self, config):
        super().initialize(config)
        self.handDetecting = False
        self.faceMeshDetecting = False
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_face_mesh = mp.solutions.face_mesh
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    """
    操作电脑的摄像头
    """
    def launch(self, handler):
        self.screen = cv2.VideoCapture(0)
        thread = threading.Thread(target=self.capture)
        self.isRunning = True
        thread.start()
        handler.output("{},启动成功".format(self.name))
        return True

    def exit(self, handler):
        #关闭摄像头
        self.isRunning = False
        handler.output("{},关闭成功".format(self.name))
        return True
    
    def shot(self, handler):
        cv2.imwrite("shot.jpg",self.img)
        handler.output("拍照成功")
        return True

    def capture(self):
        while self.screen.isOpened() and self.isRunning:
            #img即为
            sucess,img=self.screen.read()
            self.img = cv2.flip(img, 1)
            #显示摄像头
            cv2.namedWindow(self.searchWord, 0)
            cv2.imshow(self.searchWord, self.detector(self.img))
            #保持画面的持续。
            k=cv2.waitKey(1)
            if not self.isRunning:
                break
        cv2.destroyAllWindows()
        self.screen.release()
    
    def detector(self, img):
        if self.handDetecting:
            img = self._detector_hands_handle(img)
        if self.faceMeshDetecting:
            img = self._detector_face_mesh_handle(img)
        return img
    
    def _detector_hands_handle(self, image):
        results = self.hands.process(image)

        image.flags.writeable = True
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())
        return image
    
    def _detector_face_mesh_handle(self, image):
        results = self.face_mesh.process(image)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_tesselation_style())
                self.mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_contours_style())
                self.mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_iris_connections_style())
        return image

    
    def open_detector_hands(self, handler):
        self.handDetecting = True
        handler.output('打开成功')
        return True

    def stop_detector_hands(self, handler):
        self.handDetecting = False
        handler.output('关闭成功')
        return True
    
    def open_detector_face_mesh(self, handler):
        self.faceMeshDetecting = True
        handler.output('打开成功')
        return True
    
    def stop_detector_face_mesh(self, handler):
        self.faceMeshDetecting = False 
        handler.output('关闭成功')
        return True

class ExternalDevice(MetaModule):
    """
    适用于外围设备的接口
    """
    def initialize(self, config):
        self.host = config.get('host','')
        self.port = config.get('port',8899)
