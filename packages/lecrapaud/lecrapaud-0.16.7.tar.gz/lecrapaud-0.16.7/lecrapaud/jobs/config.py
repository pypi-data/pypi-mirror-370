from lecrapaud.config import REDIS_URL

REDIS_URL = REDIS_URL + "/1"
broker_url = REDIS_URL
result_backend = REDIS_URL

# For RedBeat
redbeat_redis_url = REDIS_URL
beat_scheduler = "redbeat.RedBeatScheduler"

timezone = "UTC"

task_acks_late = True
task_reject_on_worker_lost = True
worker_prefetch_multiplier = 1
task_acks_on_failure_or_timeout = False
worker_concurrency = 1
