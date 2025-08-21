#!/bin/bash

# Sphero BOLT+ PyPI 업로드 스크립트
# 사용법: ./quick_upload.sh

echo "🚀 Sphero BOLT+ PyPI 업로드 시작"
echo "=================================="

# 현재 디렉토리 확인
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ 오류: pyproject.toml 파일을 찾을 수 없습니다."
    echo "   프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# API 토큰 확인
if [[ -z "$TWINE_PASSWORD" ]]; then
    echo "⚠️  TWINE_PASSWORD 환경변수가 설정되지 않았습니다."
    echo "   다음 중 하나를 선택하세요:"
    echo "   1. export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE"
    echo "   2. ~/.pypirc 파일에 토큰 설정"
    echo ""
    read -p "계속 진행하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. 기존 빌드 정리
echo "🧹 기존 빌드 파일 정리 중..."
rm -rf build/ dist/ *.egg-info/

# 2. 새로운 빌드 생성
echo "🔨 패키지 빌드 중..."
python3 -m build

if [[ $? -ne 0 ]]; then
    echo "❌ 빌드 실패"
    exit 1
fi

# 3. 패키지 검증
echo "✅ 패키지 검증 중..."
python3 -m twine check dist/*

if [[ $? -ne 0 ]]; then
    echo "❌ 패키지 검증 실패"
    exit 1
fi

# 4. 테스트 PyPI 업로드 여부 확인
echo ""
read -p "🧪 테스트 PyPI에 먼저 업로드하시겠습니까? (권장) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 테스트 PyPI 업로드 중..."
    python3 -m twine upload --repository testpypi dist/*
    
    if [[ $? -eq 0 ]]; then
        echo "✅ 테스트 PyPI 업로드 성공!"
        echo "🔗 확인: https://test.pypi.org/project/sphero-bolt-plus/"
        echo ""
        echo "테스트 설치 명령어:"
        echo "pip install --index-url https://test.pypi.org/simple/ sphero-bolt-plus"
        echo ""
        read -p "실제 PyPI에 업로드하시겠습니까? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "업로드 중단됨"
            exit 0
        fi
    else
        echo "❌ 테스트 PyPI 업로드 실패"
        exit 1
    fi
fi

# 5. 실제 PyPI 업로드
echo "📤 PyPI 업로드 중..."
python3 -m twine upload dist/*

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 성공! sphero-bolt-plus가 PyPI에 업로드되었습니다!"
    echo "🔗 확인: https://pypi.org/project/sphero-bolt-plus/"
    echo ""
    echo "설치 명령어:"
    echo "pip install sphero-bolt-plus"
    echo ""
    echo "사용 예시:"
    echo "python3 -c 'from sphero_bolt_plus import SpheroScanner; print(\"설치 성공!\")'"
else
    echo "❌ PyPI 업로드 실패"
    exit 1
fi

echo ""
echo "🚀 업로드 완료!"