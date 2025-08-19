#!/bin/bash

# FIS MCP Server 실행 스크립트
cd "$(dirname "$0")"

# 환경 변수 설정
export AWS_REGION=${AWS_REGION:-us-east-1}
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 가상환경 활성화 (있는 경우)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 서버 실행
echo "Starting FIS MCP Server..."
python index.py
