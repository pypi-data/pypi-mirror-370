import os
import cv2
import torch
from torchvision.transforms.functional import normalize
from pathlib import Path

from codeformer.basicsr.archs.rrdbnet_arch import RRDBNet
from codeformer.basicsr.utils import img2tensor, imwrite, tensor2img
from codeformer.basicsr.utils.download_util import load_file_from_url
from codeformer.basicsr.utils.realesrgan_utils import RealESRGANer
from codeformer.basicsr.utils.registry import ARCH_REGISTRY
from codeformer.facelib.utils.face_restoration_helper import FaceRestoreHelper
from codeformer.facelib.utils.misc import is_gray

pretrain_model_url = {
    "codeformer": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth",
    "detection": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/detection_Resnet50_Final.pth",
    "parsing": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth",
    "realesrgan": "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/RealESRGAN_x2plus.pth",
}

# download weights
if not os.path.exists("models/codeformer.pth"):
    load_file_from_url(
        url=pretrain_model_url["codeformer"], model_dir="models", progress=True, file_name=None
    )
if not os.path.exists("models/detection_Resnet50_Final.pth"):
    load_file_from_url(
        url=pretrain_model_url["detection"], model_dir="models", progress=True, file_name=None
    )
if not os.path.exists("models/parsing_parsenet.pth"):
    load_file_from_url(
        url=pretrain_model_url["parsing"], model_dir="models", progress=True, file_name=None
    )
if not os.path.exists("models/RealESRGAN_x2plus.pth"):
    load_file_from_url(
        url=pretrain_model_url["realesrgan"], model_dir="models", progress=True, file_name=None
    )


def imread(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


# set enhancer with RealESRGAN
def set_realesrgan():
    half = True if torch.cuda.is_available() else False
    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=2,
    )
    upsampler = RealESRGANer(
        scale=2,
        model_path="models/RealESRGAN_x2plus.pth",
        model=model,
        tile=400,
        tile_pad=40,
        pre_pad=0,
        half=half,
    )
    return upsampler


upsampler = set_realesrgan()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
codeformer_net = ARCH_REGISTRY.get("CodeFormer")(
    dim_embd=512,
    codebook_size=1024,
    n_head=8,
    n_layers=9,
    connect_list=["32", "64", "128", "256"],
).to(device)
ckpt_path = "models/codeformer.pth"
checkpoint = torch.load(ckpt_path)["params_ema"]
codeformer_net.load_state_dict(checkpoint)
codeformer_net.eval()

# 移除全局的 os.makedirs("output", exist_ok=True) 调用


def inference_app(image, background_enhance=True, face_upsample=True, upscale=2, codeformer_fidelity=0.5, output_path=None):
    # take the default setting for the demo
    has_aligned = False
    only_center_face = False
    draw_box = False
    detection_model = "retinaface_resnet50"
    print("Inp:", image, background_enhance, face_upsample, upscale, codeformer_fidelity)

    img = cv2.imread(str(image), cv2.IMREAD_COLOR)
    print("\timage size:", img.shape)

    upscale = int(upscale)  # convert type to int
    if upscale > 4:  # avoid memory exceeded due to too large upscale
        upscale = 4
    if upscale > 2 and max(img.shape[:2]) > 1000:  # avoid memory exceeded due to too large img resolution
        upscale = 2
    if max(img.shape[:2]) > 1500:  # avoid memory exceeded due to too large img resolution
        upscale = 1
        background_enhance = False
        face_upsample = False

    face_helper = FaceRestoreHelper(
        upscale,
        face_size=512,
        crop_ratio=(1, 1),
        det_model=detection_model,
        save_ext="png",
        use_parse=True,
        device=device,
    )
    bg_upsampler = upsampler if background_enhance else None
    face_upsampler = upsampler if face_upsample else None

    if has_aligned:
        # the input faces are already cropped and aligned
        img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
        face_helper.is_gray = is_gray(img, threshold=5)
        if face_helper.is_gray:
            print("\tgrayscale input: True")
        face_helper.cropped_faces = [img]
    else:
        face_helper.read_image(img)
        # get face landmarks for each face
        num_det_faces = face_helper.get_face_landmarks_5(
            only_center_face=only_center_face, resize=640, eye_dist_threshold=5
        )
        print(f"\tdetect {num_det_faces} faces")
        # align and warp each face
        face_helper.align_warp_face()

    # face restoration for each cropped face
    for idx, cropped_face in enumerate(face_helper.cropped_faces):
        # prepare data
        cropped_face_t = img2tensor(cropped_face / 255.0, bgr2rgb=True, float32=True)
        normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
        cropped_face_t = cropped_face_t.unsqueeze(0).to(device)

        try:
            with torch.no_grad():
                output = codeformer_net(cropped_face_t, w=codeformer_fidelity, adain=True)[0]
                restored_face = tensor2img(output, rgb2bgr=True, min_max=(-1, 1))
            del output
            torch.cuda.empty_cache()
        except RuntimeError as error:
            print(f"Failed inference for CodeFormer: {error}")
            restored_face = tensor2img(cropped_face_t, rgb2bgr=True, min_max=(-1, 1))

        restored_face = restored_face.astype("uint8")
        face_helper.add_restored_face(restored_face)

    # paste_back
    if not has_aligned:
        # upsample the background
        if bg_upsampler is not None:
            # Now only support RealESRGAN for upsampling background
            bg_img = bg_upsampler.enhance(img, outscale=upscale)[0]
        else:
            bg_img = None
        face_helper.get_inverse_affine(None)
        # paste each restored face to the input image
        if face_upsample and face_upsampler is not None:
            restored_img = face_helper.paste_faces_to_input_image(
                upsample_img=bg_img,
                draw_box=draw_box,
                face_upsampler=face_upsampler,
            )
        else:
            restored_img = face_helper.paste_faces_to_input_image(upsample_img=bg_img, draw_box=draw_box)

    # 修改保存逻辑，支持自定义输出路径
    if output_path is None:
        # 如果没有指定输出路径，使用默认路径
        os.makedirs("output", exist_ok=True)
        save_path = "output/out.png"
    else:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        save_path = output_path
    
    imwrite(restored_img, str(save_path))
    return save_path


def batch_inference_app(input_dir, output_dir, background_enhance=True, face_upsample=True, upscale=2, codeformer_fidelity=0.5):
    """
    批量处理目录中的所有图像
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
        background_enhance (bool): 是否增强背景
        face_upsample (bool): 是否对人脸进行超采样
        upscale (int): 放大倍数
        codeformer_fidelity (float): 保真度参数(0更清晰，1更保真)
    """
    # 支持的图像格式
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有图像文件（不区分大小写）
    input_path = Path(input_dir)
    image_files = []
    for item in input_path.iterdir():
        if item.is_file() and item.suffix.lower() in extensions:
            image_files.append(item)
    
    # 处理每个图像
    results = {}
    for image_path in image_files:
        output_path = Path(output_dir) / f"{image_path.stem}_enhanced{image_path.suffix}"
        
        try:
            result_path = inference_app(
                image=str(image_path),
                background_enhance=background_enhance,
                face_upsample=face_upsample,
                upscale=upscale,
                codeformer_fidelity=codeformer_fidelity,
                output_path=str(output_path)
            )
            results[str(image_path)] = result_path
        except Exception as e:
            results[str(image_path)] = f"Error: {str(e)}"
    
    return results