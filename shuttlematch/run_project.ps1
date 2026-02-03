# 🚌 EvoRide - Campus Shuttle Optimization System
# 完整项目启动脚本 (PowerShell版本)

$ErrorActionPreference = "Continue"

# 获取项目根目录
$projectRoot = Split-Path -Parent $PSCommandPath
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

# 颜色输出函数
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# 打印启动横幅
function Print-Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  🚌 EvoRide - Campus Shuttle Optimization System 🚌        ║" -ForegroundColor Magenta
    Write-Host "║     Powered by Genetic Algorithm & Route Optimization      ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

# 检查Python依赖
function Check-PythonPackages {
    Write-Info "检查 Python 依赖..."
    
    $packages = @('flask', 'flask_cors', 'pandas', 'numpy', 'schedule', 'python-dotenv', 'requests')
    $missing = @()
    
    foreach ($package in $packages) {
        try {
            $output = & python -c "import $($package.Replace('-', '_'))" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$package"
            } else {
                Write-Error-Custom "$package - 缺失"
                $missing += $package
            }
        } catch {
            Write-Error-Custom "$package - 缺失"
            $missing += $package
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Warning-Custom "缺少依赖: $($missing -join ', ')"
        Write-Info "正在安装缺失的依赖..."
        & python -m pip install @missing
    }
    
    return $missing.Count -eq 0
}

# 检查Node.js和npm
function Check-NodeEnvironment {
    Write-Info "检查 Node.js 环境..."
    
    $nodeExists = $false
    $npmExists = $false
    
    try {
        $nodeVersion = & node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js $nodeVersion"
            $nodeExists = $true
        }
    } catch {
        Write-Warning-Custom "Node.js 未安装或不在 PATH 中"
    }
    
    try {
        $npmVersion = & npm --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "npm $npmVersion"
            $npmExists = $true
        }
    } catch {
        Write-Warning-Custom "npm 未安装或不在 PATH 中"
    }
    
    return $nodeExists -and $npmExists
}

# 检查前端依赖
function Check-FrontendDeps {
    Write-Info "检查前端依赖..."
    
    $nodeModulesPath = Join-Path $frontendDir "node_modules"
    
    if (Test-Path $nodeModulesPath) {
        Write-Success "node_modules 已安装"
        return $true
    } else {
        Write-Warning-Custom "node_modules 不存在，正在安装..."
        Push-Location $frontendDir
        try {
            & npm install
            if ($LASTEXITCODE -eq 0) {
                Write-Success "前端依赖安装完成"
                return $true
            } else {
                Write-Error-Custom "前端依赖安装失败"
                return $false
            }
        } finally {
            Pop-Location
        }
    }
}

# 启动后端
function Start-Backend {
    Write-Host ""
    Write-Host "═" * 60 -ForegroundColor Cyan
    Write-Info "启动后端服务 (Flask API)..."
    Write-Host "═" * 60 -ForegroundColor Cyan
    
    try {
        Push-Location $backendDir
        Write-Success "后端服务启动中..."
        Write-Info "地址: http://127.0.0.1:5001"
        
        # 启动后端作为后台任务
        Start-Process -FilePath "python" -ArgumentList "app.py" -NoNewWindow
        
        Pop-Location
        return $true
    } catch {
        Write-Error-Custom "后端服务启动失败: $_"
        Pop-Location
        return $false
    }
}

# 启动调度器
function Start-Scheduler {
    Write-Host ""
    Write-Host "═" * 60 -ForegroundColor Cyan
    Write-Info "启动调度器服务 (Scheduler)..."
    Write-Host "═" * 60 -ForegroundColor Cyan
    
    try {
        Push-Location $backendDir
        Write-Success "调度器启动中..."
        Write-Info "模式: TEST (每 30 秒运行一次匹配算法)"
        
        # 启动调度器作为后台任务
        Start-Process -FilePath "python" -ArgumentList "scheduler.py" -NoNewWindow
        
        Pop-Location
        return $true
    } catch {
        Write-Error-Custom "调度器启动失败: $_"
        Pop-Location
        return $false
    }
}

# 启动前端
function Start-Frontend {
    Write-Host ""
    Write-Host "═" * 60 -ForegroundColor Cyan
    Write-Info "启动前端服务 (Vite Dev Server)..."
    Write-Host "═" * 60 -ForegroundColor Cyan
    
    try {
        Push-Location $frontendDir
        Write-Success "前端服务启动中..."
        Write-Info "地址: http://localhost:5173"
        
        # 启动前端作为新窗口
        Start-Process -FilePath "npm" -ArgumentList "run", "dev"
        
        Pop-Location
        return $true
    } catch {
        Write-Error-Custom "前端服务启动失败: $_"
        Pop-Location
        return $false
    }
}

# 打印启动总结
function Print-Summary {
    Write-Host ""
    Write-Host "═" * 60 -ForegroundColor Green
    Write-Host "🚀 所有服务启动完成！" -ForegroundColor Green
    Write-Host "═" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 服务状态:" -ForegroundColor Yellow
    Write-Host "  ✅ 后端 API       → http://127.0.0.1:5001" -ForegroundColor Green
    Write-Host "  ✅ 前端应用       → http://localhost:5173" -ForegroundColor Green
    Write-Host "  ✅ 调度器         → 后台运行中" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 关键端点:" -ForegroundColor Yellow
    Write-Host "  POST   /match              - 提交乘客请求" -ForegroundColor Cyan
    Write-Host "  GET    /route_time         - 查询路线时间" -ForegroundColor Cyan
    Write-Host "  GET    /result/<uid>       - 获取匹配结果" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 提示:" -ForegroundColor Yellow
    Write-Host "  - 在浏览器打开 http://localhost:5173 使用应用" -ForegroundColor Cyan
    Write-Host "  - 查看各个终端窗口了解详细信息" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "═" * 60 -ForegroundColor Green
}

# 主函数
function Main {
    Print-Banner
    
    Write-Host "🔍 检查项目依赖..." -ForegroundColor Yellow
    Write-Host ""
    
    # 检查Python依赖
    $pythonOk = Check-PythonPackages
    
    Write-Host ""
    
    # 检查Node.js
    $nodeOk = Check-NodeEnvironment
    $skipFrontend = $false
    
    if (-not $nodeOk) {
        Write-Warning-Custom "Node.js 不可用，将跳过前端启动"
        $skipFrontend = $true
    } else {
        if (-not (Check-FrontendDeps)) {
            Write-Warning-Custom "前端依赖安装失败，将跳过前端启动"
            $skipFrontend = $true
        }
    }
    
    # 启动服务
    Write-Host ""
    Write-Host "═" * 60 -ForegroundColor Yellow
    Write-Host "🚀 启动项目服务..." -ForegroundColor Yellow
    Write-Host "═" * 60 -ForegroundColor Yellow
    
    # 启动后端
    Start-Sleep -Seconds 1
    if (-not (Start-Backend)) {
        Write-Error-Custom "无法启动后端，程序退出"
        return
    }
    
    Start-Sleep -Seconds 2
    
    # 启动调度器
    if (-not (Start-Scheduler)) {
        Write-Warning-Custom "调度器启动失败，继续启动前端..."
    }
    
    Start-Sleep -Seconds 1
    
    # 启动前端
    if (-not $skipFrontend) {
        if (-not (Start-Frontend)) {
            Write-Warning-Custom "前端启动失败，其他服务仍在运行"
        }
    }
    
    # 打印总结
    Start-Sleep -Seconds 2
    Print-Summary
    
    Write-Host "⏳ 所有服务运行中..." -ForegroundColor Cyan
    Write-Host "按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 运行
Main
