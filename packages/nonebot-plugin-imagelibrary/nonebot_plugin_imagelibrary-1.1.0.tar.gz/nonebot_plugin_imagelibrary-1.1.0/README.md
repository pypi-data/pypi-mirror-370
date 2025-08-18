# _✨ ImageLibrary Bot图库 ✨_
### 一个共享给所有人的Bot图库
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

## 安装方法
1. 通过nb-cli安装
```shell
nb plugin install nonebot_plugin_ImageLibrary
```

2. 通过pip安装
```shell
pip install nonebot_plugin_ImageLibrary
```
pip 安装后在 Nonebot2 入口文件(例如 bot.py )增加：

```python
nonebot.load_plugin("onebot_plugin_ImageLibrary")
```

## 使用方式
### `==所有人可用==`
* 添加[XXX]: 可以向图库中添加XXX关键词视频/图片/文字内容
> **添加咖波** --> 发送视频/图片/文字 --> 完成，保存到了咖波关键词下
* 来个/来只/来点[XXX]: 抽取图库中XXX关键词下的内容
> **来只咖波** --> 收到一张咖波关键词下的随机内容
* XXX后面接@[数字]可以选择词条下的指定内容
> **来只咖波@3** --> 收到在咖波关键词下序号为3的内容
* 插画[XXX]: 从网络引擎中获取XXX的随机高清图片
> **插画 伊蕾娜** --> 从网络上获取一张伊蕾娜的插画
### `==管理员可用==`

* @bot 启用/禁用XXX: 允许/禁用群内使用某一词条
* * 设定了禁用的词条不再可以从私聊获取
> **禁用咖波** --> 在群内禁用咖波关键词，并且私聊咖波关键词不再可用
* @bot 删除XXX: 删除某一词条的部分内容
* * 只删[数字]: 删除关键词下指定的内容
* * 彻底删除: 删除整个词条
> **删除咖波** --> 只删5/彻底删除 --> 从图库删除关键词下某一个序号或所有内容
* @bot 图片列表: 查看图库中的所有关键词
> **图片列表** --> 获取机器人下所有的关键词列表

### `==Bot主可用==`
* @bot 独占/取消独占: 让某个群聊独占/取消独占一个关键词，其他群和私聊不可用
> **独占咖波** --> 仅允许在此群内使用某一关键词

## 后台管理
所有图片和视频都会放在工作目录`/imageLibrary/Library`下保存，文字内容直接保存在`/imageLibrary/Library/image.json`中

所有关键词检索可以通过修改`/imageLibrary/Library/image.json`来手动管理

## 额外配置
你可以修改代码中的原始字段来决定相对工作目录的保存位置
```python
dataset = DataSetControl("./image_library/image.json")  # 决定关键词列表的保存路径
base = "./image_library/library/"  # 决定图片视频的存储路径
```