## 自制智障语音助手  

### 运行  
1. 去百度AI开放平台`https://ai.baidu.com/tech/speech/asr`注册  
2. 得到百度AI开放平台语音识别的`APP_ID`, `API_KEY`, `SCRET_KEY`
3. 打开本项目`config`文件夹下面的`constants.py`文件, 替换里面的`BAIDU_APP_ID`, `BAIDU_API_KEY`, `BAIDU_SCRET_KEY`
4. 在终端运行命令`pip install -r requirements.txt`
5. 运行`server.py`文件  
6. 在手机上安装`voices.apk`软件, 并根据`server.py`文件运行时显示的服务器`host`设置`host`  
7. enjoy

### 包详解  
```
config -- 配置包
handler.py -- 指令的分词并调用对应元件执行
server.py -- 程序入口  
requirements.txt -- 项目所需的python依赖  
```

### 配置  
项目的所有配置文件都在`config`包里

1. `configuration.json`文件是全局配置文件, 负责配置一些内置的指令  
2. `constants.py`文件包含一些程序运行时需要的常量  
3. `user-config.json`文件是用户自定义配置文件, 你可以在使用过程中根据需要进行配置  

您可以自主添加需要的配置文件, 并在`config/constants.py`中添加即可  
```python  
USER_CONFIGURATIONS = ["user-config.json","website-config.json"]
```

### 配置自己的指令  
如果需要配置本身不存在的指令， 那么您可以选择自定义一个类(推荐您在`modules/user_modules.py`文件中定义)并继承元组件库中的对象，自定义需要的操作  
例如：  

`modules/user_modules.py`  
```python  
class PowerPoint(Software):
    """
    自定义软件PowerPoint，继承元组件 Software
    """
    def __init__(self, name='', config=None, configName='PowerPoint'):
        """
        PowerPoint的初始化操作
        name: 软件实例的名称，配置文件中若没有配置keywords在默认使用name作为keyword
        config: 自定义配置 / 一般不用
        configName: 该软件在配置文件中的配置名, 省略时使用name来替代
        """
        # 读取配置
        config = self.load_config(name,config, configName)
        # 软件的私有配置
        self.execPath = config.get('execPath','')

        # 父类初始化， 形式基本固定 
        super().__init__(
            name=name,
            config=config,
            configName=configName
        )
        # 软件本身的初始化 和前面的区别是这里的PowerPoint是所有这个软件的实例都有的配置
        self.initialize("PowerPoint")
    
    
    def newppt(self, handle, key):
        """
        配置一个newppt操作，此操作会向powerpoint 依次发送alt+n , Shift+n , l , 1指令
        用来打开一个空白ppt
        """
        send_keys('^n'
        '%n'
        'l'
        '1'
        )
        # 语音播报
        handle.output("{}".format(key))

    def showppt(self, handle, key):
        send_keys('{F5}'
        )
        handle.output("{}".format(key))
```

`config/user-config.json`
```json
"PowerPoint": {
    "execPath": "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\PowerPoint.lnk",
    "keywords": ["展示"],
    "searchWord": "PowerPoint",
    "operations": [
        {
            "keys": ["新建"],
            "shotkeys": ["^n", "%n", "l", "1"]
        },
        {
            "keys": ["打开"],
            "sub": [
                {
                    "keys":["最近"],
                    "shotkeys": ["%h", "y","f"]
                }
            ]
        }
    ]
}
```

- `keywords`: 命令的关键字  
- `searchWord`: 搜索窗口时的关键字， 打开一个`window`窗口时的窗口标题，本软件根据窗口标题来找到对应窗口， 比如说`PowerPoint`窗口里一定有`powerpoint`这个单词  
- `operations`: 这个类支持的指令  
    - `keys`: 指令的关键词  
    - `shotkeys`: 发送快捷键到窗口  
    - `sub`: 多层指令，可以由父指令递归下去
    - `do`: 执行的函数

```json
{
    "keys": ["打开"],
    "sub": [
        {
            "keys":["最近"],
            "shotkeys": ["%h", "y","f"]
        },
        {
            "keys":["全部"],
            "do": "self.hole"
        }
    ]
}
```
这里的`打开`就可以分两种情况, 一种是`打开全部`, 另一种是`打开最近`  

最后，只需要在`server.py`文件中,

`server.py`
```python 
ppt = PowerPoint("展示")

modules = [
    ppt
]
```
把对象初始化并加入到`modules`列表中就可以了

### 快捷键列表  
```
SHIFT                            +      
CTRL                             ^      
ALT                               %
空格键                            {SPACE}

BACKSPACE                        {BACKSPACE}、{BS}   or   {BKSP}      
BREAK                            {BREAK}      
CAPS   LOCK                      {CAPSLOCK}      
DEL   or   DELETE                {DELETE}   or   {DEL}      
DOWN   ARROW                     {DOWN}      
END                              {END}      
ENTER                            {ENTER}   or   ~      
ESC                              {ESC}      
HELP                             {HELP}      
HOME                             {HOME}      
INS   or   INSERT                {INSERT}   or   {INS}      
LEFT   ARROW                     {LEFT}      
NUM   LOCK                       {NUMLOCK}      
PAGE   DOWN                      {PGDN}      
PAGE   UP                        {PGUP}      
PRINT   SCREEN                   {PRTSC}      
RIGHT   ARROW                    {RIGHT}      
SCROLL   LOCK                    {SCROLLLOCK}      
TAB                              {TAB}      
UP   ARROW                       {UP}     
+                                {ADD}      
-                                {SUBTRACT}      
*                                {MULTIPLY}      
/                                {DIVIDE}
```

### Build_in文件详解  

`MetaModule`: 元组件，是所有组件的父类，定义了指令运行的逻辑  
`ExternalDevice`: 外置组件，通过`socket`编程支持远程控制其他硬件  
`Window`: 所有`window`窗口的公有父类  
`NormalWindow`: 对所有未被特殊处理的窗口的统一支持,比如`显示微信窗口`  
`Camera`: 提供了电脑本身摄像头的支持  
`Software`: 所有软件的公有父类  
`UiaSoftware`: 提供对所有以`uia`做后台的软件的同意支持  
`ScreenCanvas`: 使用`pyqt5`的内置浏览器做后台的模拟浏览器，是本项目可以方便的集成前端的`svg`,`html`等等, 相当于把电脑显示器当成了一个`canvas`  
`EelScreenCanvas`: 使用`eel`库作为后台的模拟浏览器，目前未完善  
