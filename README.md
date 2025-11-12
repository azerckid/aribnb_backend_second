# Airbnb Clone Backend

Airbnb 클론 프로젝트의 Django 백엔드 애플리케이션입니다.

## 기술 스택

- Django 5.2.7
- Django REST Framework
- SQLite (개발 환경)
- Poetry (의존성 관리)

## 설치 및 실행

### 1. Poetry 설치

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 의존성 설치

```bash
poetry install
```

### 3. 가상 환경 활성화

```bash
poetry shell
```

### 4. 데이터베이스 마이그레이션

```bash
poetry run python manage.py migrate
```

### 5. 슈퍼유저 생성

```bash
poetry run python manage.py createsuperuser
```

### 6. 개발 서버 실행

```bash
poetry run python manage.py runserver
```

서버는 `http://127.0.0.1:8000/`에서 실행됩니다.

## 프로젝트 구조

- `config/`: Django 프로젝트 설정
- `rooms/`: 방 관련 앱
- `users/`: 사용자 관련 앱
- `experiences/`: 체험 관련 앱
- `categories/`: 카테고리 관련 앱
- `reviews/`: 리뷰 관련 앱
- `wishlists/`: 위시리스트 관련 앱
- `bookings/`: 예약 관련 앱
- `medias/`: 미디어 관련 앱
- `direct_messages/`: 직접 메시지 관련 앱
- `common/`: 공통 모델 및 유틸리티

## API 엔드포인트

API 엔드포인트는 추후 추가될 예정입니다.

## 라이선스

MIT

