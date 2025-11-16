from rest_framework.test import APITestCase
from rest_framework import status
from . import models
from users.models import User
from categories.models import Category


class TestAmenities(APITestCase):
    NAME = "Amenity Test"
    DESC = "Amenity Des"

    def setUp(self):
        """테스트 전에 실행되는 설정"""
        # 테스트용 사용자 생성 및 인증
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.base_url = "/api/v1/rooms/amenities/"

    def test_all_amenities(self):
        """GET /api/v1/rooms/amenities/ - 목록 조회 테스트"""
        # Amenity 생성
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

        # API 호출
        response = self.client.get(self.base_url)
        data = response.json()

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(data, list)
        # 기존 amenity가 있을 수 있으므로 새로 생성한 amenity가 포함되어 있는지 확인
        amenity_names = [amenity["name"] for amenity in data]
        self.assertIn(self.NAME, amenity_names)

    def test_create_amenity(self):
        """POST /api/v1/rooms/amenities/ - 생성 테스트"""
        data = {
            "name": "New Amenity",
            "description": "New Amenity Description",
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Amenity")
        self.assertEqual(response.data["description"], "New Amenity Description")
        self.assertTrue(models.Amenity.objects.filter(name="New Amenity").exists())

    def test_get_amenity_detail(self):
        """GET /api/v1/rooms/amenities/<pk> - 개별 조회 테스트"""
        # Amenity 생성
        amenity = models.Amenity.objects.create(
            name="Detail Amenity",
            description="Detail Description",
        )

        # API 호출
        response = self.client.get(f"{self.base_url}{amenity.pk}")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Detail Amenity")
        self.assertEqual(response.data["description"], "Detail Description")

    def test_update_amenity(self):
        """PUT /api/v1/rooms/amenities/<pk> - 수정 테스트"""
        # Amenity 생성
        amenity = models.Amenity.objects.create(
            name="Original Name",
            description="Original Description",
        )

        # 수정 데이터
        data = {
            "name": "Updated Name",
            "description": "Updated Description",
        }

        # API 호출
        response = self.client.put(
            f"{self.base_url}{amenity.pk}", data, format="json"
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Name")
        self.assertEqual(response.data["description"], "Updated Description")
        amenity.refresh_from_db()
        self.assertEqual(amenity.name, "Updated Name")
        self.assertEqual(amenity.description, "Updated Description")

    def test_partial_update_amenity(self):
        """PUT /api/v1/rooms/amenities/<pk> - 부분 수정 테스트"""
        # Amenity 생성
        amenity = models.Amenity.objects.create(
            name="Original Name",
            description="Original Description",
        )

        # 부분 수정 데이터 (name만 수정)
        data = {"name": "Partially Updated Name"}

        # API 호출
        response = self.client.put(
            f"{self.base_url}{amenity.pk}", data, format="json"
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Partially Updated Name")
        # description은 그대로 유지되어야 함
        self.assertEqual(response.data["description"], "Original Description")

    def test_delete_amenity(self):
        """DELETE /api/v1/rooms/amenities/<pk> - 삭제 테스트"""
        # Amenity 생성
        amenity = models.Amenity.objects.create(
            name="To Delete",
            description="To Delete Description",
        )
        amenity_id = amenity.pk

        # API 호출
        response = self.client.delete(f"{self.base_url}{amenity_id}")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Amenity.objects.filter(pk=amenity_id).exists())

    def test_amenity_not_found(self):
        """존재하지 않는 Amenity 조회 시 404 테스트"""
        # API 호출
        response = self.client.get(f"{self.base_url}999")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_amenity_without_description(self):
        """POST /api/v1/rooms/amenities/ - description 없이 생성 테스트"""
        data = {
            "name": "Amenity Without Description",
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Amenity Without Description")
        self.assertEqual(response.data["description"], None)
        self.assertTrue(
            models.Amenity.objects.filter(name="Amenity Without Description").exists()
        )


class TestRooms(APITestCase):
    def setUp(self):
        """테스트 전에 실행되는 설정"""
        # 테스트용 사용자 생성 및 인증
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.base_url = "/api/v1/rooms/"
        
        # 테스트용 Category 생성
        self.category = Category.objects.create(
            name="Test Category",
            kind=Category.CategoryKindChoices.ROOMS
        )
        
        # 테스트용 Amenity 생성
        self.amenity = models.Amenity.objects.create(
            name="Test Amenity",
            description="Test Description"
        )

    def test_get_rooms_list(self):
        """GET /api/v1/rooms/ - 목록 조회 테스트"""
        # Room 생성
        room = models.Room.objects.create(
            name="Test Room",
            country="한국",
            city="서울",
            price=50000,
            rooms=2,
            toilets=1,
            description="Test Description",
            address="Test Address",
            kind=models.Room.RoomKindChoices.ENTIRE_PLACE,
            owner=self.user,
            category=self.category,
        )

        # API 호출
        response = self.client.get(self.base_url)

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # 새로 생성한 room이 포함되어 있는지 확인
        room_names = [room["name"] for room in response.data]
        self.assertIn("Test Room", room_names)

    def test_get_rooms_list_unauthenticated(self):
        """GET /api/v1/rooms/ - 비인증 사용자 목록 조회 테스트"""
        # 인증 해제
        self.client.force_authenticate(user=None)
        
        # API 호출
        response = self.client.get(self.base_url)

        # 검증 (IsAuthenticatedOrReadOnly이므로 읽기는 가능)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_room(self):
        """POST /api/v1/rooms/ - 생성 테스트"""
        data = {
            "name": "New Room",
            "country": "한국",
            "city": "부산",
            "price": 60000,
            "rooms": 3,
            "toilets": 2,
            "description": "New Room Description",
            "address": "New Address",
            "kind": models.Room.RoomKindChoices.ENTIRE_PLACE,
            "category": self.category.pk,
            "amenities": [self.amenity.pk],
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Room")
        self.assertTrue(models.Room.objects.filter(name="New Room").exists())
        room = models.Room.objects.get(name="New Room")
        self.assertEqual(room.owner, self.user)
        self.assertEqual(room.amenities.count(), 1)
        self.assertEqual(room.amenities.first(), self.amenity)

    def test_create_room_without_category(self):
        """POST /api/v1/rooms/ - 카테고리 없이 생성 시 에러 테스트"""
        data = {
            "name": "Room Without Category",
            "country": "한국",
            "city": "서울",
            "price": 50000,
            "rooms": 2,
            "toilets": 1,
            "description": "Description",
            "address": "Address",
            "kind": models.Room.RoomKindChoices.ENTIRE_PLACE,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (카테고리가 필수이므로 에러)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_room_with_experience_category(self):
        """POST /api/v1/rooms/ - Experience 카테고리 사용 시 에러 테스트"""
        # Experience 카테고리 생성
        exp_category = Category.objects.create(
            name="Experience Category",
            kind=Category.CategoryKindChoices.EXPERIENCES
        )
        
        data = {
            "name": "Room With Experience Category",
            "country": "한국",
            "city": "서울",
            "price": 50000,
            "rooms": 2,
            "toilets": 1,
            "description": "Description",
            "address": "Address",
            "kind": models.Room.RoomKindChoices.ENTIRE_PLACE,
            "category": exp_category.pk,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증 (Experience 카테고리는 Room에 사용 불가)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_room_with_invalid_amenity(self):
        """POST /api/v1/rooms/ - 존재하지 않는 Amenity 사용 시 에러 테스트"""
        data = {
            "name": "Room With Invalid Amenity",
            "country": "한국",
            "city": "서울",
            "price": 50000,
            "rooms": 2,
            "toilets": 1,
            "description": "Description",
            "address": "Address",
            "kind": models.Room.RoomKindChoices.ENTIRE_PLACE,
            "category": self.category.pk,
            "amenities": [999],  # 존재하지 않는 amenity
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_room_detail(self):
        """GET /api/v1/rooms/<pk> - 개별 조회 테스트"""
        # Room 생성
        room = models.Room.objects.create(
            name="Detail Room",
            country="한국",
            city="서울",
            price=70000,
            rooms=4,
            toilets=2,
            description="Detail Description",
            address="Detail Address",
            kind=models.Room.RoomKindChoices.PRIVATE_ROOM,
            owner=self.user,
            category=self.category,
        )

        # API 호출
        response = self.client.get(f"{self.base_url}{room.pk}")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Detail Room")
        self.assertEqual(response.data["price"], 70000)
        # RoomDetailSerializer는 fields = "__all__" 사용하므로 id 필드 확인
        self.assertEqual(response.data["id"], room.pk)

    def test_get_room_detail_not_found(self):
        """GET /api/v1/rooms/<pk> - 존재하지 않는 Room 조회 시 404 테스트"""
        # API 호출
        response = self.client.get(f"{self.base_url}999")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_room(self):
        """PUT /api/v1/rooms/<pk> - 수정 테스트 (소유자)"""
        # Room 생성
        room = models.Room.objects.create(
            name="Original Name",
            country="한국",
            city="서울",
            price=50000,
            rooms=2,
            toilets=1,
            description="Original Description",
            address="Original Address",
            kind=models.Room.RoomKindChoices.ENTIRE_PLACE,
            owner=self.user,
            category=self.category,
        )

        # 수정 데이터
        data = {
            "name": "Updated Name",
            "country": "한국",
            "city": "부산",
            "price": 80000,
            "rooms": 3,
            "toilets": 2,
            "description": "Updated Description",
            "address": "Updated Address",
            "kind": models.Room.RoomKindChoices.PRIVATE_ROOM,
            "category": self.category.pk,
        }

        # API 호출
        response = self.client.put(
            f"{self.base_url}{room.pk}", data, format="json"
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Name")
        self.assertEqual(response.data["price"], 80000)
        room.refresh_from_db()
        self.assertEqual(room.name, "Updated Name")
        self.assertEqual(room.price, 80000)

    def test_update_room_not_owner(self):
        """PUT /api/v1/rooms/<pk> - 소유자가 아닌 사용자 수정 시 에러 테스트"""
        # 다른 사용자 생성
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123"
        )
        
        # Room 생성 (다른 사용자 소유)
        room = models.Room.objects.create(
            name="Other User's Room",
            country="한국",
            city="서울",
            price=50000,
            rooms=2,
            toilets=1,
            description="Description",
            address="Address",
            kind=models.Room.RoomKindChoices.ENTIRE_PLACE,
            owner=other_user,
            category=self.category,
        )

        # 수정 데이터
        data = {
            "name": "Hacked Name",
            "country": "한국",
            "city": "서울",
            "price": 50000,
            "rooms": 2,
            "toilets": 1,
            "description": "Description",
            "address": "Address",
            "kind": models.Room.RoomKindChoices.ENTIRE_PLACE,
            "category": self.category.pk,
        }

        # API 호출
        response = self.client.put(
            f"{self.base_url}{room.pk}", data, format="json"
        )

        # 검증 (PermissionDenied)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_room(self):
        """DELETE /api/v1/rooms/<pk> - 삭제 테스트 (소유자)"""
        # Room 생성
        room = models.Room.objects.create(
            name="To Delete",
            country="한국",
            city="서울",
            price=50000,
            rooms=2,
            toilets=1,
            description="Description",
            address="Address",
            kind=models.Room.RoomKindChoices.ENTIRE_PLACE,
            owner=self.user,
            category=self.category,
        )
        room_id = room.pk

        # API 호출
        response = self.client.delete(f"{self.base_url}{room_id}")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Room.objects.filter(pk=room_id).exists())

    def test_delete_room_not_owner(self):
        """DELETE /api/v1/rooms/<pk> - 소유자가 아닌 사용자 삭제 시 에러 테스트"""
        # 다른 사용자 생성
        other_user = User.objects.create_user(
            username="otheruser2",
            email="other2@example.com",
            password="testpass123"
        )
        
        # Room 생성 (다른 사용자 소유)
        room = models.Room.objects.create(
            name="Other User's Room 2",
            country="한국",
            city="서울",
            price=50000,
            rooms=2,
            toilets=1,
            description="Description",
            address="Address",
            kind=models.Room.RoomKindChoices.ENTIRE_PLACE,
            owner=other_user,
            category=self.category,
        )
        room_id = room.pk

        # API 호출
        response = self.client.delete(f"{self.base_url}{room_id}")

        # 검증 (PermissionDenied)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Room은 삭제되지 않아야 함
        self.assertTrue(models.Room.objects.filter(pk=room_id).exists())
