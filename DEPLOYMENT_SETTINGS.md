# 배포 시 도메인 설정 가이드

이 문서는 Django 백엔드와 프론트엔드가 서로 다른 도메인을 가질 때 필요한 설정을 설명합니다.

## 📍 도메인 설정 개념

### 1. `ALLOWED_HOSTS` (백엔드 서버 도메인)
**목적**: Django 백엔드 서버가 허용할 호스트(도메인) 목록  
**설정 대상**: **백엔드 서버 자체의 도메인**  
**예시**: Render에 배포하면 `airbnb-backend.onrender.com`

```python
ALLOWED_HOSTS = [
    "airbnb-backend.onrender.com",  # 백엔드 서버 도메인
    "localhost",                     # 로컬 개발용
    "127.0.0.1",                     # 로컬 개발용
]
```

### 2. `CORS_ALLOWED_ORIGINS` (프론트엔드 도메인)
**목적**: 백엔드 API를 호출할 수 있는 프론트엔드 도메인 목록  
**설정 대상**: **프론트엔드 도메인**  
**예시**: Vercel에 배포하면 `https://airbnb-frontend.vercel.app`

```python
CORS_ALLOWED_ORIGINS = [
    "https://airbnb-frontend.vercel.app",  # 프론트엔드 프로덕션 도메인
    "http://localhost:5173",                # 로컬 개발용
    "http://localhost:3000",                # 로컬 개발용
]
```

### 3. `CSRF_TRUSTED_ORIGINS` (프론트엔드 도메인)
**목적**: CSRF 토큰 검증 시 신뢰할 수 있는 프론트엔드 도메인 목록  
**설정 대상**: **프론트엔드 도메인**  
**예시**: Vercel에 배포하면 `https://airbnb-frontend.vercel.app`

```python
CSRF_TRUSTED_ORIGINS = [
    "https://airbnb-frontend.vercel.app",  # 프론트엔드 프로덕션 도메인
    "http://localhost:5173",                # 로컬 개발용
    "http://localhost:3000",                # 로컬 개발용
]
```

## 🔄 배포 시나리오별 설정

### 시나리오 1: Render (백엔드) + Vercel (프론트엔드)

#### Render 환경변수 설정:
```bash
# 백엔드 서버 도메인 (Render에서 제공)
ALLOWED_HOSTS=airbnb-backend.onrender.com

# 프론트엔드 도메인 (Vercel에서 제공)
CORS_ALLOWED_ORIGINS=https://airbnb-frontend.vercel.app,https://airbnb-frontend-git-main-user.vercel.app
CSRF_TRUSTED_ORIGINS=https://airbnb-frontend.vercel.app,https://airbnb-frontend-git-main-user.vercel.app
```

#### 프론트엔드 코드에서 API 호출:
```javascript
// 프론트엔드에서 백엔드 API 호출
const API_URL = 'https://airbnb-backend.onrender.com/api/v1';

fetch(`${API_URL}/rooms/`)
  .then(res => res.json())
  .then(data => console.log(data));
```

### 시나리오 2: 동일한 도메인 사용 (서브도메인)

만약 백엔드와 프론트엔드를 같은 도메인의 서브도메인으로 사용한다면:

```
프론트엔드: https://app.example.com
백엔드: https://api.example.com
```

#### 환경변수 설정:
```bash
ALLOWED_HOSTS=api.example.com
CORS_ALLOWED_ORIGINS=https://app.example.com
CSRF_TRUSTED_ORIGINS=https://app.example.com
```

## ✅ 질문에 대한 답변

**Q: `ALLOWED_HOSTS`는 프론트엔드 도메인이 바뀌면 변경해야 하나?**

**A: 아니요!** `ALLOWED_HOSTS`는 **백엔드 서버 도메인**을 지정합니다.
- 프론트엔드 도메인이 바뀌면 → `CORS_ALLOWED_ORIGINS`와 `CSRF_TRUSTED_ORIGINS`만 변경
- 백엔드 서버 도메인이 바뀌면 → `ALLOWED_HOSTS` 변경

## 📝 실제 예시

### 현재 설정 (로컬 개발)
```python
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # 백엔드: 로컬호스트
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # 프론트엔드: 로컬호스트:5173
]
```

### Render 배포 후 (프론트엔드가 Vercel에 있는 경우)
```bash
# Render 환경변수
ALLOWED_HOSTS=airbnb-backend.onrender.com  # ✅ 백엔드 도메인
CORS_ALLOWED_ORIGINS=https://airbnb-frontend.vercel.app  # ✅ 프론트엔드 도메인
CSRF_TRUSTED_ORIGINS=https://airbnb-frontend.vercel.app  # ✅ 프론트엔드 도메인
```

## 🎯 요약

| 설정 | 대상 | 예시 |
|------|------|------|
| `ALLOWED_HOSTS` | **백엔드 서버** 도메인 | `airbnb-backend.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | **프론트엔드** 도메인 | `https://airbnb-frontend.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | **프론트엔드** 도메인 | `https://airbnb-frontend.vercel.app` |

**결론**: 프론트엔드 도메인이 바뀌면 `CORS_ALLOWED_ORIGINS`와 `CSRF_TRUSTED_ORIGINS`만 변경하면 됩니다. `ALLOWED_HOSTS`는 백엔드 서버 도메인을 지정하므로 프론트엔드와 무관합니다.

