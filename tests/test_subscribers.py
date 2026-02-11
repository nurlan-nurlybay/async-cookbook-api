import pytest

@pytest.mark.asyncio
async def test_subscriber_flow(client):
    email = "tester@example.com"
    
    # 1. SUBSCRIBE (Valid)
    response = await client.post("/subscribers/", json={"email": email})
    data = response.json()
    
    assert response.status_code == 201
    assert data["email"] == email

    # 2. DUPLICATE CHECK (Business Logic)
    dup_res = await client.post("/subscribers/", json={"email": email})
    assert dup_res.status_code == 409
    assert "already on the list" in dup_res.json()["detail"]

    # 3. UNSUBSCRIBE
    unsub_res = await client.delete(f"/subscribers/{email}")
    assert unsub_res.status_code == 204


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_email", [
    "not-an-email",       # Missing @
    "user@",              # Missing domain
    "@domain.com",        # Missing username
    "user@domain",        # Missing TLD 
    "",                   # Empty string
])
async def test_subscriber_validation_cases(client, invalid_email):
    """
    Requirement: Robust Validation.
    Tests that Pydantic rejects various malformed emails.
    """
    response = await client.post("/subscribers/", json={"email": invalid_email})
    
    # Assertion: Validation Error (422)
    assert response.status_code == 422
    
    # Assertion: Error Type Check
    # Pydantic returns specific error codes like 'value_error.email'
    error_type = response.json()["detail"][0]["type"]
    assert "value_error" in error_type or "missing" in error_type
