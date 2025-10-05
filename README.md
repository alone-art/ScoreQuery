# ScoreQuery

#### 依赖环境

##### paddle

[https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/develop/install/pip/windows-pip.html](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/develop/install/pip/windows-pip.html)

安装paddle gpu版本需要对应cuda驱动版本，查看cuda版本方法之一：

打开nvidia控制面板，左下角系统信息，组件，栏3D设置，产品名称NVIDIA CUDA xx.x.xx driver，xx.x.xx对应版本号。

##### tesseract(未使用)



#### paddleocr安装

```
python -m pip install paddleocr
```

使用过程可能出现其他问题，比如numpy依赖版本需要小于2，可以先尝试运行OcrTest目录下的test_paddleocr.py。



#### 其他依赖

ccache，会导致警告，需要额外安装ccache。

```
https://github.com/ccache/ccache/releases
```

下载后解压，将解压文件目录添加至环境变量path。



#### 部署方式

此插件依赖于插件WutheringWavesUID。

```
├── gsuid_core
│   ├── gsuid_core
│   │   ├── plugins
│   │   │   ├── WutheringWavesUID
│   │   │   ├── ScoreQuery


cd gsuid_core/gsuid_core/plugins
git clone --depth=1 https://github.com/alone-art/ScoreQuery
```



#### 增加引用消息支持

我在gs_core没有找到关于获取引用消息的方法，于是对nonebot2插件GenshinUID进行了改动：
GenshinUID/`__init__`.py

```
    # onebot
    elif bot.adapter.get_name() == 'OneBot V11':
        from nonebot.adapters.onebot.v11.event import (
            GroupMessageEvent,
            PrivateMessageEvent,
        )

        if isinstance(ev, GroupMessageEvent) or isinstance(
            ev, PrivateMessageEvent
        ):
            messages = ev.original_message
            msg_id = str(ev.message_id)
            if ev.sender.role == 'owner':
                pm = 2
            elif ev.sender.role == 'admin':
                pm = 3

            sender = ev.sender.dict(exclude_none=True)
            sender['avatar'] = f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640'

            if isinstance(ev, GroupMessageEvent):
                user_type = 'group'
                group_id = str(ev.group_id)
            else:
                user_type = 'direct'
+
+            if ev.reply:
+                message.append(Message('reply_content', ev.reply.json()))
        else:
            logger.debug('[gsuid] 不支持该 onebotv11 事件...')
            return
```



#### 插件使用

```
[图片]ww查分[角色名][1c/3c/4c]
```

如：

```
[图片]ww查分月
[图片]ww查分月1c
[图片]ww查分月3c
[图片]ww查分月4c
```

引用消息查分：

```
[引用消息]ww查分月
[引用消息]ww查分月1c
```

当引用消息存在多个图片，想指定图片：

```
[引用消息]ww查分月1c 图1
```

图片中有COST级别时命令可省略COST级别，后面将会通过判断主词条等进行识别COST级别。
截图需要包含主词条。

