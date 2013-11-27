import time
from tasks.celery import celery
from tasks.celery import SqlAlchemyTaskCBA


#from ctstasks.celery import logger


@celery.task(name="ctstasks.cba_task.checkfund", base=SqlAlchemyTaskCBA)
def checkfund(account):
    time.sleep(2)
    return ['']





@celery.task(name="ctstasks.cba_task.confirmcustomer", base=SqlAlchemyTaskCBA)
def confirmcustomer(customer_id):
    time.sleep(2)
    return ['']

@celery.task(name="ctstasks.cba_task.checkaccountbalance", base=SqlAlchemyTaskCBA)
def checkaccountbalance(customer_acct_no):
    time.sleep(2)
    return ['']


@celery.task(name="ctstasks.cba_task.checkstoppedcheque", base=SqlAlchemyTaskCBA)
def checkstoppedcheque(account_no, chequeno):
    time.sleep(2)
    return ['']