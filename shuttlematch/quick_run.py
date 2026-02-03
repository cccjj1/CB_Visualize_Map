#!/usr/bin/env python3
"""
🚌 EvoRide - 简化快速启动脚本
使用方式: python quick_run.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(cmd, name, cwd=None, shell=False):
    """运行命令并返回进程"""
    try:
        print(f"⏳ 启动 {name}...")
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        print(f"✅ {name} 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ {name} 启动失败: {e}")
        return None

def main():
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    frontend_dir = project_root / 'frontend'
    
    print("""
╔════════════════════════════════════════════╗
║  🚌 EvoRide 快速启动脚本                    ║
╚════════════════════════════════════════════╝
    """)
    
    processes = []
    
    # 1. 启动后端
    print("\n[1/3] 启动后端 API...")
    backend_process = run_command(
        [sys.executable, 'app.py'],
        '后端服务',
        cwd=backend_dir
    )
    if backend_process:
        processes.append(backend_process)
    
    time.sleep(2)
    
    # 2. 启动调度器
    print("\n[2/3] 启动调度器...")
    scheduler_process = run_command(
        [sys.executable, 'scheduler.py'],
        '调度器',
        cwd=backend_dir
    )
    if scheduler_process:
        processes.append(scheduler_process)
    
    time.sleep(1)
    
    # 3. 启动前端
    print("\n[3/3] 启动前端应用...")
    try:
        frontend_process = run_command(
            [sys.executable, '-m', 'http.server', '5173'],
            '简易Web服务器',
            cwd=frontend_dir
        )
        if frontend_process:
            processes.append(frontend_process)
    except:
        # 如果npm可用，则使用npm
        try:
            import platform
            if platform.system() == 'Windows':
                frontend_process = subprocess.Popen(
                    'npm run dev',
                    shell=True,
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE
                )
            else:
                frontend_process = subprocess.Popen(
                    ['npm', 'run', 'dev'],
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE
                )
            if frontend_process:
                processes.append(frontend_process)
                print(f"✅ 前端服务已启动")
        except:
            print("⚠️  前端启动失败，但后端服务仍在运行")
    
    # 打印启动信息
    print("""
╔════════════════════════════════════════════╗
║  🚀 所有服务启动完成！                      ║
╚════════════════════════════════════════════╝

📋 服务地址:
  🔧 后端 API   → http://127.0.0.1:5001
  🎨 前端应用   → http://localhost:5173
  ⏱️  调度器     → 后台运行中

💡 使用提示:
  1. 在浏览器打开 http://localhost:5173
  2. 提交乘客请求后，调度器会自动匹配
  3. 按 Ctrl+C 停止所有服务

═══════════════════════════════════════════════
⏳ 所有服务运行中，按 Ctrl+C 停止...
═══════════════════════════════════════════════
    """)
    
    try:
        # 保持进程运行
        for process in processes:
            if process:
                process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号，正在关闭所有服务...")
        for process in processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=3)
                except:
                    process.kill()
        print("✅ 所有服务已关闭")

if __name__ == '__main__':
    main()
