#!/bin/bash

echo "🔍 프로젝트 초기 설정 체크"
echo "======================================"

# 1. 가상환경 확인
if [ -d "venv" ]; then
    echo "✅ venv 존재"
else
    echo "❌ venv 없음"
fi

# 2. .gitignore 확인
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore 존재"
else
    echo "❌ .gitignore 없음"
fi

# 3. .env 확인
if [ -f ".env" ]; then
    echo "✅ .env 존재"
else
    echo "❌ .env 없음 (생성 필요!)"
fi

# 4. requirements.txt 확인
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 존재"
else
    echo "❌ requirements.txt 없음"
fi

# 5. 폴더 구조 확인
for dir in src scripts data output; do
    if [ -d "$dir" ]; then
        echo "✅ $dir 폴더 존재"
    else
        echo "❌ $dir 폴더 없음"
    fi
done

# 6. Git 확인
if [ -d ".git" ]; then
    echo "✅ Git 초기화됨"
else
    echo "❌ Git 초기화 안 됨"
fi

echo "======================================"
echo "✅ 설정 완료!"
