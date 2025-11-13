from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category


class CategoryAPITestCase(TestCase):
    def setUp(self):
        """테스트 전에 실행되는 설정"""
        self.client = APIClient()
        self.base_url = "/api/v1/categories/"

    def test_get_categories_list(self):
        """GET /api/v1/categories/ - 목록 조회 테스트"""
        # Category 생성
        Category.objects.create(name="Test Category", kind=Category.CategoryKindChoices.ROOMS)

        # API 호출
        response = self.client.get(self.base_url)

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Category")

    def test_create_category(self):
        """POST /api/v1/categories/ - 생성 테스트"""
        data = {
            "name": "New Category",
            "kind": Category.CategoryKindChoices.ROOMS,
        }

        # API 호출
        response = self.client.post(self.base_url, data, format="json")

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.data["pk"], category.pk)

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
