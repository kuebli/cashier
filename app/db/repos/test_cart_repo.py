import unittest

from app.db.db import DB
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_repo import CartRepo
from app.db.repos.category_repo import CategoryRepo
from app.models.cart import Cart


class TestCartRepo(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")
        self.category_repo = CategoryRepo(self.db)
        self.article_repo = ArticleRepo(self.db, self.category_repo)
        self.cart_repo = CartRepo(self.db, self.article_repo)

        self.category_id = self.category_repo.create("Testcategory")
        assert self.category_id is not None

        self.article1_id = self.article_repo.create(
            "Testarticle1", 1.50, self.category_id
        )
        self.article2_id = self.article_repo.create(
            "Testarticle2", 1.80, self.category_id
        )

    def test_create(self):
        cart_id = self.cart_repo.create()
        self.assertEqual(cart_id, 1)

    def test_get_one(self):
        cart_id = self.cart_repo.create()
        assert cart_id is not None

        cart = self.cart_repo.get_one(cart_id)
        expected = Cart(id=1, total=0.0, paid=False, articles=[])

        self.assertEqual(cart, expected)

    def test_get_one_negative(self):
        self.assertIsNone(self.cart_repo.get_one(99))

    def test_get_all(self):
        cart1_id = self.cart_repo.create()
        cart2_id = self.cart_repo.create()

        assert cart1_id is not None
        assert cart2_id is not None

        cart = self.cart_repo.get_all()
        expected = [
            Cart(id=1, total=0.0, paid=False, articles=[]),
            Cart(id=2, total=0.0, paid=False, articles=[]),
        ]

        self.assertEqual(cart, expected)

    def test_get_all_empty(self):
        self.assertEqual(self.cart_repo.get_all(), [])

    def test_update(self):
        cart_id = self.cart_repo.create()
        assert cart_id is not None

        cart = self.cart_repo.get_one(cart_id)
        assert cart is not None

        cart.total = 10.0
        cart.paid = True

        updated = self.cart_repo.update(cart)
        self.assertTrue(updated)

        cart_updated = self.cart_repo.get_one(cart_id)
        expected = Cart(id=1, total=10.0, paid=True, articles=[])

        self.assertEqual(cart_updated, expected)

    def test_delete(self):
        cart_id = self.cart_repo.create()
        assert cart_id is not None

        cart = self.cart_repo.get_one(cart_id)
        assert cart is not None

        deleted = self.cart_repo.delete(cart)
        self.assertTrue(deleted)

        self.assertIsNone(self.cart_repo.get_one(cart.id))
