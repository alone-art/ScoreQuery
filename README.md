# ScoreQuery

#### 依赖环境

##### paddle

```
https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/develop/install/pip/windows-pip.html
```

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

图片中有COST级别时命令可省略COST级别，后面将会通过判断主词条等进行识别COST级别。
截图需要包含主词条。

