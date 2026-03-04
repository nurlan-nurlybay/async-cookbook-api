import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.newsletter import send_weekly_email
from app.api.v1.recipes import update_recipe
from app.schemas.recipe import RecipeUpdate
from app.core.exceptions import NotFoundException

# --- TESTS FOR send_weekly_email (Newsletter Path Testing) ---

@pytest.mark.asyncio
async def test_send_weekly_email_all_paths(mocker):
    # PATH 1: No Recipe Found
    mocker.patch("app.services.recipe_service.RecipeService.get_top_recipe_sync", return_value=None)
    result = send_weekly_email()
    assert "No recipes found" in result

    # PATH 2: No Subscribers Found
    mocker.patch("app.services.recipe_service.RecipeService.get_top_recipe_sync", return_value=MagicMock(id=1, name="Pasta"))
    mock_session = MagicMock()
    mock_session.exec.return_value.all.return_value = [] 
    
    with patch("app.services.newsletter.Session", return_value=MagicMock(__enter__=lambda x: mock_session)):
        result = send_weekly_email()
        assert "Subscriber list is empty" in result

    # PATH 3: Success Path
    mock_sub = MagicMock(email="test@example.com")
    mock_session.exec.return_value.all.return_value = [mock_sub]
    with patch("app.services.newsletter.MailService", autospec=True):
        with patch("app.services.newsletter.Session", return_value=MagicMock(__enter__=lambda x: mock_session)):
            result = send_weekly_email()
            assert "Successfully sent" in result

    # PATH 4: Exception Handling
    mocker.patch("app.services.recipe_service.RecipeService.get_top_recipe_sync", side_effect=Exception("DB Fail"))
    with pytest.raises(Exception):
        send_weekly_email()


# --- TESTS FOR update_recipe (Recipe Update Path Testing) ---

@pytest.mark.asyncio
async def test_update_recipe_all_paths(mocker):
    # Use AsyncMock for the session to handle 'await session.get' and 'await session.commit'
    mock_session = AsyncMock()
    
    # PATH 1: 404 Not Found
    mock_session.get.return_value = None
    with pytest.raises(NotFoundException):
        await update_recipe(recipe_id=999, recipe_in=RecipeUpdate(), session=mock_session)

    # PATH 2: Early Return (Empty Update Data)
    mock_recipe = MagicMock(views=10)
    mock_session.get.return_value = mock_recipe
    result = await update_recipe(recipe_id=1, recipe_in=RecipeUpdate(), session=mock_session)
    assert result == mock_recipe

    # PATH 3: Popular Recipe Logic (Views > 50)
    mock_recipe.views = 60
    recipe_in = RecipeUpdate(name="Trending Pasta")
    await update_recipe(recipe_id=1, recipe_in=recipe_in, session=mock_session)
    assert mock_recipe.name == "Trending Pasta"

    # PATH 4: Standard Update (Views <= 50)
    mock_recipe.views = 5
    await update_recipe(recipe_id=1, recipe_in=RecipeUpdate(name="Regular Pasta"), session=mock_session)
    assert mock_session.commit.called


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exists, has_data, views, expected_exception, expected_commit",
    [
        (False, True, 0, NotFoundException, False),  # Case 1
        (True, False, 10, None, False),              # Case 2
        (True, True, 60, None, True),                # Case 3
        (True, True, 10, None, True),                # Case 4
    ]
)
async def test_update_recipe_table_logic(
    exists, has_data, views, expected_exception, expected_commit
):
    mock_session = AsyncMock()
    
    if not exists:
        mock_session.get.return_value = None
    else:
        mock_recipe = MagicMock(views=views)
        mock_session.get.return_value = mock_recipe

    update_data = RecipeUpdate(name="New Name") if has_data else RecipeUpdate()

    if expected_exception:
        with pytest.raises(expected_exception):
            await update_recipe(recipe_id=1, recipe_in=update_data, session=mock_session)
    else:
        result = await update_recipe(recipe_id=1, recipe_in=update_data, session=mock_session)
        assert mock_session.commit.called is expected_commit
        if not has_data:
            assert result == mock_session.get.return_value
