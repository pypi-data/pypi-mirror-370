# PyPI 업로드 지침

## 1. API 토큰 설정

`.pypirc` 파일을 편집하여 실제 API 토큰을 입력하세요:

```bash
nano ~/.pypirc
```

다음 내용으로 수정:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_REAL_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_REAL_TESTPYPI_TOKEN_HERE
```

## 2. 테스트 PyPI 업로드

```bash
cd /Users/assistive_ai/Dev/sphero_bolt_plus
python3 -m twine upload --repository testpypi dist/*
```

## 3. 테스트 설치 확인

```bash
pip install --index-url https://test.pypi.org/simple/ sphero-bolt-plus
```

## 4. 실제 PyPI 업로드

테스트가 성공하면 실제 PyPI에 업로드:

```bash
python3 -m twine upload dist/*
```

## 5. 설치 확인

```bash
pip install sphero-bolt-plus
```

## 대안 방법 (환경 변수 사용)

```bash
# 테스트 PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TESTPYPI_TOKEN
python3 -m twine upload --repository testpypi dist/*

# 실제 PyPI
export TWINE_PASSWORD=pypi-YOUR_PYPI_TOKEN
python3 -m twine upload dist/*
```

## 업로드 후 확인사항

1. **PyPI 페이지 확인**: https://pypi.org/project/sphero-bolt-plus/
2. **테스트 설치**: `pip install sphero-bolt-plus`
3. **README 표시 확인**: PyPI 페이지에서 올바르게 렌더링되는지 확인
4. **의존성 확인**: 필요한 패키지들이 자동으로 설치되는지 확인

## 문제 해결

### 이름 충돌
만약 패키지 이름이 이미 존재한다면:
1. `pyproject.toml`에서 `name = "sphero-bolt-plus-v2"` 등으로 변경
2. 다시 빌드: `python3 -m build`
3. 업로드 재시도

### 업로드 실패
- API 토큰이 올바른지 확인
- 패키지 이름이 사용 가능한지 확인
- 네트워크 연결 상태 확인

## 성공 메시지 예시

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading sphero_bolt_plus-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.1/15.1 kB • 00:01 • ?
Uploading sphero_bolt_plus-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 23.4/23.4 kB • 00:01 • ?

View at:
https://pypi.org/project/sphero-bolt-plus/1.0.0/
```