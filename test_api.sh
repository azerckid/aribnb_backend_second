#!/bin/bash

# API 테스트 스크립트
# 사용법: ./test_api.sh

BASE_URL="http://localhost:8000/api/v1/categories"

echo "=== 1. GET /api/v1/categories/ (목록 조회) ==="
curl -X GET "$BASE_URL/" -H "Content-Type: application/json" | python3 -m json.tool
echo -e "\n"

echo "=== 2. POST /api/v1/categories/ (생성) ==="
curl -X POST "$BASE_URL/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Beach Houses", "kind": "rooms"}' | python3 -m json.tool
echo -e "\n"

echo "=== 3. GET /api/v1/categories/1 (개별 조회) ==="
curl -X GET "$BASE_URL/1" -H "Content-Type: application/json" | python3 -m json.tool
echo -e "\n"

echo "=== 4. PUT /api/v1/categories/1 (수정) ==="
curl -X PUT "$BASE_URL/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Beach Houses"}' | python3 -m json.tool
echo -e "\n"

echo "=== 5. DELETE /api/v1/categories/1 (삭제) ==="
curl -X DELETE "$BASE_URL/1" -H "Content-Type: application/json" -v
echo -e "\n"

