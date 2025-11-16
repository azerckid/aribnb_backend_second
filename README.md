# Airbnb Clone Backend

Airbnb 클론 프로젝트의 Django REST Framework 백엔드 애플리케이션입니다.

## 기술 스택

- **Python 3.14+**
- **Django 5.2.7** - 웹 프레임워크
- **Django REST Framework 3.16.1** - REST API 구축
- **SQLite** - 개발 환경 데이터베이스
- **Poetry** - 의존성 관리
- **Pillow** - 이미지 처리
- **PyJWT** - JWT 인증
- **django-environ** - 환경 변수 관리
- **pytest & pytest-django** - 테스트 프레임워크

## 기능

- ✅ 사용자 인증 (Session, Token, JWT)
- ✅ 방(Room) 관리 (CRUD, Amenities, Beds, Reviews, Photos, Bookings)
- ✅ 체험(Experience) 관리
- ✅ 카테고리(Category) 관리
- ✅ 리뷰(Review) 및 평점 계산
- ✅ 예약(Booking) 관리 (날짜 검증, 중복 방지)
- ✅ 위시리스트(Wishlist) 관리
- ✅ 미디어(Photo/Video) 업로드 및 관리
- ✅ 직접 메시지(Direct Messages)
- ✅ 페이지네이션
- ✅ 권한 관리 및 소유자 검증

## 설치 및 실행

### 1. Poetry 설치

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

또는 Homebrew (macOS):

```bash
brew install poetry
```

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd airbnb-backend
```

### 3. 의존성 설치

```bash
poetry install
```

### 4. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
SECRET_KEY='your-secret-key-here'
```

기존에 하드코딩된 SECRET_KEY를 `.env` 파일에서 로드합니다.

### 5. 가상 환경 활성화

```bash
poetry shell
```

### 6. 데이터베이스 마이그레이션

```bash
poetry run python manage.py migrate
```

### 7. 슈퍼유저 생성 (선택사항)

```bash
poetry run python manage.py createsuperuser
```

### 8. 개발 서버 실행

```bash
poetry run python manage.py runserver
```

서버는 `http://127.0.0.1:8000/`에서 실행됩니다.

## 테스트

### 테스트 실행

```bash
# 전체 테스트 실행
poetry run python manage.py test

# 또는 pytest 사용
poetry run pytest

# 특정 앱의 테스트만 실행
poetry run python manage.py test rooms
poetry run python manage.py test bookings
poetry run python manage.py test reviews
poetry run python manage.py test categories

# 자세한 출력
poetry run python manage.py test -v 2
```

### 테스트 결과 요약

현재 프로젝트에는 **49개의 테스트**가 작성되어 있으며, 모두 통과했습니다.

#### 테스트 커버리지

- **Rooms API**: 12개 테스트 ✅
  - 목록 조회 (인증/비인증)
  - 생성 (카테고리 검증, Amenities 연결, 트랜잭션)
  - 개별 조회
  - 수정/삭제 (소유자 권한 검증)
  - 에러 케이스 (카테고리 없음, Experience 카테고리 사용, 잘못된 Amenity, 404)

- **Amenities API**: 8개 테스트 ✅
  - CRUD 작업
  - 부분 업데이트
  - 에러 처리
  - 선택 필드 처리

- **Bookings API**: 11개 테스트 ✅
  - 예약 생성 (날짜 검증)
  - 날짜 검증 (과거 날짜, check_out <= check_in)
  - 중복 예약 방지
  - 목록 조회 (페이지네이션)
  - 월별 조회 (year, month 파라미터)
  - 파라미터 검증

- **Reviews API**: 12개 테스트 ✅
  - 리뷰 생성 (평점 검증)
  - 평점 검증 (1-5 범위)
  - 필수 필드 검증
  - 목록 조회 (페이지네이션)
  - 평점 계산 (평균 계산, 리뷰 없을 때 0)
  - 인증 검증
  - 동일 사용자 다중 리뷰 작성

- **Categories API**: 6개 테스트 ✅
  - CRUD 작업
  - 페이지네이션
  - 404 에러 처리

**총 49개 테스트, 모두 통과 (4.9초 소요)**

## 프로젝트 구조

