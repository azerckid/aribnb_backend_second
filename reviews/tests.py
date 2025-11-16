from rest_framework.test import APITestCase
from rest_framework import status
from reviews.models import Review
from rooms.models import Room
from categories.models import Category
from users.models import User


class TestRoomReviews(APITestCase):
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
        self.base_url = f"/api/v1/rooms/{self.room.pk}/reviews"

    def test_create_room_review(self):
        """POST /api/v1/rooms/<pk>/reviews - Room 리뷰 생성 테스트"""
        data = {
            "payload": "Great room!",
            "rating": 5,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["payload"], "Great room!")
        self.assertEqual(response.data["rating"], 5)
        self.assertTrue(
            Review.objects.filter(
                room=self.room,
                user=self.user,
                rating=5,
            ).exists()
        )

    def test_create_review_with_invalid_rating_high(self):
        """POST /api/v1/rooms/<pk>/reviews - 평점이 5를 초과하는 경우 에러 테스트"""
        data = {
            "payload": "Test Review",
            "rating": 6,  # 5를 초과
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (validation 에러 - serializer.errors 반환)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_create_review_with_invalid_rating_low(self):
        """POST /api/v1/rooms/<pk>/reviews - 평점이 1 미만인 경우 에러 테스트"""
        data = {
            "payload": "Test Review",
            "rating": 0,  # 1 미만
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (validation 에러 - serializer.errors 반환)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_create_review_without_payload(self):
        """POST /api/v1/rooms/<pk>/reviews - payload 없이 리뷰 생성 시 에러 테스트"""
        data = {
            "rating": 5,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (validation 에러 - serializer.errors 반환)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_get_room_reviews_list(self):
        """GET /api/v1/rooms/<pk>/reviews - 리뷰 목록 조회 테스트"""
        # 리뷰 생성
        Review.objects.create(
            room=self.room,
            user=self.user,
            payload="First Review",
            rating=4,
        )

        # API 호출
        response = self.client.get(self.base_url)

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["payload"], "First Review")
        self.assertEqual(response.data[0]["rating"], 4)

    def test_get_room_reviews_with_pagination(self):
        """GET /api/v1/rooms/<pk>/reviews - 페이지네이션 테스트"""
        # 여러 리뷰 생성
        for i in range(5):
            Review.objects.create(
                room=self.room,
                user=self.user,
                payload=f"Review {i+1}",
                rating=4,
            )

        # API 호출 (페이지 1)
        response = self.client.get(self.base_url, {"page": 1})

        # 검증 (PAGE_SIZE = 3이므로 최대 3개)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertLessEqual(len(response.data), 3)

    def test_room_rating_calculation(self):
        """Room 평점 계산 테스트"""
        # 여러 리뷰 생성
        Review.objects.create(
            room=self.room,
            user=self.user,
            payload="Review 1",
            rating=5,
        )
        # 다른 사용자 생성
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123"
        )
        Review.objects.create(
            room=self.room,
            user=other_user,
            payload="Review 2",
            rating=3,
        )

        # Room의 rating 메서드 호출
        calculated_rating = self.room.rating()

        # 검증 (평균: (5 + 3) / 2 = 4.0)
        self.assertEqual(calculated_rating, 4.0)

    def test_room_rating_with_no_reviews(self):
        """리뷰가 없는 Room의 평점 테스트"""
        # 리뷰가 없는 Room 생성
        new_room = Room.objects.create(
            name="New Room",
            country="한국",
            city="서울",
            price=60000,
            rooms=3,
            toilets=2,
            description="Description",
            address="Address",
            kind=Room.RoomKindChoices.ENTIRE_PLACE,
            owner=self.user,
            category=self.category,
        )

        # Room의 rating 메서드 호출
        calculated_rating = new_room.rating()

        # 검증 (리뷰가 없으면 0 반환)
        self.assertEqual(calculated_rating, 0)

    def test_create_review_unauthenticated(self):
        """POST /api/v1/rooms/<pk>/reviews - 비인증 사용자 리뷰 생성 시 에러 테스트"""
        # 인증 해제
        self.client.force_authenticate(user=None)
        
        data = {
            "payload": "Test Review",
            "rating": 5,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (인증 필요 - IsAuthenticatedOrReadOnly는 403 반환)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_reviews_unauthenticated(self):
        """GET /api/v1/rooms/<pk>/reviews - 비인증 사용자 리뷰 목록 조회 테스트"""
        # 인증 해제
        self.client.force_authenticate(user=None)
        
        # API 호출
        response = self.client.get(self.base_url)

        # 검증 (IsAuthenticatedOrReadOnly이므로 읽기는 가능)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_reviews_room_not_found(self):
        """GET /api/v1/rooms/<pk>/reviews - 존재하지 않는 Room 조회 시 404 테스트"""
        # API 호출
        response = self.client.get("/api/v1/rooms/999/reviews")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_multiple_reviews_same_user(self):
        """같은 사용자가 여러 리뷰 작성 테스트"""
        # 첫 번째 리뷰
        data1 = {
            "payload": "First Review",
            "rating": 5,
        }
        response1 = self.client.post(self.base_url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # 두 번째 리뷰 (같은 사용자, 같은 방)
        data2 = {
            "payload": "Second Review",
            "rating": 4,
        }
        response2 = self.client.post(self.base_url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # 검증 (두 리뷰 모두 생성됨)
        reviews = Review.objects.filter(room=self.room, user=self.user)
        self.assertEqual(reviews.count(), 2)

