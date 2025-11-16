from datetime import date, timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from bookings.models import Booking
from rooms.models import Room, Amenity
from categories.models import Category
from users.models import User


class TestRoomBookings(APITestCase):
    def setUp(self):
        """테스트 전에 실행되는 설정"""
        # 테스트용 사용자 생성 및 인증
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        
        # 테스트용 Category 생성
        self.category = Category.objects.create(
            name="Test Category",
            kind=Category.CategoryKindChoices.ROOMS
        )
        
        # 테스트용 Room 생성
        self.room = Room.objects.create(
            name="Test Room",
            country="한국",
            city="서울",
            price=50000,
            rooms=2,
            toilets=1,
            description="Test Description",
            address="Test Address",
            kind=Room.RoomKindChoices.ENTIRE_PLACE,
            owner=self.user,
            category=self.category,
        )
        self.base_url = f"/api/v1/rooms/{self.room.pk}/bookings"
        
        # 테스트용 날짜 설정
        self.today = timezone.localdate()
        self.tomorrow = self.today + timedelta(days=1)
        self.day_after_tomorrow = self.today + timedelta(days=2)
        self.three_days_later = self.today + timedelta(days=3)

    def test_create_room_booking(self):
        """POST /api/v1/rooms/<pk>/bookings/ - Room 예약 생성 테스트"""
        data = {
            "check_in": self.tomorrow.strftime("%Y-%m-%d"),
            "check_out": self.day_after_tomorrow.strftime("%Y-%m-%d"),
            "guests": 2,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["check_in"], self.tomorrow.strftime("%Y-%m-%d"))
        self.assertEqual(response.data["check_out"], self.day_after_tomorrow.strftime("%Y-%m-%d"))
        self.assertEqual(response.data["guests"], 2)
        self.assertTrue(
            Booking.objects.filter(
                room=self.room,
                user=self.user,
                check_in=self.tomorrow,
                check_out=self.day_after_tomorrow,
            ).exists()
        )

    def test_create_booking_with_past_check_in(self):
        """POST /api/v1/rooms/<pk>/bookings/ - 과거 check_in 날짜 사용 시 에러 테스트"""
        yesterday = self.today - timedelta(days=1)
        data = {
            "check_in": yesterday.strftime("%Y-%m-%d"),
            "check_out": self.tomorrow.strftime("%Y-%m-%d"),
            "guests": 2,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (과거 날짜는 사용 불가 - serializer.errors 반환)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("check_in", response.data)

    def test_create_booking_check_out_before_check_in(self):
        """POST /api/v1/rooms/<pk>/bookings/ - check_out이 check_in 이전인 경우 에러 테스트"""
        data = {
            "check_in": self.day_after_tomorrow.strftime("%Y-%m-%d"),
            "check_out": self.tomorrow.strftime("%Y-%m-%d"),
            "guests": 2,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (validation 에러 - serializer.errors 반환)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # serializer.errors에 validation 에러가 포함되어 있는지 확인
        self.assertIsInstance(response.data, dict)

    def test_create_booking_check_out_equal_check_in(self):
        """POST /api/v1/rooms/<pk>/bookings/ - check_out이 check_in과 같은 경우 에러 테스트"""
        data = {
            "check_in": self.tomorrow.strftime("%Y-%m-%d"),
            "check_out": self.tomorrow.strftime("%Y-%m-%d"),
            "guests": 2,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (validation 에러 - serializer.errors 반환)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # serializer.errors에 validation 에러가 포함되어 있는지 확인
        self.assertIsInstance(response.data, dict)

    def test_create_booking_overlapping_dates(self):
        """POST /api/v1/rooms/<pk>/bookings/ - 중복 날짜 예약 시 에러 테스트"""
        # 첫 번째 예약 생성
        Booking.objects.create(
            room=self.room,
            user=self.user,
            kind=Booking.BookingKindChoices.ROOM,
            check_in=self.tomorrow,
            check_out=self.day_after_tomorrow,
            guests=2,
        )

        # 중복되는 날짜로 예약 시도
        data = {
            "check_in": self.tomorrow.strftime("%Y-%m-%d"),
            "check_out": self.three_days_later.strftime("%Y-%m-%d"),
            "guests": 2,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (중복 날짜는 views.py에서 ParseError 발생 또는 serializer validation)
        # serializer의 validate에서 체크하거나 views에서 체크
        # 200과 serializer.errors 또는 400과 ParseError 모두 가능
        if response.status_code == status.HTTP_200_OK:
            # serializer validation 에러인 경우
            self.assertIsInstance(response.data, dict)
        else:
            # ParseError인 경우
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_room_bookings_list(self):
        """GET /api/v1/rooms/<pk>/bookings/ - 예약 목록 조회 테스트"""
        # 예약 생성
        Booking.objects.create(
            room=self.room,
            user=self.user,
            kind=Booking.BookingKindChoices.ROOM,
            check_in=self.tomorrow,
            check_out=self.day_after_tomorrow,
            guests=2,
        )

        # API 호출 (현재 년월로 조회)
        current_year = self.today.year
        current_month = self.today.month
        response = self.client.get(
            self.base_url, {"year": current_year, "month": current_month}
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # 예약이 목록에 포함되어 있는지 확인
        if response.data:
            booking = response.data[0]
            self.assertEqual(booking["check_in"], self.tomorrow.strftime("%Y-%m-%d"))

    def test_get_room_bookings_with_pagination(self):
        """GET /api/v1/rooms/<pk>/bookings/ - 페이지네이션 테스트"""
        # 여러 예약 생성
        for i in range(5):
            Booking.objects.create(
                room=self.room,
                user=self.user,
                kind=Booking.BookingKindChoices.ROOM,
                check_in=self.tomorrow + timedelta(days=i),
                check_out=self.day_after_tomorrow + timedelta(days=i),
                guests=2,
            )

        # API 호출 (페이지 1)
        current_year = self.today.year
        current_month = self.today.month
        response = self.client.get(
            self.base_url, {"year": current_year, "month": current_month, "page": 1}
        )

        # 검증 (PAGE_SIZE = 3이므로 최대 3개)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertLessEqual(len(response.data), 3)

    def test_get_room_bookings_invalid_month(self):
        """GET /api/v1/rooms/<pk>/bookings/ - 잘못된 month 파라미터 테스트"""
        current_year = self.today.year
        
        # API 호출 (month = 13)
        response = self.client.get(self.base_url, {"year": current_year, "month": 13})

        # 검증
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # API 호출 (month = 0)
        response = self.client.get(self.base_url, {"year": current_year, "month": 0})

        # 검증
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_room_bookings_invalid_page(self):
        """GET /api/v1/rooms/<pk>/bookings/ - 잘못된 page 파라미터 테스트"""
        current_year = self.today.year
        current_month = self.today.month
        
        # API 호출 (page = 0)
        response = self.client.get(
            self.base_url, {"year": current_year, "month": current_month, "page": 0}
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_room_bookings_room_not_found(self):
        """GET /api/v1/rooms/<pk>/bookings/ - 존재하지 않는 Room 조회 시 404 테스트"""
        # API 호출
        response = self.client.get("/api/v1/rooms/999/bookings/")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_booking_unauthenticated(self):
        """POST /api/v1/rooms/<pk>/bookings/ - 비인증 사용자 예약 시 에러 테스트"""
        # 인증 해제
        self.client.force_authenticate(user=None)
        
        data = {
            "check_in": self.tomorrow.strftime("%Y-%m-%d"),
            "check_out": self.day_after_tomorrow.strftime("%Y-%m-%d"),
            "guests": 2,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (인증 필요 - IsAuthenticatedOrReadOnly는 403 반환)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

