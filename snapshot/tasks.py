from celery.decorators import task
from celery.utils.log import get_task_logger

from snapshot.utils import upload_image_and_recognize_license_plate

logger = get_task_logger(__name__)


@task(name="recognize_license_plate_task")
def recognize_license_plate_task(data):
    """sends an snapshot to recognize it"""
    logger.info("Sent snapshot")
    return upload_image_and_recognize_license_plate(data)
