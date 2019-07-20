from celery.decorators import task
from celery.utils.log import get_task_logger

from snapshot.utils import upload

logger = get_task_logger(__name__)


@task(name="upload_task")
def upload_task(filename):
    """sends an snapshot to recognize it"""
    logger.info("Sent snapshot")
    return upload(filename)
