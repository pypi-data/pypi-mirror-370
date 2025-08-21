# CodeFormer-CR

一个简化的 [CodeFormer](https://github.com/sczhou/CodeFormer) 命令行工具，用于图像增强和人脸修复。

该存储库来自 [codeformer-pip](https://github.com/kadirnar/codeformer-pip) ，并在其基础上进行了修改和优化。

## 安装
```bash
pip install codeformer-cr
```

## 简易命令
```bash
cr            # 当前目录修复所有图像，输出与当前目录一致
cr -i input   # 指定图像或目录修复所有图像，输出与输入目录一致
cr -h         # 显示参数信息
```


## Citation 
```bash
@inproceedings{zhou2022codeformer,
    author = {Zhou, Shangchen and Chan, Kelvin C.K. and Li, Chongyi and Loy, Chen Change},
    title = {Towards Robust Blind Face Restoration with Codebook Lookup TransFormer},
    booktitle = {NeurIPS},
    year = {2022}
}
```

License
This project is licensed under NTU S-Lab License 1.0. Redistribution and use should follow this license.




