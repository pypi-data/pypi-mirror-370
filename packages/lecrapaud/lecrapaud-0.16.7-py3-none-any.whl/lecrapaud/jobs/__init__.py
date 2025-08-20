from celery import Celery, signals
from lecrapaud.jobs import config
from lecrapaud.utils import setup_logger


@signals.setup_logging.connect
def configure_celery_logging(**kwargs):
    setup_logger()


app = Celery("src")
app.config_from_object(config)
app.autodiscover_tasks(["src.jobs"])
