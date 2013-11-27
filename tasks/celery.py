from __future__ import absolute_import
from celery import Celery
from celery.task import Task
from tasks.db import db_session, db_session_cba
from logbook import TimedRotatingFileHandler
import requests
import service_config
from tasks import celeryconfig

celery = Celery(include=service_config.CELERY_TASKS_LIST)
celery.config_from_object('tasks.celeryconfig')


log_handler = TimedRotatingFileHandler('Celery.log', date_format='%Y-%m-%d')
log_handler.push_application()

from logbook import Logger

logger = Logger('CeleryLog')






class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def __call__(self, *args, **kwargs):
        """In celery task this function call the run method, here you can
        set some environment variable before the run of the task"""
        logger.info("Starting to run")
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()



class SqlAlchemyTaskCBA(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session_cba.remove()


if __name__ == '__main__':
	celery.start()