# API 엔드포인트 목록

## 인증 (Authentication)
- `POST /api/v1/users/log-in` - 세션 로그인
- `POST /api/v1/users/log-out` - 세션 로그아웃
- `POST /api/v1/users/token-login` - 토큰 발급
- `POST /api/v1/users/jwt-login` - JWT 토큰 발급

## 사용자 (Users)
- `GET /api/v1/users/` - 사용자 목록
- `POST /api/v1/users/` - 사용자 회원가입
- `GET /api/v1/users/me` - 현재 사용자 정보
- `PUT /api/v1/users/me` - 현재 사용자 정보 수정
- `PUT /api/v1/users/change-password` - 비밀번호 변경
- `GET /api/v1/users/@<username>` - 공개 사용자 프로필

## 카테고리 (Categories)
- `GET /api/v1/categories/` - 카테고리 목록
- `POST /api/v1/categories/` - 카테고리 생성
- `GET /api/v1/categories/<pk>` - 카테고리 상세
- `PUT /api/v1/categories/<pk>` - 카테고리 수정
- `DELETE /api/v1/categories/<pk>` - 카테고리 삭제

## 방 (Rooms)
- `GET /api/v1/rooms/` - 방 목록
- `POST /api/v1/rooms/` - 방 생성
- `GET /api/v1/rooms/<pk>` - 방 상세
- `PUT /api/v1/rooms/<pk>` - 방 수정
- `DELETE /api/v1/rooms/<pk>` - 방 삭제

## 편의시설 (Amenities)
- `GET /api/v1/rooms/amenities/` - 편의시설 목록
- `POST /api/v1/rooms/amenities/` - 편의시설 생성
- `GET /api/v1/rooms/amenities/<pk>` - 편의시설 상세
- `PUT /api/v1/rooms/amenities/<pk>` - 편의시설 수정
- `DELETE /api/v1/rooms/amenities/<pk>` - 편의시설 삭제

## 침대 (Beds)
- `GET /api/v1/rooms/<pk>/beds` - 방의 침대 목록
- `POST /api/v1/rooms/<pk>/beds` - 침대 생성
- `GET /api/v1/rooms/<pk>/beds/<bed_pk>` - 침대 상세
- `PUT /api/v1/rooms/<pk>/beds/<bed_pk>` - 침대 수정
- `DELETE /api/v1/rooms/<pk>/beds/<bed_pk>` - 침대 삭제

## 리뷰 (Reviews)
- `GET /api/v1/rooms/<pk>/reviews` - 방 리뷰 목록
- `POST /api/v1/rooms/<pk>/reviews` - 방 리뷰 생성
- `GET /api/v1/experiences/<pk>/reviews` - 체험 리뷰 목록
- `POST /api/v1/experiences/<pk>/reviews` - 체험 리뷰 생성

## 예약 (Bookings)
- `GET /api/v1/rooms/<pk>/bookings?year=2024&month=12` - 방 예약 목록 (월별 조회)
- `POST /api/v1/rooms/<pk>/bookings` - 방 예약 생성
- `GET /api/v1/rooms/<pk>/beds/<bed_pk>/bookings?year=2024&month=12` - 침대 예약 목록
- `POST /api/v1/rooms/<pk>/beds/<bed_pk>/bookings` - 침대 예약 생성

## 체험 (Experiences)
- `GET /api/v1/experiences/` - 체험 목록
- `POST /api/v1/experiences/` - 체험 생성
- `GET /api/v1/experiences/<pk>` - 체험 상세
- `PUT /api/v1/experiences/<pk>` - 체험 수정
- `DELETE /api/v1/experiences/<pk>` - 체험 삭제

## 특전 (Perks)
- `GET /api/v1/experiences/perks/` - 특전 목록
- `POST /api/v1/experiences/perks/` - 특전 생성
- `GET /api/v1/experiences/perks/<pk>` - 특전 상세
- `PUT /api/v1/experiences/perks/<pk>` - 특전 수정
- `DELETE /api/v1/experiences/perks/<pk>` - 특전 삭제
- `GET /api/v1/experiences/<pk>/perks` - 특정 체험의 특전 목록

## 체험 예약 (Experience Bookings)
- `GET /api/v1/experiences/<pk>/bookings` - 체험 예약 목록
- `POST /api/v1/experiences/<pk>/bookings` - 체험 예약 생성
- `GET /api/v1/experiences/<pk>/bookings/<booking_pk>` - 체험 예약 상세
- `PUT /api/v1/experiences/<pk>/bookings/<booking_pk>` - 체험 예약 수정
- `DELETE /api/v1/experiences/<pk>/bookings/<booking_pk>` - 체험 예약 삭제

## 위시리스트 (Wishlists)
- `GET /api/v1/wishlists/` - 위시리스트 목록
- `POST /api/v1/wishlists/` - 위시리스트 생성
- `GET /api/v1/wishlists/<pk>` - 위시리스트 상세
- `PUT /api/v1/wishlists/<pk>` - 위시리스트 수정
- `DELETE /api/v1/wishlists/<pk>` - 위시리스트 삭제
- `PUT /api/v1/wishlists/<pk>/rooms/<room_pk>` - 방 추가/제거 (토글)
- `PUT /api/v1/wishlists/<pk>/experiences/<experience_pk>` - 체험 추가/제거 (토글)

## 미디어 (Medias)
- `DELETE /api/v1/medias/photos/<pk>` - 사진 삭제
- `POST /api/v1/rooms/<pk>/photos` - 방 사진 업로드

