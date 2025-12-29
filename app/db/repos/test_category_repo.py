import unittest

from app.db.db import DB
from app.db.repos.category_repo import CategoryRepo
from app.models.category import Category


class TestCategoryRepo(unittest.TestCase):
    def setUp(self) -> None:
        self.category_repo = CategoryRepo(DB(":memory:"))

    def test_create(self):
        result = self.category_repo.create("Testcategory")
        expected = 1
        self.assertEqual(result, expected)

    def test_get_one(self) -> None:
        self.category_repo.create("Testcategory 1")
        expected = Category(id=1, name="Testcategory 1")
        result = self.category_repo.get_one(1)
        self.assertEqual(result, expected)

    def test_get_all(self) -> None:
        self.category_repo.create("Testcategory 1")
        self.category_repo.create("Testcategory 2")
        expected = [
            Category(id=1, name="Testcategory 1"),
            Category(id=2, name="Testcategory 2"),
        ]
        result = self.category_repo.get_all()
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_update(self) -> None:
        category_id = self.category_repo.create("Testcategory 1")
        self.assertIsNotNone(category_id)

        category = Category(id=1, name="Testcategory updated")
        updated = self.category_repo.update(category)

        self.assertTrue(updated)

        updated_category = self.category_repo.get_one(1)
        self.assertEqual(updated_category, category)

    def test_delete(self) -> None:
        category_id = self.category_repo.create("Testcategory 1")
        self.assertIsNotNone(category_id)

        deleted = self.category_repo.delete(Category(id=1, name="Testcategory 1"))
        self.assertTrue(deleted)

        self.assertIsNone(self.category_repo.get_one(1))
