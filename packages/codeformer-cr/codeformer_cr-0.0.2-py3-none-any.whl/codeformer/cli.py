import argparse
import os
import sys
from pathlib import Path
from codeformer import inference_app
import cv2
import numpy as np

def main():
    parser = argparse.ArgumentParser(
        description='简易命令', 
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False
    )
    parser.add_argument('-i', '--input', type=str, help='输入图像或目录', required=True)
    parser.add_argument('--bg_upsampler', type=str, help='背景超分辨率模型 默认:启用', default='realesrgan')
    parser.add_argument('--face_upsample', action='store_true', help='启用面部超分辨率 默认:启用', default=True)
    parser.add_argument('--no-face_upsample', action='store_false', dest='face_upsample', help='禁用面部超分辨率')
    parser.add_argument('-w', '--weight', type=float, help='保真0.0 修复1.0 默认:0.7', default=0.7)
    parser.add_argument('-s', '--scale', type=int, help='放大倍数 默认:2', default=2)
    parser.add_argument('-o', '--output', type=str, help='输出路径 可选 默认与输入同目录')
    parser.add_argument('-h', '--help', action='help', help='显示帮助信息并退出')
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()

    # 检查输入是文件还是目录
    input_path = Path(args.input).resolve()
    
    if not input_path.exists():
        print(f"错误: 输入路径 '{input_path}' 不存在。")
        return

    # 支持的图像格式
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # 收集图像文件
    image_files = []
    if input_path.is_file():
        if input_path.suffix.lower() in extensions:
            image_files = [input_path]
        else:
            print(f"错误: 输入文件 '{input_path}' 不是支持的图像格式。")
            return
    else:  # 目录
        for item in input_path.iterdir():
            if item.is_file() and item.suffix.lower() in extensions:
                image_files.append(item)

    if not image_files:
        print("错误: 没有找到支持的图像文件。")
        return

    # 处理每个图像
    for image_path in image_files:
        # 确定输出路径
        if args.output:
            # 如果用户指定了输出路径
            output_path = Path(args.output).resolve()
            if output_path.is_dir() or output_path.suffix == '':
                # 如果输出路径是目录或没有扩展名，则在其中创建输出文件
                output_path = output_path / f"{image_path.stem}-out{image_path.suffix}"
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # 默认行为：与输入文件同目录，添加-out后缀
            output_path = image_path.parent / f"{image_path.stem}-out{image_path.suffix}"

        # 确保输出文件有有效的扩展名
        if output_path.suffix.lower() not in extensions:
            output_path = output_path.with_suffix('.png')
            print(f"警告: 输出文件扩展名不支持，已更改为 PNG 格式: {output_path}")

        if output_path.exists():
            print(f"输出文件 {output_path} 已存在。跳过。")
            continue

        print(f"处理中: {image_path}")
        try:
            # 直接使用 inference_app 保存结果
            inference_app(
                image=str(image_path),
                background_enhance=True,
                face_upsample=args.face_upsample,
                upscale=args.scale,
                codeformer_fidelity=args.weight,
                output_path=str(output_path)
            )
            
            print(f"已保存至: {output_path}")
        except Exception as e:
            print(f"处理 {image_path} 时出错: {e}")

if __name__ == '__main__':
    main()