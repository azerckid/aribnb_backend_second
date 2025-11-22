# 프론트엔드 통합 가이드

이 문서는 프론트엔드 개발자가 백엔드 API를 사용하기 위한 정보를 제공합니다.

## 📡 API 베이스 URL

**프로덕션 (Render):**
```
https://airbnb-backend-yvup.onrender.com/api/v1
```

**로컬 개발 (개발 서버):**
```
http://localhost:8000/api/v1
```

## 🔐 인증 방법

백엔드는 다음과 같은 인증 방법을 지원합니다:

1. **Token Authentication** (추천)
   - 로그인 후 받은 토큰을 `Authorization: Token <token>` 헤더에 포함
   
2. **JWT Authentication**
   - JWT 토큰을 `Authorization: Bearer <jwt_token>` 헤더에 포함

3. **Session Authentication**
   - 쿠키 기반 인증 (브라우저 환경)

### 인증 예시

```javascript
// Token Authentication
fetch('https://airbnb-backend-yvup.onrender.com/api/v1/me/', {
  headers: {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json'
  }
})

// JWT Authentication
fetch('https://airbnb-backend-yvup.onrender.com/api/v1/me/', {
  headers: {
    'Authorization': 'Bearer your-jwt-token-here',
    'Content-Type': 'application/json'
  }
})
```

## 🌐 CORS 설정

현재 백엔드는 다음 도메인에서의 요청을 허용하도록 설정되어 있습니다:

**로컬 개발:**
- `http://localhost:5173` (Vite 기본 포트)
- `http://localhost:3000` (Next.js 기본 포트)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

**프로덕션:**
프론트엔드가 배포되면 Render 대시보드에서 다음 환경변수를 업데이트해야 합니다:
- `CORS_ALLOWED_ORIGINS`: 프론트엔드 도메인 (쉼표로 구분)
- `CSRF_TRUSTED_ORIGINS`: 프론트엔드 도메인 (쉼표로 구분)

예시:
```bash
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
CSRF_TRUSTED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
```

## 📋 주요 API 엔드포인트

### 인증 관련
- `POST /api/v1/users/` - 회원가입
- `POST /api/v1/users/login/` - 로그인
- `POST /api/v1/users/logout/` - 로그아웃
- `GET /api/v1/users/me/` - 내 정보 조회
- `PUT /api/v1/users/me/` - 내 정보 수정

### 방(Room) 관련
- `GET /api/v1/rooms/` - 방 목록 조회
- `GET /api/v1/rooms/<id>/` - 방 상세 조회
- `POST /api/v1/rooms/` - 방 생성 (인증 필요)
- `PUT /api/v1/rooms/<id>/` - 방 수정 (소유자만)
- `DELETE /api/v1/rooms/<id>/` - 방 삭제 (소유자만)
- `GET /api/v1/rooms/<id>/bookings/check?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&guests=1` - 예약 가능 여부 확인
- `POST /api/v1/rooms/<id>/bookings/` - 방 예약
- `GET /api/v1/rooms/<id>/bookings/status?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD` - 예약 상태 확인

### 예약(Booking) 관련
- `GET /api/v1/bookings/` - 내 예약 목록 (인증 필요)
- `GET /api/v1/bookings/<id>/` - 예약 상세 (인증 필요)
- `PUT /api/v1/bookings/<id>/` - 예약 수정 (본인만)
- `DELETE /api/v1/bookings/<id>/` - 예약 취소 (본인만)

### 체험(Experience) 관련
- `GET /api/v1/experiences/` - 체험 목록
- `GET /api/v1/experiences/<id>/` - 체험 상세
- `POST /api/v1/experiences/` - 체험 생성 (호스트만)

### 카테고리 관련
- `GET /api/v1/categories/` - 카테고리 목록

### 리뷰 관련
- `GET /api/v1/rooms/<id>/reviews/` - 방 리뷰 목록
- `POST /api/v1/rooms/<id>/reviews/` - 리뷰 작성 (인증 필요)

### 위시리스트 관련
- `GET /api/v1/wishlists/` - 위시리스트 목록 (인증 필요)
- `POST /api/v1/wishlists/` - 위시리스트 생성 (인증 필요)

자세한 API 문서는 `API_ENDPOINTS.md`를 참고하세요.

## ⚙️ 프론트엔드 환경변수 설정

프론트엔드에서 API URL을 환경변수로 관리하는 것을 권장합니다:

### `.env` (로컬 개발)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
# 또는
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### `.env.production` (프로덕션)
```env
VITE_API_BASE_URL=https://airbnb-backend-yvup.onrender.com/api/v1
# 또는
NEXT_PUBLIC_API_BASE_URL=https://airbnb-backend-yvup.onrender.com/api/v1
```

### 사용 예시 (Vite/React)
```javascript
// .env
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// API 호출
fetch(`${API_BASE_URL}/rooms/`)
```

### 사용 예시 (Next.js)
```javascript
// .env.local
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'

// API 호출
fetch(`${API_BASE_URL}/rooms/`)
```

## 📝 API 응답 형식

### 성공 응답
```json
{
  "id": 1,
  "name": "Room Name",
  ...
}
```

### 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

또는:
```json
{
  "field_name": ["에러 메시지"]
}
```

### 예약 가능 여부 확인 응답
```json
{
  "available": true,
  "message": "Booking is available for the specified dates and guests."
}
```

예약 불가 시:
```json
{
  "available": false,
  "reason": "INSUFFICIENT_BEDS",
  "message": "Not enough beds available for the requested number of guests.",
  "details": {
    "requested_guests": 3,
    "available_beds": 2
  }
}
```

## 🔒 보안 주의사항

1. **토큰 저장**: 
   - 브라우저의 `localStorage` 또는 `sessionStorage`에 저장 가능
   - 민감한 정보이므로 안전하게 관리

2. **HTTPS 사용**: 
   - 프로덕션에서는 반드시 HTTPS를 사용하세요
   - Render는 자동으로 HTTPS를 제공합니다

3. **CORS 설정**:
   - 프론트엔드 배포 후 백엔드의 `CORS_ALLOWED_ORIGINS` 환경변수를 업데이트해야 합니다

## 🐛 문제 해결

### CORS 오류 발생 시
1. 프론트엔드 도메인이 `CORS_ALLOWED_ORIGINS`에 포함되어 있는지 확인
2. Render 대시보드에서 환경변수 업데이트 후 재배포

### 401 Unauthorized 오류
- 토큰이 올바르게 전달되고 있는지 확인
- 토큰이 만료되었는지 확인 (새로 로그인 필요)

### 403 Forbidden 오류
- 해당 리소스에 대한 권한이 있는지 확인
- 소유자만 접근 가능한 경우 본인이 소유자인지 확인

### 400 Bad Request 오류
- 요청 본문의 데이터 형식이 올바른지 확인
- 필수 필드가 누락되지 않았는지 확인

## 📞 연락처

백엔드 관련 문제가 있으면 백엔드 개발자에게 연락하세요.

## 🔗 참고 문서

- [API 엔드포인트 전체 목록](./API_ENDPOINTS.md)
- [배포 설정](./DEPLOYMENT_SETTINGS.md)

