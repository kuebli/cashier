import unittest

from app.db.db import DB
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_item_repo import CartItemRepo
from app.db.repos.cart_repo import CartRepo
from app.db.repos.category_repo import CategoryRepo
from app.services.cart_service import CartService


class TestCartService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")
        self.cart_repo = CartRepo(self.db)

        self.category_repo = CategoryRepo(self.db)
        self.article_repo = ArticleRepo(self.db, self.category_repo)
        self.cart_item_repo = CartItemRepo(self.db, self.cart_repo, self.article_repo)

        self.category_id = self.category_repo.create("Testcategory")
        assert self.category_id is not None

        self.article1_id = self.article_repo.create("Article 1", 1.0, self.category_id)
        self.article2_id = self.article_repo.create("Article 2", 2.0, self.category_id)
        self.article3_id = self.article_repo.create("Article 3", 3.0, self.category_id)
        assert self.article1_id is not None
        assert self.article2_id is not None
        assert self.article3_id is not None

        self.article1 = self.article_repo.get_one(self.article1_id)
        self.article2 = self.article_repo.get_one(self.article2_id)
        self.article3 = self.article_repo.get_one(self.article3_id)
        assert self.article1 is not None
        assert self.article2 is not None
        assert self.article3 is not None

        self.cart1_id = self.cart_repo.create()
        self.cart2_id = self.cart_repo.create()
        assert self.cart1_id is not None
        assert self.cart2_id is not None

        self.cart1 = self.cart_repo.get_one(self.cart1_id)
        self.cart2 = self.cart_repo.get_one(self.cart2_id)
        assert self.cart1 is not None
        assert self.cart2 is not None

        self.cart_item1_id = self.cart_item_repo.create(self.cart1, self.article1, 1)
        self.cart_item2_id = self.cart_item_repo.create(self.cart1, self.article2, 2)
        self.cart_item3_id = self.cart_item_repo.create(self.cart2, self.article3, 3)
        assert self.cart_item1_id is not None
        assert self.cart_item2_id is not None
        assert self.cart_item3_id is not None

        self.cart_item1 = self.cart_item_repo.get_one(self.cart_item1_id)
        self.cart_item2 = self.cart_item_repo.get_one(self.cart_item2_id)

        self.cart_service = CartService(self.cart_repo, self.cart_item_repo)

    def tearDown(self) -> None:
        self.db.close()

    def test_get_carts(self):
        result = self.cart_service.get_carts()
        self.assertEqual(result, [self.cart1, self.cart2])

    def test_get_cart_items(self):
        assert self.cart1 is not None
        result = self.cart_service.get_cart_items(self.cart1.id)

        self.assertEqual(result, [self.cart_item1, self.cart_item2])

    def test_get_cart_items_negative(self):
        self.assertEqual(self.cart_service.get_cart_items(999), [])
