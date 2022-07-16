# 2 Player Kung Fu Game

[简体中文](/README.md) | English

2 Player Kung Fu Fighting Game,  with one camera, have fun! based on MMPose
![demo](https://user-images.githubusercontent.com/108378035/179365172-73c5c6dd-6768-4736-a06a-4ef6992b392b.jpg)
Bilibili：https://www.bilibili.com/video/BV12t4y147Tw?p=1

## Guide
```
START: Raise hands above head        
EXIT: Press 'Esc'
Punch: Left or Right hand Up
Kick: Left leg Up
Flying Kick: Right leg Up
```


## Configure Environment

### Install MMCV and MMDetection

```shell
pip install openmim
mim install mmcv-full
pip install mmdet
```

### Install MMPose

```shell
cd ..
git clone clone https://github.com/open-mmlab/mmpose.git
cd mmpose
pip install -e .
```


## Run the Demo

```shell
python run.py
```

## Useful Links

- Webcam API
  - [Tutorial](https://mmpose.readthedocs.io/en/latest/tutorials/7_webcam_api.html)
  - [API Reference](https://mmpose.readthedocs.io/en/latest/api.html#mmpose-apis-webcam)
- MMPose
  - [Code](https://github.com/open-mmlab/mmpose)
  - [Documentation](https://mmpose.readthedocs.io/en/latest/)
  - [Model Zoo](https://mmpose.readthedocs.io/en/latest/modelzoo.html)
