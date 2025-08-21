import argparse
import os
from os import path as osp

from basicsr.utils.download_util import load_file_from_url


def download_pretrained_models(method, file_urls):
    # 修改保存路径为项目根目录下的 models 文件夹
    save_path_root = "models"
    os.makedirs(save_path_root, exist_ok=True)

    for file_name, file_url in file_urls.items():
        save_path = load_file_from_url(url=file_url, model_dir=save_path_root, progress=True, file_name=file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "method", type=str, help=("Options: 'CodeFormer' 'facelib' 'dlib'. Set to 'all' to download all the models.")
    )
    args = parser.parse_args()

    file_urls = {
        "CodeFormer": {
            "codeformer.pth": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth"
        },
        "facelib": {
            # 'yolov5l-face.pth': 'https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/yolov5l-face.pth',
            "detection_Resnet50_Final.pth": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/detection_Resnet50_Final.pth",
            "parsing_parsenet.pth": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth",
        },
        "dlib": {
            "mmod_human_face_detector-4cb19393.dat": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/mmod_human_face_detector-4cb19393.dat",
            "shape_predictor_5_face_landmarks-c4b1e980.dat": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/shape_predictor_5_face_landmarks-c4b1e980.dat",
        },
    }

    if args.method == "all":
        # 当选择'all'时，合并所有文件URL
        all_files = {}
        for method_files in file_urls.values():
            all_files.update(method_files)
        download_pretrained_models("all", all_files)
    else:
        download_pretrained_models(args.method, file_urls[args.method])