```
airbnb-backend/
├── config/              # Django 프로젝트 설정
│   ├── settings.py      # 프로젝트 설정
│   ├── urls.py          # 메인 URL 설정
│   └── authentication.py # JWT 인증 설정
├── common/              # 공통 모델 및 유틸리티
├── users/               # 사용자 관련 앱
│   ├── models.py        # User 모델 (AbstractUser 확장)
│   ├── views.py         # 인증, 프로필 관리
│   ├── serializers.py   # User 시리얼라이저
│   └── urls.py          # User API 엔드포인트
├── rooms/               # 방 관련 앱
│   ├── models.py        # Room, Amenity, Bed 모델
│   ├── views.py         # Room, Amenity, Bed, Review, Photo, Booking 뷰
│   ├── serializers.py   # Room 시리얼라이저
│   ├── urls.py          # Room API 엔드포인트
│   └── tests.py         # Room & Amenity 테스트
├── experiences/         # 체험 관련 앱
├── categories/          # 카테고리 관련 앱
│   ├── models.py        # Category 모델
│   ├── views.py         # CategoryViewSet
│   ├── serializers.py   # Category 시리얼라이저
│   ├── urls.py          # Category API 엔드포인트
│   └── tests.py         # Category 테스트
├── reviews/             # 리뷰 관련 앱
│   ├── models.py        # Review 모델
│   ├── serializers.py   # Review 시리얼라이저
│   └── tests.py         # Review 테스트
├── bookings/            # 예약 관련 앱
│   ├── models.py        # Booking 모델
│   ├── serializers.py   # Booking 시리얼라이저
│   └── tests.py         # Booking 테스트
├── wishlists/           # 위시리스트 관련 앱
├── medias/              # 미디어 관련 앱
├── direct_messages/     # 직접 메시지 관련 앱
├── manage.py            # Django 관리 스크립트
├── pyproject.toml       # Poetry 의존성 설정
├── .env                 # 환경 변수 (gitignore)
└── README.md            # 프로젝트 문서
```

## API 엔드포인트

### 인증 (Authentication)

#### Session 기반 인증
- `POST /api/v1/users/log-in` - 로그인
- `POST /api/v1/users/log-out` - 로그아웃

#### Token 기반 인증
- `POST /api/v1/users/token-login` - 토큰 발급

#### JWT 기반 인증
- `POST /api/v1/users/jwt-login` - JWT 토큰 발급

### 사용자 (Users)

- `GET /api/v1/users/` - 사용자 목록
- `GET /api/v1/users/me` - 현재 사용자 정보
- `PUT /api/v1/users/me` - 현재 사용자 정보 수정
- `POST /api/v1/users/change-password` - 비밀번호 변경
- `GET /api/v1/users/@<username>` - 공개 사용자 프로필

### 카테고리 (Categories)

- `GET /api/v1/categories/` - 카테고리 목록 (페이지네이션)
- `POST /api/v1/categories/` - 카테고리 생성
- `GET /api/v1/categories/<pk>` - 카테고리 상세
- `PUT /api/v1/categories/<pk>` - 카테고리 수정
- `DELETE /api/v1/categories/<pk>` - 카테고리 삭제

### 방 (Rooms)

- `GET /api/v1/rooms/` - 방 목록 (인증 불필요)
- `POST /api/v1/rooms/` - 방 생성 (인증 필요)
- `GET /api/v1/rooms/<pk>` - 방 상세
- `PUT /api/v1/rooms/<pk>` - 방 수정 (소유자만)
- `DELETE /api/v1/rooms/<pk>` - 방 삭제 (소유자만)

### 편의시설 (Amenities)

- `GET /api/v1/rooms/amenities/` - 편의시설 목록
- `POST /api/v1/rooms/amenities/` - 편의시설 생성
- `GET /api/v1/rooms/amenities/<pk>` - 편의시설 상세
- `PUT /api/v1/rooms/amenities/<pk>` - 편의시설 수정
- `DELETE /api/v1/rooms/amenities/<pk>` - 편의시설 삭제

### 리뷰 (Reviews)

- `GET /api/v1/rooms/<pk>/reviews` - 방 리뷰 목록 (페이지네이션)
- `POST /api/v1/rooms/<pk>/reviews` - 방 리뷰 생성
- `GET /api/v1/experiences/<pk>/reviews` - 체험 리뷰 목록

### 예약 (Bookings)

- `GET /api/v1/rooms/<pk>/bookings?year=2024&month=12&page=1` - 방 예약 목록 (월별 조회)
- `POST /api/v1/rooms/<pk>/bookings` - 방 예약 생성
  - 날짜 검증 (과거 날짜 불가, check_out > check_in)
  - 중복 예약 방지
