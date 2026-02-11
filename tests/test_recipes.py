import pytest
from sqlmodel import select
from app.models.recipe import Recipe, Ingredient
from app.core.config import settings

@pytest.mark.asyncio
@pytest.mark.parametrize("name, cooking_time, expected_status", [
    ("Toast", 5, 201),             # Valid
    ("", 5, 422),                  # Invalid: Empty Name
    ("Slow Roast", -10, 422),      # Invalid: Negative Time
    ("Normal", "NaN", 422),        # Invalid: Type mismatch
])
async def test_create_recipe_parameterized(client, name, cooking_time, expected_status):
    response = await client.post("/recipes/", json={
        "name": name,
        "description": "Valid description required",
        "cooking_time": cooking_time,
        "ingredients": [{"name": "Bread"}]
    })

    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_recipe_security_and_lifecycle(client):
    payload = {
        "name": "Security Cake",
        "description": "Testing Auth",
        "cooking_time": 10,
        "ingredients": [{"name": "Flour"}]
    }

    # A. SECURITY: Missing Header (401)
    client.headers.pop("X-Admin-Key", None)
    unauth_res = await client.post("/recipes/", json=payload)
    
    # Assertion 2: Forbidden Status
    assert unauth_res.status_code == 401
    # Assertion 3: Error Detail Check
    assert unauth_res.json()["detail"] == "Admin privileges required"

    # B. SECURITY: Wrong Key (403)
    client.headers["X-Admin-Key"] = "wrong_password"
    wrong_res = await client.post("/recipes/", json=payload)
    
    # Assertion 4: Forbidden Status (Wrong Key)
    assert wrong_res.status_code == 401

    # Restore correct key
    client.headers["X-Admin-Key"] = str(settings.API_SECRET_KEY)

    # C. CREATE SUCCESS
    response = await client.post("/recipes/", json=payload)
    data = response.json()
    
    # Assertion 5-8: Response Data Integrity
    assert response.status_code == 201
    assert data["name"] == "Security Cake"
    assert "id" in data
    assert isinstance(data["id"], int)
    
    recipe_id = data["id"]

    # D. READ DETAIL
    get_res = await client.get(f"/recipes/{recipe_id}")
    get_data = get_res.json()
    
    # Assertion 9-11: Detail View
    assert get_res.status_code == 200
    assert get_data["description"] == "Testing Auth"
    assert len(get_data["ingredients"]) == 1

    # E. UPDATE (PATCH)
    patch_res = await client.patch(f"/recipes/{recipe_id}", json={"cooking_time": 99})
    patch_data = patch_res.json()

    # Assertion 33: Update Success
    assert patch_res.status_code == 200
    # Assertion 34: Field Updated
    assert patch_data["cooking_time"] == 99
    # Assertion 35: Other Fields Unchanged
    assert patch_data["name"] == "Security Cake"
    
    # F. VERIFY 404 (Not Found)
    # Try to delete a non-existent ID
    fail_del = await client.delete("/recipes/999999")
    
    # Assertion 36: Not Found Status
    assert fail_del.status_code == 404
    # Assertion 37: Error Message
    assert fail_del.json()["detail"] == "Resource not found"

    # G. VERIFY VALIDATION ON UPDATE
    fail_patch = await client.patch(f"/recipes/{recipe_id}", json={"cooking_time": -5})
    
    # Assertion 38: Validation Error Status
    assert fail_patch.status_code == 422
    # Assertion 39: Validation Error Type
    assert fail_patch.json()["detail"][0]["type"] == "greater_than"


@pytest.mark.asyncio
async def test_cascade_delete(client, async_session):
    """
    Verifies that deleting a Recipe also deletes its Ingredients.
    """
    # Create Recipe
    res = await client.post("/recipes/", json={
        "name": "Cascade Test",
        "description": "To be deleted",
        "cooking_time": 5,
        "ingredients": [{"name": "Orphan Ingredient"}]
    })
    recipe_id = res.json()["id"]

    # Verify Ingredient exists in DB directly
    statement = select(Ingredient).where(Ingredient.recipe_id == recipe_id)
    result = await async_session.execute(statement)
    ingredients = result.scalars().all()
    
    # Assertion 12: Pre-condition check
    assert len(ingredients) == 1

    # Delete Recipe
    del_res = await client.delete(f"/recipes/{recipe_id}")
    
    # Assertion 13: Delete Success
    assert del_res.status_code == 204

    # Verify Ingredient is GONE from DB
    result_after = await async_session.execute(statement)
    ingredients_after = result_after.scalars().all()
    
    # Assertion 14: Cascade Logic Verification
    assert len(ingredients_after) == 0
