# PyPI API 토큰 가이드

## 문제점
현재 제공된 토큰 `85b213cb-7d30-4d32-a325-763e2f4f7c27`이 PyPI에서 인증되지 않고 있습니다.

## PyPI API 토큰 얻기

1. **PyPI 계정 로그인**: https://pypi.org/account/login/
2. **Account settings** 이동: https://pypi.org/manage/account/
3. **API tokens** 섹션으로 이동
4. **Add API token** 클릭
5. Token name 입력 (예: "sphero-bolt-plus-upload")
6. Scope 선택:
   - **Entire account** (전체 계정) 또는
   - **Specific project** (특정 프로젝트만)

## 올바른 토큰 형태

PyPI API 토큰은 다음과 같은 형태입니다:
```
pypi-AgEIcHlwaS5vcmcCJGFiY2RlZmdo-abcdefghijklmnopqrstuvwxyz1234567890
```

- 항상 `pypi-`로 시작
- 매우 긴 문자열 (보통 100+ 문자)
- 대소문자, 숫자, 하이픈 포함

## 토큰 설정 후 업로드 명령

올바른 토큰을 받으신 후:

```bash
cd /Users/assistive_ai/Dev/sphero_bolt_plus

# 환경 변수 사용
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_ACTUAL_LONG_TOKEN_HERE
python3 -m twine upload dist/*

# 또는 직접 명령어에 포함
python3 -m twine upload -u __token__ -p pypi-YOUR_ACTUAL_LONG_TOKEN_HERE dist/*
```

## 보안 주의사항

- API 토큰은 절대 공개하지 마세요
- 토큰은 계정 비밀번호와 동일한 권한을 가집니다
- 사용하지 않는 토큰은 삭제하세요
- 토큰이 노출되었다면 즉시 취소하고 새로 생성하세요

## 대안: 사용자명/비밀번호

API 토큰 대신 PyPI 계정 사용자명과 비밀번호도 사용 가능합니다:
```bash
python3 -m twine upload -u your_username -p your_password dist/*
```

하지만 보안상 API 토큰 사용을 강력히 권장합니다.