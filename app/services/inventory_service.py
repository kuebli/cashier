from typing import List, Optional
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.category_repo import CategoryRepo
from app.models.category import Category
from app.models.article import Article


class InventoryService:
    def __init__(self, category_repo: CategoryRepo, article_repo: ArticleRepo) -> None:
        self.category_repo = category_repo
        self.article_repo = article_repo

    def create_category(self, name: str) -> Optional[int]:
        return self.category_repo.create(name)

    def delete_category(self, category_id: int) -> bool:
        category = self.category_repo.get_one(category_id)
        if category is not None:
            return self.category_repo.delete(category)
        return False

    def get_categories(self) -> List[Category]:
        return self.category_repo.get_all()

    def create_article(
        self, name: str, price: float, category_id: int
    ) -> Optional[int]:
        return self.article_repo.create(name, price, category_id)

    def delete_article(self, article_id: int) -> bool:
        article = self.article_repo.get_one(article_id)
        if article is not None:
            return self.article_repo.delete(article)
        return False

    def get_articles(self, category_id: Optional[int] = None) -> List[Article]:
        return self.article_repo.get_all(category_id)
