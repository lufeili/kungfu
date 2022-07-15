# 2 Player Kung Fu Game

[简体中文](/README.md) | English

A 2 Player Kung Fu Fighting Game,  with one camera, have fun! based on MMPose

[![Watch the video](https://user-images.githubusercontent.com/15977946/171618680-49968673-6f11-4b9d-b63e-72543e8a75a0.gif)](https://www.bilibili.com/video/BV12t4y147Tw?p=1)

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

### Configure pre-commit hook

```shell
# In mmpose-webcam-demo repo folder
pip install pre-commit
pre-commit install
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
- About "Infinity Pose" MMPose Creative Demo Competition
  - [Event Home Page](https://openmmlab.com/community/mmpose-demo)
  - [Submission](https://github.com/open-mmlab/mmpose/issues/1407)
