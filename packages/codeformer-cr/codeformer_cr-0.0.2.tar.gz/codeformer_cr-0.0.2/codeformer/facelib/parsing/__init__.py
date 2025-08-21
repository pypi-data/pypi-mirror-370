import torch
import os
from pathlib import Path

from codeformer.facelib.parsing.bisenet import BiSeNet
from codeformer.facelib.parsing.parsenet import ParseNet
from codeformer.facelib.utils import load_file_from_url

def init_parsing_model(model_name="bisenet", half=False, device="cuda"):
    
    if model_name == "bisenet":
        model = BiSeNet(num_class=19)
        model_url = "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_bisenet.pth"
    elif model_name == "parsenet":
        model = ParseNet(in_size=512, out_size=512, parsing_ch=19)
        model_url = "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth"
    else:
        raise NotImplementedError(f"{model_name} is not implemented.")

    current_dir = Path(__file__).parent
    project_root = current_dir
    while project_root and not (project_root / ".git").exists():
        if project_root.parent == project_root:  # 到达根目录
            project_root = Path.cwd()  # 使用当前工作目录
            break
        project_root = project_root.parent
    models_dir = project_root / "models"

    models_dir.mkdir(exist_ok=True)
    model_path = load_file_from_url(url=model_url, model_dir=str(models_dir), progress=True, file_name=None)
    load_net = torch.load(model_path, map_location=lambda storage, loc: storage)
    model.load_state_dict(load_net, strict=True)
    model.eval()
    model = model.to(device)
    return model