# 双人武术格斗

简体中文 | [English](/README_en.md)

双人武术格斗游戏，只需一个摄像头，简单而富有乐趣，来试试吧！
基于 MMPose人体姿态估计技术

[![demo](https://user-images.githubusercontent.com/108378035/179365172-73c5c6dd-6768-4736-a06a-4ef6992b392b.jpg)](https://www.bilibili.com/video/BV12t4y147Tw?p=1)

演示视频：https://www.bilibili.com/video/BV12t4y147Tw?p=1

## 游戏操作说明
```
准备：两位选手分别站在摄像头视野的左右两侧，使两位选手完整身体分别出现在左右两个窗口内
开始游戏：两位选手都要举手超过头顶
结束游戏：按‘Esc’键
冲拳：抬手过肩
踢腿：抬起左脚
飞踢：抬起右脚
```

## 配置环境

### 安装 Pygame

```shell
pip install pygame
```

### 安装 MMCV 和 MMDetection

```shell
pip install openmim
mim install mmcv-full
pip install mmdet
```

### 安装 MMPose

```shell
cd ..
git clone https://github.com/open-mmlab/mmpose.git
cd mmpose
pip install -e .
```

### 安装本游戏

```shell
cd ..
git clone https://github.com/lufeili/kungfu.git

```

## 运行游戏

```shell
cd kungfu
python run.py 

```

## 相关链接

- 关于摄像头应用接口（MMPose Webcam API）
  - [教程文档](https://mmpose.readthedocs.io/zh_CN/latest/tutorials/7_webcam_api.html)
  - [API 查询](https://mmpose.readthedocs.io/zh_CN/latest/api.html#mmpose-apis-webcam)
- 关于 MMPose
  - [代码仓库](https://github.com/open-mmlab/mmpose)
  - [使用文档](https://mmpose.readthedocs.io/zh_CN/latest/)
  - [模型池](https://mmpose.readthedocs.io/zh_CN/latest/modelzoo.html)

