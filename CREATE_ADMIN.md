# Render에서 관리자 계정 생성하기

Render 무료 플랜에서는 Shell 접근이 불가능하므로, 관리자 계정을 생성하는 여러 방법이 있습니다.

## ⚠️ 중요: Internal Database URL vs External Database URL

- **Internal Database URL**: Render 내부 네트워크에서만 접근 가능 (로컬에서 접근 불가)
- **External Database URL**: 외부에서 접근 가능 (로컬에서 접근 가능)

로컬에서 스크립트를 실행하려면 **External Database URL**을 사용해야 합니다.

## 방법 1: `create_admin.py` 스크립트 사용 (추천)

### 1단계: Render에서 DATABASE_URL 복사

1. Render 대시보드 → **"airbnb-db"** 데이터베이스 클릭
2. **"Connections"** 탭 또는 **"Info"** 탭에서 **"Internal Database URL"** 또는 **"External Database URL"** 복사
   - 형식: `postgresql://user:password@host:port/database_name`
   - 또는 `postgres://user:password@host:port/database_name`

### 2단계: 로컬에서 스크립트 실행

```bash
# 환경변수로 DATABASE_URL 설정
export DATABASE_URL="postgresql://user:password@host:port/database_name"

# 스크립트 실행
python create_admin.py --username admin --email your@email.com

# 비밀번호는 프롬프트에서 입력
```

또는 인자로 직접 전달:

```bash
python create_admin.py \
  --database-url "postgresql://user:password@host:port/database_name" \
  --username admin \
  --email your@email.com \
  --password yourpassword
```

## 방법 2: 환경변수 설정 후 `createsuperuser` 사용

### 1단계: .env 파일에 임시로 DATABASE_URL 추가

`.env` 파일 (로컬 개발용이 아닌 임시 파일로 만드세요):

```env
DATABASE_URL=postgresql://user:password@host:port/database_name
SECRET_KEY=your-secret-key-here
```

### 2단계: Django createsuperuser 실행

```bash
python manage.py createsuperuser
```

### 3단계: .env 파일에서 DATABASE_URL 제거

로컬 개발을 위해 `.env` 파일을 원래대로 복구하세요.

## 방법 3: Render 환경변수에서 직접 확인

Render 대시보드에서 `DATABASE_URL` 환경변수를 확인하고, 위의 방법 1 또는 2를 사용하세요.

## 주의사항

⚠️ **보안**: DATABASE_URL에는 비밀번호가 포함되어 있으므로 다음을 주의하세요:
- `.env` 파일을 Git에 커밋하지 마세요
- 스크립트 실행 후 환경변수를 정리하세요
- `DATABASE_URL`을 다른 사람과 공유하지 마세요

## 문제 해결

### "No module named 'psycopg2'" 오류
```bash
pip install psycopg2-binary
# 또는
poetry add psycopg2-binary
```

### "FATAL: password authentication failed" 오류
- DATABASE_URL이 정확한지 확인
- Internal Database URL 사용 (Render 내부 네트워크)
- External Database URL은 IP 허용 목록 설정 필요할 수 있음

### "could not connect to server" 오류
- Render 데이터베이스가 실행 중인지 확인
- External Database URL 사용 시 IP 허용 목록 확인
- Internal Database URL 사용 권장

## 완료 후 확인

관리자 계정 생성 후:
1. `https://airbnb-backend-yvup.onrender.com/admin/` 접속
2. 생성한 계정으로 로그인 확인

