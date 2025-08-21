# ABLE Labs API

ABLE Labs 로봇 제어 API 패키지입니다.

## 설치

```bash
pip install ablelabs
```

## 사용법

```python
from ablelabs.neon_v2.notable import Notable

# 로봇 API 초기화 및 사용
base_url = "http://localhost:7777"
notable = Notable(base_url)
```

## 요구사항

- Python 3.10 이상

## 개발자 가이드

### 배포

PyPI에 패키지를 배포하려면 `deploy.py` 스크립트를 사용합니다.

#### 사전 준비

1. **가상환경 활성화**
   ```bash
   source .venv/bin/activate  # macOS/Linux
   # 또는
   .venv\Scripts\activate     # Windows
   ```

2. **PyPI 토큰 설정**
   ```bash
   # tokens.py 파일에 토큰 설정
   PYPI_TOKEN = "your-actual-pypi-token"
   ```

> **참고**: `deploy.py` 스크립트가 필요한 도구들(`twine`, `wheel`)을 자동으로 설치합니다.

#### 배포 실행

1. **버전 업데이트**
   ```bash
   # setup.py 파일에서 version 번호를 올려주세요
   # 예: "0.4.0" → "0.4.1"
   ```
   
   **버전 규칙**:
   - `MAJOR.MINOR.PATCH` 형식 사용
   - `MAJOR`: 호환되지 않는 API 변경
   - `MINOR`: 새로운 기능 추가 (하위 호환)
   - `PATCH`: 버그 수정 (하위 호환)

2. **배포 스크립트 실행**
   ```bash
   python deploy.py
   ```

스크립트는 다음 단계를 자동으로 수행합니다:
1. 환경 확인 (가상환경, Python 버전, 필요한 도구)
2. 이전 빌드 파일 정리
3. 패키지 빌드 (`setup.py sdist bdist_wheel`)
4. 패키지 검사 (`twine check`)
5. PyPI 업로드 (`twine upload --skip-existing`)
6. 빌드 파일 자동 정리

#### 수동 배포

자동화 스크립트 대신 수동으로 배포할 수도 있습니다:

```bash
# 빌드
python setup.py sdist bdist_wheel

# 검사
python -m twine check dist/*

# 업로드
python -m twine upload --skip-existing dist/*
```
