from sqlmodel import SQLModel, Field
from typing import List
from app.models.recipe import RecipeBase
from typing import Optional


class IngredientCreate(SQLModel):
    name: str = Field(min_length=2, max_length=50)


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]


class IngredientRead(SQLModel):
    name: str


# For the list view (Requirement: Name, Views, Time)
class RecipeRead(RecipeBase):
    id: int
    views: int

# For the detail view (Requirement: + Description, + Ingredients)
class RecipeDetail(RecipeBase):
    id: int
    views: int
    ingredients: List[IngredientRead] = []


class RecipeUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, min_length=5, max_length=500)
    cooking_time: Optional[int] = Field(default=None, gt=0)
