import os
from sqlmodel import Session, create_engine
from app.models.recipe import Recipe, Ingredient
from app.models.subscriber import Subscriber
from app.core.config import settings

# Setup Sync Engine (Similar to Celery)
raw_url = str(settings.DATABASE_URL_DOCKER if os.getenv("DOCKER_ENV") else settings.DATABASE_URL)
sync_url = raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
engine = create_engine(sync_url)

def seed_data():
    with Session(engine) as session:
        # 1. Add a Recipe
        recipe = Recipe(
            name="Gordon's Beef Wellington", 
            description="The ultimate luxury dinner.", 
            cooking_time=120,
            views=10
        )
        recipe.ingredients = [
            Ingredient(name="Beef Fillet"),
            Ingredient(name="Puff Pastry")
        ]
        
        # 2. Add a Subscriber (Use your email to test the mailer!)
        sub = Subscriber(email="n.nurlibay32@gmail.com")
        
        session.add(recipe)
        session.add(sub)
        session.commit()
        print("✅ DB Seeded: 1 Recipe, 1 Subscriber added.")

if __name__ == "__main__":
    seed_data()
