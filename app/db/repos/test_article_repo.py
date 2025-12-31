import unittest

from app.db.db import DB
from app.models.article import Article
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.category_repo import CategoryRepo


class TestArticleRepo(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")
        self.category_repo = CategoryRepo(self.db)
        self.category_id = self.category_repo.create("Testcategory")
        self.article_repo = ArticleRepo(self.db, self.category_repo)

    def tearDown(self) -> None:
        self.db.close()

    def test_create(self):
        assert self.category_id is not None
        article_id = self.article_repo.create("Testarticle", 1.5, self.category_id)
        self.assertEqual(article_id, 1)

    def test_get_one(self):
        assert self.category_id is not None
        article_id = self.article_repo.create("Testarticle", 1.5, self.category_id)
        assert article_id is not None
        result = self.article_repo.get_one(article_id)
        expected = Article(
            id=article_id, name="Testarticle", price=1.5, category_id=self.category_id
        )
        self.assertEqual(result, expected)

    def test_get_one_negative(self):
        self.assertIsNone(self.article_repo.get_one(99))

    def test_get_all_without_category(self):
        assert self.category_id is not None
        self.article_repo.create("Testarticle 1", 1.50, self.category_id)
        self.article_repo.create("Testarticle 2", 1.80, self.category_id)
        articles = self.article_repo.get_all()
        expected = [
            Article(
                id=1, name="Testarticle 1", price=1.50, category_id=self.category_id
            ),
            Article(
                id=2, name="Testarticle 2", price=1.80, category_id=self.category_id
            ),
        ]
        self.assertEqual(articles, expected)

    def test_get_all_with_category(self):
        category_2 = self.category_repo.create("Testcategory 2")

        assert self.category_id is not None
        assert category_2 is not None

        self.article_repo.create("Testarticle 1", 1.50, self.category_id)
        self.article_repo.create("Testarticle 2", 1.80, self.category_id)
        self.article_repo.create("Testarticle 3", 1.80, category_2)
        self.article_repo.create("Testarticle 4", 1.90, category_2)

        articles = self.article_repo.get_all(category_id=category_2)

        expected = [
            Article(id=3, name="Testarticle 3", price=1.80, category_id=category_2),
            Article(id=4, name="Testarticle 4", price=1.90, category_id=category_2),
        ]

        self.assertEqual(articles, expected)

    def test_get_all_with_search_text(self):
        assert self.category_id is not None

        self.article_repo.create("Testarticle 1", 1.50, self.category_id)
        self.article_repo.create("Testarticle 2", 1.80, self.category_id)

        articles = self.article_repo.get_all(search_text="1")
        expected = [
            Article(
                id=1, name="Testarticle 1", price=1.50, category_id=self.category_id
            ),
        ]

        self.assertEqual(articles, expected)

    def test_update(self):
        assert self.category_id is not None

        article_id = self.article_repo.create("Testarticle", 1.45, self.category_id)
        assert article_id is not None

        article = self.article_repo.get_one(article_id)
        assert article is not None

        article.name = "Testarticle 2"
        article.price = 2.05
        updated = self.article_repo.update(article)
        assert updated is True

        article_updated = self.article_repo.get_one(article_id)
        assert article_updated is not None
        expected = Article(
            id=1, name="Testarticle 2", price=2.05, category_id=self.category_id
        )
        self.assertEqual(article_updated, expected)

    def test_delete(self):
        assert self.category_id is not None

        article_id = self.article_repo.create("Testarticle", 1.45, self.category_id)
        assert article_id is not None

        article = self.article_repo.get_one(article_id)
        assert article is not None

        deleted = self.article_repo.delete(article)
        assert deleted is True

        self.assertIsNone(self.article_repo.get_one(article_id))
