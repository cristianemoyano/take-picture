from celery.decorators import task
from celery.utils.log import get_task_logger

from snapshot.utils import upload, upload_image_and_recognize_license_place

logger = get_task_logger(__name__)


@task(name="upload_task")
def upload_task(filename):
    """sends an snapshot to recognize it"""
    logger.info("Sent snapshot")
    return upload(filename)


@task(name="recognize_license_place_task")
def recognize_license_place_task(data):
    """sends an snapshot to recognize it"""
    logger.info("Sent snapshot")
    return upload_image_and_recognize_license_place(data)
