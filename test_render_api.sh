#!/bin/bash

# Render 배포된 API 테스트 스크립트
BASE_URL="https://airbnb-backend-dyxn.onrender.com"

echo "=========================================="
echo "Testing Render Deployed API"
echo "Base URL: $BASE_URL"
echo "=========================================="
echo ""

# Health Check (rooms 엔드포인트)
echo "1. Testing /api/v1/rooms/ (Health Check)"
curl -X GET "$BASE_URL/api/v1/rooms/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  -s | head -20
echo ""
echo ""

# Categories 엔드포인트
echo "2. Testing /api/v1/categories/"
curl -X GET "$BASE_URL/api/v1/categories/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  -s | head -20
echo ""
echo ""

# Users 엔드포인트
echo "3. Testing /api/v1/users/"
curl -X GET "$BASE_URL/api/v1/users/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  -s | head -20
echo ""
echo ""

# Admin 엔드포인트 (접근 불가능할 수 있음)
echo "4. Testing /admin/ (should redirect or show 403)"
curl -X GET "$BASE_URL/admin/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  -s -L | head -10
echo ""
echo ""

echo "=========================================="
echo "Test completed!"
echo "=========================================="

