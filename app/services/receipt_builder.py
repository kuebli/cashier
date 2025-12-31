from datetime import datetime
from typing import List
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem


class ReceiptBuilder:
    def __build_header(self, paid_at: datetime) -> str:
        return f"### Your purchase from {paid_at.strftime('%d.%m.%Y')}\n\n"

    def __build_table_header(self) -> str:
        header = "| Article | Quantity | Unit Price | Total in CHF |\n"
        header += "|--|--|--|--|\n"
        return header

    def __build_table_body(self, items: List[ReceiptItem], total: float) -> str:
        body = ""
        for item in items:
            body += f"| {item.article_name} | {item.quantity} | {item.unit_price} | {item.line_total()} |\n"
        body += f"|**Total**|||**{total}**|\n\n"
        return body

    def __build_footer(self, paid_at: datetime) -> str:
        footer = f"Paid at: {paid_at.strftime('%d.%m.%Y %H:%M')}\n"
        footer += "Thank you very much for your purchase!"
        return footer

    def build(self, receipt: Receipt) -> str:
        md = ""
        md += self.__build_header(receipt.paid_at)
        md += self.__build_table_header()
        md += self.__build_table_body(receipt.items, receipt.total())
        md += self.__build_footer(receipt.paid_at)

        return md
