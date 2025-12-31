from datetime import datetime
import unittest

from app.db.db import DB
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_item_repo import CartItemRepo
from app.db.repos.cart_repo import CartRepo
from app.db.repos.category_repo import CategoryRepo
from app.models.article import Article
from app.models.cart_item import CartItem
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem
from app.services.checkout_service import CheckoutService


class TestCheckoutService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")

        self.category_repo = CategoryRepo(self.db)
        self.category_id = self.category_repo.create("Testcategory 1")
        assert self.category_id is not None

        self.article_repo = ArticleRepo(self.db, self.category_repo)

        self.article1_id = self.article_repo.create(
            "Testarticle 1", 2.0, self.category_id
        )
        self.article2_id = self.article_repo.create(
            "Testarticle 2", 3.0, self.category_id
        )
        self.article3_id = self.article_repo.create(
            "Testarticle 3 2", 4.0, self.category_id
        )
        assert self.article1_id is not None
        assert self.article2_id is not None
        assert self.article3_id is not None

        self.article1 = self.article_repo.get_one(self.article1_id)
        self.article2 = self.article_repo.get_one(self.article2_id)
        self.article3 = self.article_repo.get_one(self.article3_id)

        assert self.article1 is not None
        assert self.article2 is not None
        assert self.article3 is not None

        self.article1_model = Article(
            id=self.article1.id,
            name=self.article1.name,
            price=self.article1.price,
            category_id=self.article1.category_id,
        )

        self.article2_model = Article(
            id=self.article2.id,
            name=self.article2.name,
            price=self.article2.price,
            category_id=self.article2.category_id,
        )

        self.article3_model = Article(
            id=self.article3.id,
            name=self.article3.name,
            price=self.article3.price,
            category_id=self.article3.category_id,
        )

        self.cart_repo = CartRepo(self.db)
        self.cart_item_repo = CartItemRepo(self.db, self.cart_repo, self.article_repo)

        self.checkout_service = CheckoutService(
            self.article_repo, self.cart_repo, self.cart_item_repo
        )

    def tearDown(self) -> None:
        self.db.close()

    def test_search_article(self):
        articles = self.checkout_service.search_article("2")
        expected = [self.article2_model, self.article3_model]

        self.assertEqual(articles, expected)

    def test_add_article(self):
        assert self.article1 is not None

        quantity = 2
        added = self.checkout_service.add_article(self.article1, quantity)
        self.assertTrue(added)

        expected = CartItem(
            id=1,
            article_id=self.article1.id,
            cart_id=1,
            article_name=self.article1.name,
            unit_price=self.article1.price,
            quantity=quantity,
        )
        cart_item = self.cart_item_repo.get_one(1)
        assert cart_item is not None

        self.assertEqual(cart_item, expected)

    def test_add_existing_article(self):
        assert self.article1 is not None

        quantity = 2
        expected_quantity = 4

        added = self.checkout_service.add_article(self.article1, quantity)
        self.assertTrue(added)

        added_existing = self.checkout_service.add_article(
            self.article1_model, quantity
        )
        self.assertTrue(added_existing)

        expected = CartItem(
            id=1,
            article_id=self.article1.id,
            cart_id=1,
            article_name=self.article1.name,
            unit_price=self.article1.price,
            quantity=expected_quantity,
        )
        cart_item = self.cart_item_repo.get_one(1)
        assert cart_item is not None

        self.assertEqual(cart_item, expected)

    def test_add_article_negative(self):
        fake_article = Article(id=999, name="test", price=2.0, category_id=9999)

        added = self.checkout_service.add_article(fake_article, 2)
        self.assertFalse(added)

    def test_remove_article(self):
        assert self.article1 is not None

        quantity = 2
        added = self.checkout_service.add_article(self.article1, quantity)
        self.assertTrue(added)

        cart_item = self.cart_item_repo.get_one(1)
        assert cart_item is not None

        removed = self.checkout_service.remove_article(cart_item.id)
        self.assertTrue(removed)

        self.assertIsNone(self.cart_item_repo.get_one(1))

    def test_remove_article_negative(self):
        self.assertFalse(self.checkout_service.remove_article(999))

    def test_checkout(self):
        assert self.article1 is not None
        assert self.article2 is not None
        assert self.article3 is not None

        quantities = (1, 2, 3)

        self.checkout_service.add_article(self.article1, quantities[0])
        self.checkout_service.add_article(self.article2, quantities[1])
        self.checkout_service.add_article(self.article3, quantities[2])

        result = self.checkout_service.checkout()

        cart = self.cart_repo.get_one(1)
        assert cart is not None
        assert cart.paid_at is not None

        expected = Receipt(
            paid_at=cart.paid_at,
            items=[
                ReceiptItem(
                    article_name=self.article1.name,
                    quantity=quantities[0],
                    unit_price=self.article1.price,
                ),
                ReceiptItem(
                    article_name=self.article2.name,
                    quantity=quantities[1],
                    unit_price=self.article2.price,
                ),
                ReceiptItem(
                    article_name=self.article3.name,
                    quantity=quantities[2],
                    unit_price=self.article3.price,
                ),
            ],
        )

        self.assertEqual(result, expected)
