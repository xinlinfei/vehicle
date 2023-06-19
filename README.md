# vehicle
车牌定位及识别，精度较低，仅供学习参考

# usage

## 下载依赖
```
pip install paddleocr
```
### 有CUDA环境
```
conda install paddlepaddle-gpu==2.4.2 cudatoolkit=11.7 -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/Paddle/ -c conda-forge
```
### 无CUDA环境
```
ocr = paddleocr.PaddleOCR(use_angle_cls=True, use_gpu=True, lang="ch")use_gpu设置为false
conda install paddlepaddle==2.4.2 --channel https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/Paddle/
```
## 运行
```
python main.py
```

