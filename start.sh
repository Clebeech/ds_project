#!/bin/bash
# 启动脚本 - 同时启动后端和前端

echo "启动832工程数据库应用系统..."
echo ""

# 检查后端是否已启动
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ 后端API已在运行 (http://localhost:5001)"
else
    echo "启动后端API..."
    python run.py &
    BACKEND_PID=$!
    echo "后端API已启动 (PID: $BACKEND_PID)"
    sleep 2
fi

echo ""
echo "启动前端服务器..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "系统已启动！"
echo "=========================================="
echo "前端页面: http://localhost:8000"
echo "后端API:  http://localhost:5001"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="

# 等待用户中断
wait

