from sqlmodel import select, col, Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recipe import Recipe

class RecipeService:
    @staticmethod
    async def get_all_sorted(session: AsyncSession):
        statement = select(Recipe).order_by(
            col(Recipe.views).desc(), 
            col(Recipe.cooking_time).asc()
        )
        result = await session.execute(statement)
        return result.scalars().all()

    @staticmethod
    def get_top_recipe_sync(session: Session):
        """Used by Celery (Sync)"""
        statement = select(Recipe).order_by(col(Recipe.views).desc()).limit(1)
        return session.exec(statement).first()
    