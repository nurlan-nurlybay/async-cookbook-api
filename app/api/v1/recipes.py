import structlog
from fastapi import APIRouter, status, Depends
from sqlmodel import select
from app.core.db import SessionDep
from app.models.recipe import Recipe, Ingredient
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeDetail, RecipeUpdate
from app.core.exceptions import NotFoundException
from app.core.security import get_admin_user

router = APIRouter()
logger = structlog.get_logger()

@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_recipe(recipe_in: RecipeCreate, session: SessionDep):
    logger.info("create_recipe_attempt", name=recipe_in.name)
    
    recipe_data = recipe_in.model_dump(exclude={"ingredients"})
    recipe = Recipe(**recipe_data)
    recipe.ingredients = [Ingredient(name=i.name) for i in recipe_in.ingredients]

    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    
    logger.info("recipe_created", recipe_id=recipe.id, ingredients_count=len(recipe.ingredients))
    return recipe


@router.get("/", response_model=list[RecipeRead])
async def get_recipes(session: SessionDep):
    from app.services.recipe_service import RecipeService
    return await RecipeService.get_all_sorted(session)


@router.get("/{recipe_id}", response_model=RecipeDetail)
async def get_recipe_detail(recipe_id: int, session: SessionDep):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        logger.warning("recipe_not_found", recipe_id=recipe_id)
        raise NotFoundException(detail="Recipe not found")

    logger.info("recipe_viewed", recipe_id=recipe_id, current_views=recipe.views + 1)

    recipe.views += 1 
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    return recipe


@router.patch("/{recipe_id}", response_model=RecipeRead, dependencies=[Depends(get_admin_user)])
async def update_recipe(recipe_id: int, recipe_in: RecipeUpdate, session: SessionDep):
    recipe = await session.get(Recipe, recipe_id)
    
    if not recipe:
        raise NotFoundException()

    update_data = recipe_in.model_dump(exclude_unset=True)
    if not update_data:
        return recipe

    # Business Rule - High traffic protection (Complexity +1)
    if recipe.views > 50:
        logger.info("updating_popular_recipe", recipe_id=recipe_id)

    for key, value in update_data.items():
        setattr(recipe, key, value)

    await session.commit()
    await session.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_admin_user)])
async def delete_recipe(recipe_id: int, session: SessionDep):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        logger.warning("delete_failed_not_found", recipe_id=recipe_id)
        raise NotFoundException()
    
    await session.delete(recipe)
    await session.commit()
    logger.info("recipe_deleted", recipe_id=recipe_id)
    return None
