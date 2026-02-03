#!/bin/bash

# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 运行调度器
python scheduler.py
