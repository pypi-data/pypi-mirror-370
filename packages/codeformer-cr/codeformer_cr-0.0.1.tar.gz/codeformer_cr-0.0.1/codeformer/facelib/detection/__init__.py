import os
from copy import deepcopy
import logging
from os import path as osp

import torch
from codeformer.facelib.detection.yolov5face.models.common import Conv
from codeformer.facelib.utils import download_pretrained_models, load_file_from_url
from torch import nn

from codeformer.facelib.detection.retinaface.retinaface import RetinaFace
from codeformer.facelib.detection.yolov5face.face_detector import YoloDetector



def init_detection_model(model_name, half=False, device="cuda"):
    if "retinaface" in model_name:
        model = init_retinaface_model(model_name, half, device)
    elif "YOLOv5" in model_name:
        model = init_yolov5face_model(model_name, device)
    else:
        raise NotImplementedError(f"{model_name} is not implemented.")

    return model


def init_retinaface_model(model_name, half=False, device="cuda"):
    if model_name == "retinaface_resnet50":
        model = RetinaFace(network_name="resnet50", half=half)
        model_url = "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/detection_Resnet50_Final.pth"
    elif model_name == "retinaface_mobile0.25":
        model = RetinaFace(network_name="mobile0.25", half=half)
        model_url = "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/detection_mobilenet0.25_Final.pth"
    else:
        raise NotImplementedError(f"{model_name} is not implemented.")

    current_working_dir = os.getcwd()
    
    project_root = current_working_dir
    while project_root and not os.path.exists(os.path.join(project_root, '.git')):
        project_root = os.path.dirname(project_root)
        if project_root == os.path.dirname(project_root):  # 到达根目录
            project_root = current_working_dir
            break
    
    # 设置模型目录为项目根目录下的 models 文件夹
    models_dir = os.path.join(project_root, 'models')
    
    # 确保目录存在
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = load_file_from_url(url=model_url, model_dir=models_dir, progress=True, file_name=None)
    
    load_net = torch.load(model_path, map_location=lambda storage, loc: storage)
    # remove unnecessary 'module.'
    for k, v in deepcopy(load_net).items():
        if k.startswith("module."):
            load_net[k[7:]] = v
            load_net.pop(k)
    model.load_state_dict(load_net, strict=True)
    model.eval()
    model = model.to(device)

    return model


def init_yolov5face_model(model_name, device="cuda"):
    if model_name == "YOLOv5l":
        model = YoloDetector(config_name="facelib/detection/yolov5face/models/yolov5l.yaml", device=device)
        model_url = "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/yolov5l-face.pth"
    elif model_name == "YOLOv5n":
        model = YoloDetector(config_name="facelib/detection/yolov5face/models/yolov5n.yaml", device=device)
        model_url = "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/yolov5n-face.pth"
    else:
        raise NotImplementedError(f"{model_name} is not implemented.")

    
    # 获取当前工作目录和项目根目录
    current_working_dir = os.getcwd()

    # 尝试确定项目根目录
    # 假设项目根目录是包含 .git 文件夹的目录
    project_root = current_working_dir
    while project_root and not os.path.exists(os.path.join(project_root, '.git')):
        project_root = os.path.dirname(project_root)
        if project_root == os.path.dirname(project_root):  # 到达根目录
            project_root = current_working_dir
            break
    
    # 设置模型目录为项目根目录下的 models 文件夹
    models_dir = os.path.join(project_root, 'models')
    
    # 确保目录存在
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = load_file_from_url(url=model_url, model_dir=models_dir, progress=True, file_name=None)
    
    load_net = torch.load(model_path, map_location=lambda storage, loc: storage)
    model.detector.load_state_dict(load_net, strict=True)
    model.detector.eval()
    model.detector = model.detector.to(device).float()

    for m in model.detector.modules():
        if type(m) in [nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6, nn.SiLU]:
            m.inplace = True  # pytorch 1.7.0 compatibility
        elif isinstance(m, Conv):
            m._non_persistent_buffers_set = set()  # pytorch 1.6.0 compatibility

    return model