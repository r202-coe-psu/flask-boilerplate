import logging

import redis
from rq import Queue
from rq.job import Job

logger = logging.getLogger(__name__)


class RedisQueue:
    def __init__(self, redis_url=""):
        self.redis_url = redis_url
        if self.redis_url:
            self.init_app(self.redis_url)

    def init_app(self, redis_url):
        self.redis_url = redis_url
        self.conn = redis.from_url(redis_url)
        self.queue = Queue(connection=self.conn)

    def enqueue(self, func, *args, **kwargs) -> Job:
        return self.queue.enqueue(func, *args, **kwargs)

    def get_job(self, job_id):
        try:
            return Job.fetch(job_id, connection=self.conn)
        except Exception as e:
            logger.warning(f"cannot fetch job {job_id}: {e}")
        return None


redis_queue = RedisQueue()


def init_rq(app):
    redis_queue.init_app(app.config.get("REDIS_URL", "redis://localhost:6379"))
