#!/bin/bash
# 빠른 관리자 계정 생성 (모든 값을 직접 입력)

DATABASE_URL="postgresql://airbnb_qfh4_user:hC2x0NKePmnseTJcSYu5Bjh8iT8Vf8i1@dpg-d4gvcs0dl3ps73d6poug-a/airbnb_qfh4"

# 여기에 값을 직접 입력하세요
USERNAME="admin"
EMAIL="your@email.com"
PASSWORD="yourpassword"

poetry run python create_admin.py \
  --database-url "$DATABASE_URL" \
  --username "$USERNAME" \
  --email "$EMAIL" \
  --password "$PASSWORD"
