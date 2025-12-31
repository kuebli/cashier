import unittest

from app.db.db import DB
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_item_repo import CartItemRepo
from app.db.repos.cart_repo import CartRepo
from app.db.repos.category_repo import CategoryRepo
from app.models.cart_item import CartItem


class TestCartItemRepo(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")
        self.category_repo = CategoryRepo(self.db)
        self.article_repo = ArticleRepo(self.db, self.category_repo)
        self.cart_repo = CartRepo(self.db)
        self.cart_item_repo = CartItemRepo(self.db, self.cart_repo, self.article_repo)

        self.category_id = self.category_repo.create("Testcategory")
        assert self.category_id is not None

        self.article1_id = self.article_repo.create("Article 1", 1.5, self.category_id)
        self.article2_id = self.article_repo.create("Article 2", 2.0, self.category_id)

        assert self.article1_id is not None
        assert self.article2_id is not None

        self.article1 = self.article_repo.get_one(self.article1_id)
        self.article2 = self.article_repo.get_one(self.article2_id)

        self.cart_id1 = self.cart_repo.create()
        self.cart_id2 = self.cart_repo.create()
        assert self.cart_id1 is not None
        assert self.cart_id2 is not None

        self.cart1 = self.cart_repo.get_one(self.cart_id1)
        self.cart2 = self.cart_repo.get_one(self.cart_id2)

    def tearDown(self) -> None:
        self.db.close()

    def test_create(self):
        assert self.cart1 is not None
        assert self.article1 is not None

        cart_item_id = self.cart_item_repo.create(self.cart1, self.article1, 2)
        self.assertEqual(cart_item_id, 1)

    def test_get_one(self):
        assert self.cart1 is not None
        assert self.article1 is not None

        cart_item_id = self.cart_item_repo.create(self.cart1, self.article1, 2)
        assert cart_item_id is not None

        cart = self.cart_item_repo.get_one(cart_item_id)
        expected = CartItem(
            id=1,
            article_id=self.article1.id,
            cart_id=self.cart1.id,
            quantity=2,
            article_name=self.article1.name,
            unit_price=1.5,
        )

        self.assertEqual(cart, expected)

    def test_get_one_negative(self):
        self.assertIsNone(self.cart_item_repo.get_one(99))

    def test_get_all_no_category(self):
        assert self.cart1 is not None
        assert self.cart2 is not None
        assert self.article1 is not None
        assert self.article2 is not None

        cart1_item1_id = self.cart_item_repo.create(self.cart1, self.article1, 2)
        cart1_item2_id = self.cart_item_repo.create(self.cart1, self.article2, 4)
        cart2_item1_id = self.cart_item_repo.create(self.cart2, self.article1, 2)

        assert cart1_item1_id is not None
        assert cart1_item2_id is not None
        assert cart2_item1_id is not None

        cart_items = self.cart_item_repo.get_all()
        expected = [
            CartItem(
                id=1,
                article_id=self.article1.id,
                cart_id=self.cart1.id,
                quantity=2,
                article_name=self.article1.name,
                unit_price=self.article1.price,
            ),
            CartItem(
                id=2,
                article_id=self.article2.id,
                cart_id=self.cart1.id,
                quantity=4,
                article_name=self.article2.name,
                unit_price=self.article2.price,
            ),
            CartItem(
                id=3,
                article_id=self.article1.id,
                cart_id=self.cart2.id,
                quantity=2,
                article_name=self.article1.name,
                unit_price=self.article1.price,
            ),
        ]

        self.assertEqual(cart_items, expected)

    def test_get_all_with_category(self):
        assert self.cart1 is not None
        assert self.cart2 is not None
        assert self.article1 is not None
        assert self.article2 is not None

        cart1_item1_id = self.cart_item_repo.create(self.cart1, self.article1, 2)
        cart1_item2_id = self.cart_item_repo.create(self.cart1, self.article2, 4)
        cart2_item1_id = self.cart_item_repo.create(self.cart2, self.article1, 2)

        assert cart1_item1_id is not None
        assert cart1_item2_id is not None
        assert cart2_item1_id is not None

        cart_items = self.cart_item_repo.get_all(self.cart1)

        expected = [
            CartItem(
                id=1,
                article_id=self.article1.id,
                cart_id=self.cart1.id,
                quantity=2,
                article_name=self.article1.name,
                unit_price=self.article1.price,
            ),
            CartItem(
                id=2,
                article_id=self.article2.id,
                cart_id=self.cart1.id,
                quantity=4,
                article_name=self.article2.name,
                unit_price=self.article2.price,
            ),
        ]

        self.assertEqual(cart_items, expected)

    def test_get_all_negative(self):
        self.assertEqual(self.cart_item_repo.get_all(), [])

    def test_update(self):
        assert self.cart1 is not None
        assert self.article1 is not None

        cart_item_id = self.cart_item_repo.create(self.cart1, self.article1, 2)
        assert cart_item_id is not None

        cart = self.cart_item_repo.get_one(cart_item_id)
        assert cart is not None

        cart.quantity = 9
        cart.unit_price = 3

        updated = self.cart_item_repo.update(cart)
        self.assertTrue(updated)

        cart_updated = self.cart_item_repo.get_one(cart.id)
        expexted = CartItem(
            id=1,
            article_id=self.article1.id,
            cart_id=self.cart1.id,
            quantity=9,
            article_name=self.article1.name,
            unit_price=3,
        )

        self.assertEqual(cart_updated, expexted)

    def test_delete(self):
        assert self.cart1 is not None
        assert self.article1 is not None

        cart_item_id = self.cart_item_repo.create(self.cart1, self.article1, 2)
        assert cart_item_id is not None

        cart = self.cart_item_repo.get_one(cart_item_id)
        assert cart is not None

        deleted = self.cart_item_repo.delete(cart)
        self.assertTrue(deleted)

        self.assertIsNone(self.cart_item_repo.get_one(cart.id))
