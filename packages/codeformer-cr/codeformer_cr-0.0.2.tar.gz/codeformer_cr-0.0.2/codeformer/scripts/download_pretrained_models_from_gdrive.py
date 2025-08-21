import argparse
import os
from os import path as osp

import gdown

def download_pretrained_models(file_ids):
    # 修改保存路径为项目根目录下的 models 文件夹
    save_path_root = "models"
    os.makedirs(save_path_root, exist_ok=True)

    for file_name, file_id in file_ids.items():
        file_url = "https://drive.google.com/uc?id=" + file_id
        save_path = osp.abspath(osp.join(save_path_root, file_name))
        if osp.exists(save_path):
            user_response = input(f"{file_name} already exist. Do you want to cover it? Y/N\n")
            if user_response.lower() == "y":
                print(f"Covering {file_name} to {save_path}")
                gdown.download(file_url, save_path, quiet=False)
            elif user_response.lower() == "n":
                print(f"Skipping {file_name}")
            else:
                raise ValueError("Wrong input. Only accepts Y/N.")
        else:
            print(f"Downloading {file_name} to {save_path}")
            gdown.download(file_url, save_path, quiet=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "method", type=str, help=("Options: 'CodeFormer' 'facelib'. Set to 'all' to download all the models.")
    )
    args = parser.parse_args()

    file_ids = {
        "CodeFormer": {"codeformer.pth": "1v_E_vZvP-dQPF55Kc5SRCjaKTQXDz-JB"},
        "facelib": {
            "yolov5l-face.pth": "131578zMA6B2x8VQHyHfa6GEPtulMCNzV",
            "parsing_parsenet.pth": "16pkohyZZ8ViHGBk3QtVqxLZKzdo466bK",
        },
    }

    if args.method == "all":
        # 合并所有文件ID到一个字典
        all_files = {}
        for method_files in file_ids.values():
            all_files.update(method_files)
        download_pretrained_models(all_files)
    else:
        download_pretrained_models(file_ids[args.method])