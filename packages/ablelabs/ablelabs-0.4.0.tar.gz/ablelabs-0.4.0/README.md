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
