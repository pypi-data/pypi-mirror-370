from lecrapaud.jobs import app
from lecrapaud.utils import logger


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
)
def task_training_experiment(self):
    try:
        pass
    except Exception as e:
        logger.error(e)
        raise
