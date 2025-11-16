from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category
from users.models import User


class CategoryAPITestCase(APITestCase):
    def setUp(self):
        """테스트 전에 실행되는 설정"""
        # 테스트용 사용자 생성 및 인증
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.base_url = "/api/v1/categories/"

    def test_get_categories_list(self):
        """GET /api/v1/categories/ - 목록 조회 테스트"""
        # Category 생성
        Category.objects.create(name="Test Category", kind=Category.CategoryKindChoices.ROOMS)

        # API 호출
        response = self.client.get(self.base_url)

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 페이지네이션으로 인해 response.data는 dict 형태
        self.assertIn("results", response.data)
        results = response.data["results"]
        # 기존 카테고리가 있을 수 있으므로 새로 생성한 카테고리가 포함되어 있는지 확인
        category_names = [cat["name"] for cat in results]
        self.assertIn("Test Category", category_names)

    def test_create_category(self):
        """POST /api/v1/categories/ - 생성 테스트"""
        data = {
            "name": "New Category",
            "kind": Category.CategoryKindChoices.ROOMS,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertTrue(Category.objects.filter(name="New Category").exists())

    def test_get_category_detail(self):
        """GET /api/v1/categories/<pk> - 개별 조회 테스트"""
        # Category 생성
        category = Category.objects.create(
            name="Detail Category", kind=Category.CategoryKindChoices.ROOMS
        )

        # API 호출
        response = self.client.get(f"{self.base_url}{category.pk}")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Detail Category")
        self.assertEqual(response.data["kind"], Category.CategoryKindChoices.ROOMS)

    def test_update_category(self):
        """PUT /api/v1/categories/<pk> - 수정 테스트"""
        # Category 생성
        category = Category.objects.create(
            name="Original Name", kind=Category.CategoryKindChoices.ROOMS
        )

        # 수정 데이터
        data = {"name": "Updated Name"}

        # API 호출
        response = self.client.put(
            f"{self.base_url}{category.pk}", data, format="json"
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Name")
        category.refresh_from_db()
        self.assertEqual(category.name, "Updated Name")

    def test_delete_category(self):
        """DELETE /api/v1/categories/<pk> - 삭제 테스트"""
        # Category 생성
        category = Category.objects.create(
            name="To Delete", kind=Category.CategoryKindChoices.ROOMS
        )
        category_id = category.pk

        # API 호출
        response = self.client.delete(f"{self.base_url}{category_id}")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=category_id).exists())

    def test_category_not_found(self):
        """존재하지 않는 Category 조회 시 404 테스트"""
        # API 호출
        response = self.client.get(f"{self.base_url}999")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
