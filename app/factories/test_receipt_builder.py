from datetime import datetime
import unittest

from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem
from app.factories.receipt_builder import ReceiptBuilder


class TestReceiptBuilder(unittest.TestCase):
    def test_build(self):
        fixed_time = datetime(2024, 1, 1, 12, 30)
        expected = f"""
### Your purchase from {datetime.strftime(fixed_time, "%d.%m.%Y")}

| Article | Quantity | Unit Price | Total in CHF |
|--|--|--|--|
| Article 1 | 2 | 1.5 | 3.0 |
| Article 2 | 4 | 2.0 | 8.0 |
| Article 3 | 3 | 2.5 | 7.5 |
|**Total**|||**18.5**|

Paid at: {datetime.strftime(fixed_time, "%d.%m.%Y %H:%M")}
Thank you very much for your purchase!
"""

        receipt_items = [
            ReceiptItem("Article 1", 2, 1.5),
            ReceiptItem("Article 2", 4, 2.0),
            ReceiptItem("Article 3", 3, 2.5),
        ]
        receipt = Receipt(fixed_time, receipt_items)

        builder = ReceiptBuilder()
        result = builder.build(receipt)

        self.assertEqual(result, expected[1:-1])
