from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

# if TYPE_CHECKING:
#     from app.models.subscriber import Subscriber  # Avoid circular imports


# 1. Base Class (Shared Fields)
class RecipeBase(SQLModel):
    name: str = Field(index=True, min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=500)
    cooking_time: int = Field(gt=0)  # Minutes


# 2. Table Model (For Database)
class Recipe(RecipeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    views: int = Field(default=0)

    ingredients: list["Ingredient"] = Relationship(
        back_populates="recipe", sa_relationship_kwargs={"lazy": "selectin"}
    )


# 3. Ingredient Table
class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=50)

    # FIX: Make recipe_id Optional.
    # SQLModel will auto-fill this when we add it to the Recipe.ingredients list.
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id")

    recipe: Recipe = Relationship(back_populates="ingredients")
