#!/bin/bash

# 啟動事件驅動系統

cd "$(dirname "$0")"

# 檢查是否已經運行
if [ -f pids/event-driven.pid ]; then
    PID=$(cat pids/event-driven.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  系統已經在運行 (PID: $PID)"
        echo "使用 'stop_event_driven.sh' 來停止系統"
        exit 1
    else
        rm pids/event-driven.pid
    fi
fi

# 啟動系統
echo "🚀 啟動事件驅動系統..."
nohup python3 -u event_driven_system.py > logs/event-driven.log 2>&1 &
echo $! > pids/event-driven.pid

echo "✅ 系統已啟動 (PID: $!)"
echo "📊 日誌文件: logs/event-driven.log"
echo "🔍 查看狀態: tail -f logs/event-driven.log"
echo "⏹️  停止系統: ./stop_event_driven.sh"
