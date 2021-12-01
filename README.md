## 自制智障语音助手  

### Quick Start  
1. 在终端运行命令`pip install -r requirements.txt`
2. 运行`server.py`文件  
3. `order.md`文件中包含一些基本的命令

示例
```
启动相机
打开手势检测
打开人脸检测
退出相机窗口

显示微信窗口
最大化微信窗口
退出窗口

百度搜索语音识别
必应搜索语音识别
```

> 默认使用`文本输入模式`  

### 使用安卓语音识别模式
如果要把输入的模式改成远程语音输入，只需要更改`config`文件夹下面的`constants.py`文件
```python
# 输入模式， 语音模式: voice 文本输入模式: text
INPUT_MODE = "voice"
# 输入的位置， 来自本地的输入: local 来自端口的输入: remote
INPUT_POSITION = "remote"
```
在手机上安装`voices.apk`软件, 并根据`server.py`文件运行时显示的服务器`host`设置`host`  

> 手机和电脑需要在同一个局域网内

### 使用自己的api  
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

1. `alias/global.yml`文件是全局配置文件, 负责配置一些内置的指令  
2. `constants.py`文件包含一些程序运行时需要的常量  
3. `user-config.yml`文件是用户自定义配置文件, 你可以在使用过程中根据需要进行配置  

您可以自主添加需要的配置文件, 并在`config/constants.py`中添加即可  
```python  
USER_CONFIGURATIONS = ["user-config.yml","website-config.json"]
```

### 配置自己的指令  
如果需要配置本身不存在的指令， 那么您可以选择自定义一个类(推荐您在`modules/user_modules.py`文件中定义)并继承元组件库中的对象，自定义需要的操作  
例如：  

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
    - `operations`: 多层指令，可以由父指令递归下去
    - `method`: 执行的函数

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
            "method": "self.hole"
        }
    ]
}
```

```yml
PowerPoint:
  operations:
    - 
      keys:
        - 新建
      shotkeys:
        - '^n'
        - '%n'
        - 'l'
        - '1'
    - 
      keys:
        - 最近
      operations:
        - 
          keys:
            - 打开
          shotkeys:
            - '%h'
            - 'y'
            - 'f'
    - 
      keys:
        - 放映
      operations:
        - 
          keys:
            - 开始
          shotkeys:
            - '{F5}'
    -
      keys:
        - 下一页
        - 下一张
      shotkeys:
        - '{DONW}'
    -
      keys:
        - 上一页
        - 上一张
      shotkeys:
        - '{UP}'
```

这里的`打开`就可以分两种情况, 一种是`打开全部`, 另一种是`打开最近`  

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
`Camera`: 提供了电脑本身摄像头的支持  
`Software`: 所有软件的公有父类  
