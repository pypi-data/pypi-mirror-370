import argparse
import os
from pathlib import Path
from codeformer import inference_app

def main():
    parser = argparse.ArgumentParser(description='CodeFormer Command Line Tool')
    parser.add_argument('-i', '--input', type=str, help='Input directory', default='.')
    args = parser.parse_args()

    # 获取输入目录的绝对路径
    input_dir = Path(args.input).resolve()
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # 支持的图像格式
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # 收集图像文件
    image_files = []
    for item in input_dir.iterdir():
        if item.is_file() and item.suffix.lower() in extensions:
            image_files.append(item)

    # 处理每个图像
    for image_path in image_files:
        output_path = image_path.parent / f"{image_path.stem}-out{image_path.suffix}"
        if output_path.exists():
            print(f"Output file {output_path} already exists. Skipping.")
            continue

        print(f"Processing: {image_path}")
        try:
            inference_app(
                image=str(image_path),
                background_enhance=True,
                face_upsample=True,
                upscale=2,
                codeformer_fidelity=0.5,
                output_path=str(output_path)
            )
            print(f"Saved to: {output_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

if __name__ == '__main__':
    main()