- `GET /api/v1/rooms/<pk>/beds/<bed_pk>/bookings` - 침대별 예약 목록
- `POST /api/v1/rooms/<pk>/beds/<bed_pk>/bookings` - 침대 예약 생성

### 체험 (Experiences)

- `GET /api/v1/experiences/` - 체험 목록
- `POST /api/v1/experiences/` - 체험 생성
- `GET /api/v1/experiences/<pk>` - 체험 상세
- `PUT /api/v1/experiences/<pk>` - 체험 수정
- `DELETE /api/v1/experiences/<pk>` - 체험 삭제
- `POST /api/v1/experiences/<pk>/bookings` - 체험 예약 생성

### 편의시설/특전 (Perks)

- `GET /api/v1/experiences/perks/` - 특전 목록
- `POST /api/v1/experiences/perks/` - 특전 생성
- `GET /api/v1/experiences/perks/<pk>` - 특전 상세
- `PUT /api/v1/experiences/perks/<pk>` - 특전 수정
- `DELETE /api/v1/experiences/perks/<pk>` - 특전 삭제

### 위시리스트 (Wishlists)

- `GET /api/v1/wishlists/` - 위시리스트 목록
- `POST /api/v1/wishlists/` - 위시리스트 생성
- `GET /api/v1/wishlists/<pk>` - 위시리스트 상세
- `PUT /api/v1/wishlists/<pk>` - 위시리스트 수정
- `DELETE /api/v1/wishlists/<pk>` - 위시리스트 삭제
- `PUT /api/v1/wishlists/<pk>/rooms/<room_pk>` - 방 추가/제거 (토글)
- `PUT /api/v1/wishlists/<pk>/experiences/<experience_pk>` - 체험 추가/제거 (토글)

### 미디어 (Medias)

- `DELETE /api/v1/medias/photos/<pk>` - 사진 삭제
- `POST /api/v1/rooms/<pk>/photos` - 방 사진 업로드

## 인증 방법

### 1. Session 인증

```bash
# 로그인
curl -X POST http://localhost:8000/api/v1/users/log-in \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}' \
  -c cookies.txt

# 인증된 요청 (쿠키 사용)
curl -X GET http://localhost:8000/api/v1/users/me \
  -b cookies.txt
```

### 2. Token 인증

```bash
# 토큰 발급
curl -X POST http://localhost:8000/api/v1/users/token-login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# 인증된 요청 (토큰 사용)
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Token <your-token>"
```

### 3. JWT 인증

```bash
# JWT 토큰 발급
curl -X POST http://localhost:8000/api/v1/users/jwt-login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# 인증된 요청 (JWT 토큰 사용)
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <your-jwt-token>"
```

## 주요 기능 상세

### 권한 관리

- **IsAuthenticated**: 대부분의 API 엔드포인트는 인증 필요
- **IsAuthenticatedOrReadOnly**: 읽기는 인증 불필요, 쓰기는 인증 필요 (Rooms, Reviews, Bookings 등)
- **소유자 검증**: Room, Experience 수정/삭제는 소유자만 가능

### 평점 계산

Room과 Experience 모델은 `rating()` 메서드를 통해 평균 평점을 계산합니다:

```python
def rating(self):
    count = self.reviews.count()
    if count == 0:
        return 0
    total_rating = sum(review.rating for review in self.reviews.all())
    return round(total_rating / count, 2)
```

### 페이지네이션

- **기본 페이지 크기**: 3 (PAGE_SIZE 설정)
- **API**: `GET /api/v1/categories/?page=1`
- **Bookings**: 월별 조회 지원 (`?year=2024&month=12&page=1`)

### 날짜 검증 (Bookings)

- 과거 날짜 예약 불가
- `check_out`은 `check_in`보다 이후여야 함
- 중복 예약 방지 (Room 레벨, Bed 레벨)
- Bed 예약 시 capacity 검증

### 트랜잭션 처리

Room 생성 시 Amenities 연결은 트랜잭션으로 처리되어 원자성을 보장합니다.

## 개발 가이드

### 코드 스타일

- **포맷터**: Black
- **린터**: Flake8

```bash
# 코드 포맷팅
poetry run black .

# 린트 검사
poetry run flake8 .
```

### 환경 변수

`.env` 파일을 생성하여 다음 변수를 설정하세요:

```env
SECRET_KEY='your-secret-key-here'
```

### 데이터베이스

개발 환경에서는 SQLite를 사용합니다. 프로덕션 환경에서는 PostgreSQL 사용을 권장합니다.

## 라이선스

MIT
