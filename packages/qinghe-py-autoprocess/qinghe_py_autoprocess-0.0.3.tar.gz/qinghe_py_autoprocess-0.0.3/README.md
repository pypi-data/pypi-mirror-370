# qinghe_py_autoprocess

视频音轨提取与变速处理工具

## 安装

```bash
pip install .
```

## 使用

```bash
slowdown input.mp4 -o output.wav -s 0.8
```

## 参数说明
- `input`: 输入视频文件路径
- `-o/--output`: 输出音频文件路径 (默认: output_slow1.wav)
- `-s/--speed`: 变速系数 (默认: 0.95)

## tips
- `import ffmpeg`: 依赖ffmpeg模块
