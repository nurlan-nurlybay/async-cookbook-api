import os
import sentry_sdk
import structlog
from celery import Celery
from celery.signals import setup_logging
from sqlmodel import Session, select
from sqlalchemy import create_engine

from app.core.config import settings
from app.services.mail import MailService
from app.models.subscriber import Subscriber
from app.services.recipe_service import RecipeService
from app.core.logging_conf import configure_structlog

# 1. Initialize Sentry (Worker Context)
if hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        traces_sample_rate=1.0,
    )

# 2. Configure Structlog via Signal
@setup_logging.connect
def config_loggers(*args, **kwargs):
    configure_structlog()

logger = structlog.get_logger()

# 3. Celery Instance
celery_app = Celery(
    "worker", 
    broker=str(settings.REDIS_URL), 
    backend=str(settings.REDIS_URL)
)

# 4. Sync Engine Setup
raw_url = str(settings.DATABASE_URL_DOCKER if os.getenv("DOCKER_ENV") else settings.DATABASE_URL)
sync_db_url = raw_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
engine = create_engine(sync_db_url)

@celery_app.task
def send_weekly_email():
    """
    Orchestrates the newsletter with structured logging.
    """
    log = logger.bind(task_name="send_weekly_email")
    log.info("task_started", status="fetching_data")

    try:
        with Session(engine) as session:
            recipe = RecipeService.get_top_recipe_sync(session)
            if not recipe:
                log.warning("task_cancelled", reason="no_recipes_found")
                return "Task cancelled: No recipes found."

            subscribers = session.exec(select(Subscriber)).all()
            emails = [s.email for s in subscribers]

            if not emails:
                log.warning("task_cancelled", reason="no_subscribers")
                return "Task cancelled: Subscriber list is empty."

            subject = f"Weekly Recommendation: {recipe.name}"
            body = f"Check out {recipe.name}! Cooking time: {recipe.cooking_time} mins."

            with MailService() as mailer:
                mailer.send_bulk(emails, subject, body)

            log.info("task_succeeded", recipient_count=len(emails), recipe_id=recipe.id)
            return f"Successfully sent newsletter to {len(emails)} subscribers."

    except Exception as e:
        log.error("task_failed", error=str(e))
        raise

# 5. Beat Schedule
celery_app.conf.update(
    beat_schedule={
        "send-every-minute-debug": {
            "task": "app.services.newsletter.send_weekly_email",
            "schedule": 60.0,
        },
    },
    timezone="UTC",
)
