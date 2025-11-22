# Render 배포 가이드

이 문서는 Django Airbnb Backend 프로젝트를 Render에 배포하는 방법을 설명합니다.

## 📋 사전 준비사항

1. GitHub 저장소에 코드 푸시 완료
2. Render 계정 생성 (https://render.com)
3. 환경변수 준비 (아래 참고)

## 🚀 배포 방법: 두 가지 옵션

### 방법 1: render.yaml 사용 (권장 ⭐)

**Infrastructure as Code 방식** - 설정을 코드로 관리

1. **render.yaml 파일 확인**
   - 프로젝트 루트에 `render.yaml` 파일이 이미 생성되어 있습니다.
   - 이 파일에 웹서비스와 데이터베이스 설정이 포함되어 있습니다.

2. **Render에서 Blueprint 배포**
   - Render 대시보드 → "New +" → "Blueprint" 클릭
   - GitHub 저장소 연결
   - `render.yaml` 파일이 자동으로 감지됩니다.
   - "Apply" 클릭하여 배포 시작

3. **환경변수 설정**
   - 배포 후 Render 대시보드에서 환경변수를 설정해야 합니다.
   - `sync: false`로 표시된 환경변수는 수동으로 설정해야 합니다:
     - `SECRET_KEY`
     - `CORS_ALLOWED_ORIGINS`
     - `CSRF_TRUSTED_ORIGINS`
     - `CLOUDINARY_*`
     - OAuth 관련 변수들

4. **장점**
   - ✅ 설정을 코드로 관리 (버전 관리 가능)
   - ✅ 여러 서비스를 한 번에 배포 (웹서비스 + 데이터베이스)
   - ✅ 재현 가능한 배포
   - ✅ 자동화에 적합

### 방법 2: GUI를 통한 수동 배포

**대시보드를 통한 수동 설정** - 더 직관적이지만 설정 관리가 어려움

## 🚀 배포 단계 (GUI 방식)

### 1. Render 웹서비스 생성

1. Render 대시보드 → "New +" → "Web Service" 클릭
2. GitHub 저장소 연결
3. 프로젝트 선택

### 2. 서비스 설정

**기본 설정:**
- **Name**: `airbnb-backend` (원하는 이름)
- **Region**: `Singapore` (아시아에 가까운 지역)
- **Branch**: `main`
- **Root Directory**: (비워두기)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  chmod +x build.sh && ./build.sh
  ```
- **Start Command**: 
  ```
  gunicorn config.wsgi:application
  ```

### 3. PostgreSQL 데이터베이스 생성

1. Render 대시보드 → "New +" → "PostgreSQL" 클릭
2. 설정:
   - **Name**: `airbnb-db`
   - **Database**: `airbnb`
   - **User**: 자동 생성
   - **Region**: 웹서비스와 동일하게 선택
   - **PostgreSQL Version**: 16 (최신)
   - **Plan**: Free

3. 생성 후 **Internal Database URL** 복사 (환경변수에 사용)

### 4. 환경변수 설정

웹서비스 설정의 **Environment** 섹션에서 다음 환경변수 추가:

#### 필수 환경변수:

```bash
# Django 기본 설정
SECRET_KEY=your-secret-key-here  # Django SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com

# 데이터베이스 (PostgreSQL 서비스의 Internal Database URL 사용)
DATABASE_URL=postgresql://user:password@host:port/database

# CORS 설정 (프론트엔드 도메인)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-frontend-domain.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com,https://your-frontend-domain.vercel.app

# Cloudinary (이미 설정되어 있으면 동일)
CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret

# OAuth (GitHub)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OAuth (Kakao)
KAKAO_CLIENT_ID=your-kakao-client-id
KAKAO_CLIENT_SECRET=your-kakao-client-secret
KAKAO_REDIRECT_URI=https://your-frontend-domain.com/auth/kakao/callback
```

#### SECRET_KEY 생성 방법:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. 배포 및 확인

1. **"Create Web Service"** 클릭
2. 배포 진행 상황 모니터링 (Build Log 확인)
3. **서비스 URL 확인 방법:**
   - 방법 1: 서비스 목록에서 **"airbnb-backend"** 클릭 → 상세 페이지 상단에 URL 표시
   - 방법 2: 서비스 상세 페이지 → **"Settings"** 탭 → Service 정보 섹션에서 URL 확인
   - 방법 3: 서비스 상세 페이지 상단에 **"Visit site"** 버튼 옆에 URL 표시
   - 기본 형식: `https://airbnb-backend.onrender.com`
4. 배포 완료 후 URL로 접속 테스트

### 6. 마이그레이션 (자동 실행됨)

`build.sh`에서 자동으로 마이그레이션이 실행됩니다. 필요시 수동으로 실행:

1. Render 대시보드 → 웹서비스 → **Shell** 탭
2. 다음 명령 실행:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # 관리자 계정 생성
   ```

## 📝 중요 사항

### 무료 티어 제한사항:

1. **15분 무활동 시 자동 수면**
   - 첫 요청 시 깨어나는 데 약 30초~1분 소요
   - 항상 활성 상태 유지하려면 유료 플랜 필요

2. **리소스 제한**
   - CPU: 0.1-0.25 CPU
   - RAM: 512MB
   - PostgreSQL: 256MB 저장공간, 90일 무활동 시 삭제

3. **월간 제한**
   - 웹서비스: 750시간 (충분함)
   - PostgreSQL: 90일 무활동 시 삭제

### 최적화 팁:

1. **Keep-Alive 설정** (필요시)
   - 외부 서비스로 주기적 ping (UptimeRobot 등)

2. **로깅 모니터링**
   - Render 대시보드에서 로그 확인
   - 에러 발생 시 즉시 확인 가능

3. **환경변수 보안**
   - `.env` 파일은 Git에 커밋하지 않기
   - 모든 민감 정보는 Render 환경변수로 관리

## 🔧 트러블슈팅

### 배포 실패 시:

1. **Build Log 확인**
   - 의존성 설치 오류
   - Python 버전 불일치

2. **Runtime Log 확인**
   - 애플리케이션 실행 오류
   - 환경변수 누락

3. **데이터베이스 연결 오류**
   - `DATABASE_URL` 확인
   - PostgreSQL 서비스가 실행 중인지 확인

### 자주 발생하는 오류:

1. **`No module named 'gunicorn'`**
   - `requirements.txt`에 `gunicorn`이 있는지 확인

2. **`Database connection failed`**
   - `DATABASE_URL` 환경변수 확인
   - PostgreSQL 서비스 상태 확인

3. **`ALLOWED_HOSTS` 오류**
   - Render에서 제공하는 도메인을 `ALLOWED_HOSTS`에 추가

## 📚 참고 자료

- [Render 공식 문서](https://render.com/docs)
- [Django on Render](https://render.com/docs/deploy-django)
- [PostgreSQL on Render](https://render.com/docs/databases)

## ✅ 배포 체크리스트

- [ ] GitHub 저장소에 코드 푸시 완료
- [ ] Render 계정 생성 완료
- [ ] PostgreSQL 데이터베이스 생성 완료
- [ ] 모든 환경변수 설정 완료
- [ ] 웹서비스 생성 및 배포 완료
- [ ] 마이그레이션 실행 완료
- [ ] 관리자 계정 생성 완료
- [ ] API 엔드포인트 테스트 완료
- [ ] 프론트엔드에서 연동 테스트 완료

