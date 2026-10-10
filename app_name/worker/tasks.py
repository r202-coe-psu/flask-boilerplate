"""Background jobs executed by the RQ worker.

Enqueue from a view with:

    from app_name.web.redis_rq import redis_queue
    from app_name.worker import tasks

    job = redis_queue.enqueue(tasks.example_task, str(current_user.id))
"""

import logging

from app_name import models

logger = logging.getLogger(__name__)


def example_task(user_id: str):
    user = models.User.objects.with_id(user_id)
    logger.info(f"running example task for {user.username if user else user_id}")
    return {"user_id": user_id}
