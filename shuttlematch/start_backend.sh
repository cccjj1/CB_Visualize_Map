#!/bin/bash

# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行后端服务
python app.py
