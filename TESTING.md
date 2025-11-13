# API 테스트 가이드

## 1. curl 사용 (기본)

### 서버 실행
```bash
poetry run python manage.py runserver
```

### 테스트 스크립트 실행
```bash
./test_api.sh
```

### 개별 명령어

#### GET - 목록 조회
```bash
curl -X GET http://localhost:8000/api/v1/categories/ \
  -H "Content-Type: application/json"
```

#### POST - 생성
```bash
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Beach Houses", "kind": "rooms"}'
```

#### GET - 개별 조회
```bash
curl -X GET http://localhost:8000/api/v1/categories/1 \
  -H "Content-Type: application/json"
```

#### PUT - 수정
```bash
curl -X PUT http://localhost:8000/api/v1/categories/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

#### DELETE - 삭제
```bash
curl -X DELETE http://localhost:8000/api/v1/categories/1 \
  -H "Content-Type: application/json" -v
```

---

## 2. httpie 사용 (더 간단하고 읽기 쉬움)

### 설치
```bash
# macOS
brew install httpie

# 또는 pip
pip install httpie
```

### 사용법

#### GET - 목록 조회
```bash
http GET http://localhost:8000/api/v1/categories/
```

#### POST - 생성
```bash
http POST http://localhost:8000/api/v1/categories/ \
  name="Beach Houses" kind="rooms"
```

#### GET - 개별 조회
```bash
http GET http://localhost:8000/api/v1/categories/1
```

#### PUT - 수정
```bash
http PUT http://localhost:8000/api/v1/categories/1 \
  name="Updated Name"
```

#### DELETE - 삭제
```bash
http DELETE http://localhost:8000/api/v1/categories/1
```

---

## 3. Django 테스트 케이스 (자동화)

### 테스트 파일 생성
`categories/tests.py`에 테스트 케이스 작성

### 실행
```bash
poetry run python manage.py test categories
```

---

## 4. Postman / Insomnia (GUI 도구)

### Postman
- 다운로드: https://www.postman.com/downloads/
- Collection 생성하여 API 엔드포인트 관리

### Insomnia
- 다운로드: https://insomnia.rest/download
- 더 가벼운 대안

---

## 5. Python requests 라이브러리

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/categories"

# GET - 목록 조회
response = requests.get(f"{BASE_URL}/")
print(response.json())

# POST - 생성
response = requests.post(
    f"{BASE_URL}/",
    json={"name": "Beach Houses", "kind": "rooms"}
)
print(response.json())

# GET - 개별 조회
response = requests.get(f"{BASE_URL}/1")
print(response.json())

# PUT - 수정
response = requests.put(
    f"{BASE_URL}/1",
    json={"name": "Updated Name"}
)
print(response.json())

# DELETE - 삭제
response = requests.delete(f"{BASE_URL}/1")
print(response.status_code)  # 204
```

---

## 추천 방법

1. **개발 중 빠른 테스트**: `httpie` (가장 간단)
2. **자동화된 테스트**: Django 테스트 케이스
3. **API 문서화/공유**: Postman Collection
4. **스크립트 자동화**: `test_api.sh` 사용

