import unittest

from app.db.db import DB
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.category_repo import CategoryRepo
from app.models.article import Article
from app.models.category import Category
from app.services.inventory_service import InventoryService


class TestInventoryService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")
        self.category_repo = CategoryRepo(self.db)
        self.article_repo = ArticleRepo(self.db, self.category_repo)

        self.inventory_service = InventoryService(self.category_repo, self.article_repo)

    def tearDown(self) -> None:
        self.db.close()

    def test_create_category(self):
        category_id = self.inventory_service.create_category("Testcategory")
        assert category_id is not None
        self.assertIsNotNone(category_id)

        category = self.category_repo.get_one(category_id)
        expected = Category(id=1, name="Testcategory")

        self.assertEqual(category, expected)

    def test_delete_category(self):
        category_id = self.inventory_service.create_category("Testcategory")
        assert category_id is not None
        self.assertIsNotNone(category_id)

        deleted = self.inventory_service.delete_category(category_id)
        self.assertTrue(deleted)

        self.assertIsNone(self.category_repo.get_one(category_id))

    def test_get_categories(self):
        category1_id = self.inventory_service.create_category("Testcategory 1")
        category2_id = self.inventory_service.create_category("Testcategory 2")
        assert category1_id is not None
        assert category2_id is not None
        self.assertIsNotNone(category1_id)
        self.assertIsNotNone(category2_id)

        categories = self.inventory_service.get_categories()

        expected = [
            Category(id=1, name="Testcategory 1"),
            Category(id=2, name="Testcategory 2"),
        ]

        self.assertEqual(categories, expected)

    def test_create_article(self):
        category_id = self.inventory_service.create_category("Testcategory")
        assert category_id is not None
        self.assertIsNotNone(category_id)

        article_id = self.inventory_service.create_article(
            "Testarticle 1", 2.0, category_id
        )
        assert article_id is not None
        self.assertIsNotNone(article_id)

        article = self.article_repo.get_one(article_id)
        expected = Article(
            id=1, name="Testarticle 1", price=2.0, category_id=category_id
        )

        self.assertEqual(article, expected)

    def test_delete_article(self):
        category_id = self.inventory_service.create_category("Testcategory")
        assert category_id is not None
        self.assertIsNotNone(category_id)

        article_id = self.inventory_service.create_article(
            "Testarticle 1", 2.0, category_id
        )
        assert article_id is not None
        self.assertIsNotNone(article_id)

        deleted = self.inventory_service.delete_article(article_id)
        self.assertTrue(deleted)

        self.assertIsNone(self.article_repo.get_one(article_id))

    def test_get_articles_without_category(self):
        category_id = self.inventory_service.create_category("Testcategory")
        assert category_id is not None
        self.assertIsNotNone(category_id)

        self.inventory_service.create_article("Testarticle 1", 2.0, category_id)
        self.inventory_service.create_article("Testarticle 2", 5.0, category_id)
        self.inventory_service.create_article("Testarticle 3", 4.0, category_id)

        articles = self.inventory_service.get_articles()
        expected = [
            Article(id=1, name="Testarticle 1", price=2.0, category_id=category_id),
            Article(id=2, name="Testarticle 2", price=5.0, category_id=category_id),
            Article(id=3, name="Testarticle 3", price=4.0, category_id=category_id),
        ]

        self.assertEqual(articles, expected)

    def test_get_articles_with_category(self):
        category1_id = self.inventory_service.create_category("Testcategory 1")
        category2_id = self.inventory_service.create_category("Testcategory 2")
        assert category1_id is not None
        assert category2_id is not None
        self.assertIsNotNone(category1_id)
        self.assertIsNotNone(category2_id)

        self.inventory_service.create_article("Testarticle 1", 2.0, category1_id)
        self.inventory_service.create_article("Testarticle 2", 5.0, category2_id)
        self.inventory_service.create_article("Testarticle 3", 4.0, category2_id)

        articles = self.inventory_service.get_articles(category2_id)
        expected = [
            Article(id=2, name="Testarticle 2", price=5.0, category_id=category2_id),
            Article(id=3, name="Testarticle 3", price=4.0, category_id=category2_id),
        ]

        self.assertEqual(articles, expected)
