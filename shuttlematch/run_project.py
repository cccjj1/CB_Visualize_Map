#!/usr/bin/env python3
"""
🚌 EvoRide - Campus Shuttle Optimization System
完整项目启动脚本 - 一键启动所有服务
"""

import subprocess
import os
import sys
import time
import platform
from pathlib import Path

class ProjectRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.processes = []
        self.os_type = platform.system()
        
    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔════════════════════════════════════════════════════════════╗
║  🚌 EvoRide - Campus Shuttle Optimization System 🚌        ║
║     Powered by Genetic Algorithm & Route Optimization      ║
╚════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_python_packages(self):
        """检查Python依赖是否安装"""
        print("📦 检查 Python 依赖...")
        required_packages = [
            'flask', 'flask_cors', 'pandas', 'numpy', 
            'schedule', 'python-dotenv', 'requests'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - 缺失")
                missing.append(package)
        
        if missing:
            print(f"\n⚠️  缺少依赖: {', '.join(missing)}")
            print("正在安装缺失的依赖...\n")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install'] + missing,
                cwd=self.backend_dir
            )
            print()
        
        return len(missing) == 0
    
    def check_node_packages(self):
        """检查Node.js和npm"""
        print("📦 检查 Node.js 环境...")
        
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"  ✅ Node.js {node_version}")
            else:
                print("  ⚠️  Node.js 未在 PATH 中")
                return False
        except:
            print("  ⚠️  Node.js 未安装")
            return False
        
        # Check npm
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"  ✅ npm {npm_version}")
            else:
                print("  ⚠️  npm 未在 PATH 中")
                return False
        except:
            print("  ⚠️  npm 未安装")
            return False
        
        return True
    
    def check_frontend_deps(self):
        """检查前端依赖是否安装"""
        print("📦 检查前端依赖...")
        node_modules = self.frontend_dir / 'node_modules'
        
        if node_modules.exists():
            print(f"  ✅ node_modules 已安装")
            return True
        else:
            print(f"  ⚠️  node_modules 不存在，正在安装...")
            try:
                subprocess.run(
                    ['npm', 'install'],
                    cwd=self.frontend_dir,
                    timeout=120
                )
                print("  ✅ 前端依赖安装完成")
                return True
            except Exception as e:
                print(f"  ❌ 前端依赖安装失败: {e}")
                return False
    
    def start_backend(self):
        """启动后端Flask服务"""
        print("\n" + "="*60)
        print("🔧 启动后端服务 (Flask API)...")
        print("="*60)
        
        try:
            cmd = [sys.executable, 'app.py']
            process = subprocess.Popen(
                cmd,
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.processes.append(('backend', process))
            print(f"✅ 后端服务启动中 (PID: {process.pid})")
            print(f"📍 地址: http://127.0.0.1:5001")
            return True
        except Exception as e:
            print(f"❌ 后端服务启动失败: {e}")
            return False
    
    def start_scheduler(self):
        """启动调度器服务"""
        print("\n" + "="*60)
        print("⏱️  启动调度器服务 (Scheduler)...")
        print("="*60)
        
        try:
            cmd = [sys.executable, 'scheduler.py']
            process = subprocess.Popen(
                cmd,
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.processes.append(('scheduler', process))
            print(f"✅ 调度器启动中 (PID: {process.pid})")
            print(f"📍 模式: TEST (每 30 秒运行一次匹配算法)")
            return True
        except Exception as e:
            print(f"❌ 调度器启动失败: {e}")
            return False
    
    def start_frontend(self):
        """启动前端开发服务器"""
        print("\n" + "="*60)
        print("🎨 启动前端服务 (Vite Dev Server)...")
        print("="*60)
        
        try:
            if self.os_type == 'Windows':
                # Windows 使用特殊的 npm 启动方式
                cmd = f'cd {self.frontend_dir} && set NODE_ENV=development && npm run dev'
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            else:
                cmd = ['npm', 'run', 'dev']
                process = subprocess.Popen(
                    cmd,
                    cwd=self.frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            
            self.processes.append(('frontend', process))
            print(f"✅ 前端服务启动中 (PID: {process.pid})")
            print(f"📍 地址: http://localhost:5173")
            return True
        except Exception as e:
            print(f"❌ 前端服务启动失败: {e}")
            return False
    
    def print_startup_summary(self):
        """打印启动总结"""
        print("\n" + "="*60)
        print("🚀 所有服务启动完成！")
        print("="*60)
        print("\n📋 服务状态:")
        print("  ✅ 后端 API       → http://127.0.0.1:5001")
        print("  ✅ 前端应用       → http://localhost:5173")
        print("  ✅ 调度器         → 后台运行中")
        print("\n📚 关键端点:")
        print("  POST   /match              - 提交乘客请求")
        print("  GET    /route_time         - 查询路线时间")
        print("  GET    /result/<uid>       - 获取匹配结果")
        print("\n💡 提示:")
        print("  - 在浏览器打开 http://localhost:5173 使用应用")
        print("  - 按 Ctrl+C 停止所有服务")
        print("  - 查看控制台输出了解详细信息")
        print("\n" + "="*60)
    
    def log_output(self, process_name, process):
        """记录进程输出"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"[{process_name.upper()}] {line.rstrip()}")
        except:
            pass
    
    def monitor_processes(self):
        """监控所有进程"""
        print("\n⏳ 所有服务运行中... (按 Ctrl+C 停止)")
        print("-" * 60)
        
        try:
            while True:
                time.sleep(1)
                
                # 检查进程是否仍在运行
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"\n⚠️  {name} 进程已终止 (返回码: {process.poll()})")
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("🛑 收到停止信号，正在关闭所有服务...")
            print("="*60)
            self.stop_all()
    
    def stop_all(self):
        """停止所有进程"""
        for name, process in self.processes:
            try:
                print(f"  停止 {name}...", end='')
                process.terminate()
                process.wait(timeout=5)
                print(" ✅")
            except subprocess.TimeoutExpired:
                print(" (强制终止)", end='')
                process.kill()
                print(" ✅")
            except Exception as e:
                print(f" ❌ 错误: {e}")
        
        print("\n✅ 所有服务已关闭")
        sys.exit(0)
    
    def run(self):
        """主运行函数"""
        self.print_banner()
        
        # 检查依赖
        print("🔍 检查项目依赖...\n")
        
        if not self.check_python_packages():
            print("❌ Python 依赖检查失败")
            return False
        
        print()
        
        if not self.check_node_packages():
            print("⚠️  Node.js 不可用，跳过前端启动")
            skip_frontend = True
        else:
            skip_frontend = False
            if not self.check_frontend_deps():
                print("⚠️  前端依赖安装失败，跳过前端启动")
                skip_frontend = True
        
        # 启动服务
        print("\n" + "="*60)
        print("🚀 启动项目服务...")
        print("="*60)
        
        # 先启动后端和调度器
        time.sleep(1)
        if not self.start_backend():
            print("❌ 无法启动后端，程序退出")
            return False
        
        time.sleep(2)
        
        if not self.start_scheduler():
            print("⚠️  调度器启动失败，继续启动前端...")
        
        time.sleep(1)
        
        # 启动前端
        if not skip_frontend:
            if not self.start_frontend():
                print("⚠️  前端启动失败，其他服务仍在运行")
        
        # 打印启动总结
        time.sleep(2)
        self.print_startup_summary()
        
        # 监控进程
        self.monitor_processes()


def main():
    """主入口"""
    runner = ProjectRunner()
    
    try:
        runner.run()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        runner.stop_all()
        sys.exit(1)


if __name__ == '__main__':
    main()
