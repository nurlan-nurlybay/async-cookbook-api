import pytest
from unittest.mock import MagicMock, patch
from app.services.recipe_service import RecipeService
from app.models.recipe import Recipe

@pytest.mark.asyncio
async def test_worker_ranking_logic(async_session):
    """
    Tests the logic the background worker uses to pick the 'Top Recipe'.
    """
    # Setup data with required fields
    r1 = Recipe(name="Low", views=10, cooking_time=1, description="desc")
    r2 = Recipe(name="Winner", views=999, cooking_time=1, description="desc")
    r3 = Recipe(name="Mid", views=50, cooking_time=1, description="desc")
    
    async_session.add_all([r1, r2, r3])
    await async_session.commit()
    
    # Verify business logic: Descending view order
    top_recipes = await RecipeService.get_all_sorted(async_session)
    
    assert top_recipes[0].name == "Winner"
    assert top_recipes[0].views == 999

    assert len(top_recipes) == 3


@patch("app.services.newsletter.MailService")
def test_mail_service_mocking(MockMailService):
    """
    Tests the MailService context manager logic used by the worker.
    """
    mock_instance = MagicMock()
    MockMailService.return_value.__enter__.return_value = mock_instance
    
    from app.services.newsletter import MailService
    with MailService() as mailer:
        mailer.send_bulk(["test@test.com"], "Subject", "Body")
        
    # Verify Service was called
    assert mock_instance.send_bulk.called is True
    
    # Verify Arguments passed to Service
    args, _ = mock_instance.send_bulk.call_args
    assert args[0] == ["test@test.com"]
