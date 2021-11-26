import os
import sys
import threading
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui

from assistantlib.configuration import Configuration

resource_path = 'resources'
pet_images_dir = 'pet'
# 动作组
actions_config = {
    'MoveLeft' :[2, 3],
    '放精灵球':[37,41],
    '放电':[42,46],
    'MoveRight' :[47, 48]
} 


class Pet(QWidget):

    def __init__(self):
        super().__init__()

        # 初始化
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 动作库
        self.actions, iconpath = self._load_actions()

		# 设置系统托盘选项
        quit_action = QAction('exit', self, triggered=self.quit)
        quit_action.setIcon(QIcon(iconpath))
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(iconpath))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()

        self.iconImage = self.loadImage(iconpath)
        self.image = QLabel(self)
        self.setImage(self.iconImage)

        # 是否跟随鼠标
        self.is_follow_mouse = False
        # 宠物拖拽时避免鼠标直接跳到左上角
        self.mouse_drag_pos = self.pos()
        # 显示
        self.resize(128, 128)
        self.show()

        self.action_images = []
        self.action_pointer = 0
        self.action_max_len = 0
        self.isRunning = False
        self.waitQueue = []
        self.method = None
        self.args = None
        self.timer = QTimer()
        self.times = 0
        self.timer.timeout.connect(self.runFrame)
    
    def runAction(self, name, interval=200, method=None, args=None):
        """
        name:动作名
        interval:动作间隔
        method:动作附加行为
        args: 行为参数
        """
        if not self.isRunning:
            self.isRunning = True
            self.action_images = self.actions[name]
            self.action_max_len = len(self.action_images)
            self.action_pointer = 0
            self.method = method
            if args == None:
                args = {}
            self.args = args
            self.timer.start(interval)       
        else:
            self.waitQueue.append([name,interval,method, args])

    def runFrame(self):
        '''
        完成动作的每一帧
        '''
        self.setImage(self.action_images[self.action_pointer])
        self.action_pointer += 1
        if self.action_pointer == self.action_max_len:
            self.nextAction()
        if self.method != None:
            eval(self.method)(self.args)
    
    def nextAction(self):
        self.isRunning = False
        self.Method = None
        self.timer.stop()
        if len(self.waitQueue) > 0:
            action = self.waitQueue.pop(0)
            self.runAction(*action)
    
    def _load_actions(self):
        pet_images_path = os.path.join(resource_path, pet_images_dir)
        actions = {}
        for name, action in actions_config.items():
            images = [self.loadImage(os.path.join(pet_images_path, 'shime'+str(item)+'.png')) for item in range(action[0],action[1]+1)]
            actions[name] = images
        return actions, os.path.join(pet_images_path, 'icon.png')
    
    def setImage(self, image):
        '''
        设置当前显示的图片
        '''
        self.image.setPixmap(QPixmap.fromImage(image))

    def loadImage(self, path):
        image = QImage()
        image.load(path)
        return image

    def mousePressEvent(self, event):
        '''
        鼠标左键按下时, 宠物将和鼠标位置绑定
        '''
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        '''
        鼠标移动, 则宠物也移动
        '''
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        '''
        鼠标释放时, 取消绑定
        '''
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def quit(self):
        """
        退出
        """
        self.close()
        sys.exit()

    def moveTo(self, args):
        if not args.__contains__('except'):
            args['except'] = 'self.times > 1'
        if not args.__contains__('interval'):
            args['interval'] = 200
        
        if not self.isRunning:
            if not eval(args['except']):
                self.runAction(args['action'], args['interval'], 'self.moveTo', args)
                self.times += 1
            else:
                self.times = 0
                self.setImage(self.iconImage)
                self.nextAction()
        self.move(QPoint(eval(args['stepX']), eval(args['stepY'])))

def start(configuration):
    app = QApplication(sys.argv)
    pet = Pet()
    configuration.pet = pet
    pet.moveTo({
        'step':200,
        'action': 'MoveLeft',
        'stepX': 'self.x()-20',
        'stepY': 'self.y()',
        'except': 'self.x() < 2000'
    })
    # pet.moveTo({
    #     'step':200,
    #     'action': 'MoveRight',
    #     'stepX': 'self.x()+20',
    #     'stepY': 'self.y()',
    #     'except': 'self.x() > self.desktop.width()-150'
    # })
    app.exec_()

configuration =  Configuration()
thread = threading.Thread(target=start, args=[configuration])
thread.start()
while True:
    msg = input(">>>")
    if msg == 'left':
        configuration.pet.moveTo({
            'step':200,
            'action': 'MoveLeft',
            'stepX': 'self.x()-20',
            'stepY': 'self.y()',
            'except': 'self.x() < 1000'
        })