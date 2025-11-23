#!/bin/bash

# Render 관리자 계정 생성 스크립트 (간단 버전)

DATABASE_URL="postgresql://airbnb_qfh4_user:hC2x0NKePmnseTJcSYu5Bjh8iT8Vf8i1@dpg-d4gvcs0dl3ps73d6poug-a/airbnb_qfh4"

echo "=========================================="
echo "Render 관리자 계정 생성"
echo "=========================================="
echo ""

# 사용자 입력
read -p "사용자명 (기본값: admin): " username
username=${username:-admin}

read -p "이메일: " email
if [ -z "$email" ]; then
    echo "❌ 이메일은 필수입니다."
    exit 1
fi

read -sp "비밀번호: " password
echo ""
if [ -z "$password" ]; then
    echo "❌ 비밀번호는 필수입니다."
    exit 1
fi

read -sp "비밀번호 확인: " password_confirm
echo ""

if [ "$password" != "$password_confirm" ]; then
    echo "❌ 비밀번호가 일치하지 않습니다."
    exit 1
fi

echo ""
echo "=========================================="
echo "관리자 계정 생성 중..."
echo "=========================================="

# 스크립트 실행
poetry run python create_admin.py \
  --database-url "$DATABASE_URL" \
  --username "$username" \
  --email "$email" \
  --password "$password"

