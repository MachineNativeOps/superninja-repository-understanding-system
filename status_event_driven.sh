#!/bin/bash

# 檢查事件驅動系統狀態

if [ -f pids/event-driven.pid ]; then
    PID=$(cat pids/event-driven.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🟢 系統運行中 (PID: $PID)"
        echo ""
        echo "📊 進程資訊:"
        ps -p $PID -o pid,ppid,cmd,etime,stat
        
        echo ""
        echo "📈 資源使用:"
        ps -p $PID -o pid,%cpu,%mem,vsz,rss
        
        echo ""
        echo "📝 最近的日誌:"
        tail -n 10 logs/event-driven.log 2>/dev/null || echo "無日誌檔案"
    else
        echo "🔴 系統未運行 (PID 檔案存在但進程不存在)"
        rm pids/event-driven.pid
    fi
else
    echo "🔴 系統未運行 (PID 檔案不存在)"
fi
