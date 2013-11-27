#!flask/bin/python

'''
Created on Sep 07, 2013

@author: Amosun Sunday
'''
import requests
import service_config
import json
from logbook import Logger
from logbook import TimedRotatingFileHandler
import importlib
import utility.utility_functions as util_func
import ast
from multiprocessing import Pool

logger = Logger('ProcessControllerLogger')

log_handler = TimedRotatingFileHandler('ProcessController.log',  date_format='%Y-%m-%d')
log_handler.push_application()
headers = {'Content-Type': 'application/json'}
url_process = service_config.HTTP_LONG_PROCESS_REQUEST
url_process_task = service_config.HTTP_LONG_PROCESS_TASK_LIST_REQUEST
process_count = service_config.PROCESS_COUNT




def load_module(full_module_path):
    module = importlib.import_module(full_module_path)
    return module


def load_class(full_class_string):
    """
    dynamically load a class from a string
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)




def getPendingRequest():
    '''Get list of request that have not started running.
    We can also re-initiate requests that have failed if marked
    for re-initiation'''
    
    filters = [dict(name='current_status', op='eq', val='NEW')]
    response = util_func.sendGetRequest(url_process, filters)
    return response.json()['objects']

def getTaskList():
    '''Get list of request that have not started running.
    We can also re-initiate requests that have failed if marked
    for re-initiation'''
    
    filters = [dict(name='status', op='eq', val='ACTIVE')]
    response = util_func.sendGetRequest(url_process_task, filters)
    return response.json()['objects']

def updateRequest(status, process_id):
    ''''''
    data = {'current_status': status}
    util_func.sendPostRequest(url_process, data=json.dumps(data))






def getRequestTaskDetails(process_id):
    '''Get list of request that have not started running.
    We can also re-initiate requests that have failed if marked
    for re-initiation'''
    
    filters = [dict(name='process_id', op='eq', val=process_id)]
    params = dict(q=json.dumps(dict(filters=filters)))
    response = util_func.sendGetRequest(url_process_task, filters)
    return response.json()

def show_result(self, obj, task_id, time_out=None):

    if time_out:
        retval = getattr(obj, "AsyncResult")(task_id).get(timeout=time_out)
    else:
        retval = getattr(obj, "AsyncResult")(task_id).get()
    return repr(retval)

def executeTaskOnModule(pool, module_name, module_method, module_kwargs = None):
    if module_kwargs:
        pool.apply_async(getattr(module_name, module_method), args = (module_kwargs,), callback = celeryTaskCallback)
        #return (module_kwargs)
    else:
        pool.apply_async(getattr(module_name, module_method), args = (), callback = celeryTaskCallback)
        #return getattr(module_name, module_method)()


def executeTaskOnCelery(celery_module, celery_task, celery_task_kwargs = None, time_out=None):
    if celery_task_kwargs:
        cel_result = getattr(celery_module, celery_task)(celery_task_kwargs)
    elif celery_task_kwargs:
        cel_result = getattr(celery_module, celery_task)(celery_module, celery_task_kwargs)
    else:
        cel_result = getattr(celery_module, celery_task)()

    if time_out:
        result = show_result(getattr(celery_module, celery_task), cel_result.task_id, time_out)
    else:
        result = show_result(getattr(celery_module, celery_task), cel_result.task_id)


def celeryTaskCallback(result):
    '''Callback function for multi-processing. Update long processes status from here'''
    logger.info(result)
    retlist, process_running_id = result
    if process_running_id:
        process_task_data = {'current_status': 'COMPLETED', 'process_result': json.dumps(retlist)}
        process_update = util_func.sendPutRequest(service_config.HTTP_LONG_PROCESS_REQUEST + '/' + str(process_running_id), process_task_data)


def moduleTaskCallback(result):
    '''Callback function for multi-processing. Update long processes status from here'''
    logger.info(result)



def startSystem():
    pool = Pool(process_count)

    
    while 1:

        try:
            for task_detail in getTaskList():
                pending_reqs = task_detail['current_processes']
                celery_task_module = task_detail['task_module_name']
                celery_task_function = task_detail['celery_task']
                celery_task_kwargs = task_detail['celery_task_kwargs']
                expected_duration_seconds = task_detail['expected_duration_seconds'] #default value of 5
                #celery_class_module = load_module(celery_task_module)
                #celery_instance = celery_class_module()
                celery_module = load_module(celery_task_module)

                if expected_duration_seconds == '' or int(expected_duration_seconds) < 0:
                    expected_duration_seconds = 5

                for request in pending_reqs:
                    process_id = request['process_id']
                    if request['current_status'] == 'NEW': #or (request['current_status'] == 'FAILED' and request['retry'] == 'Y'):
                        if celery_task_kwargs != '':
                            task_kwargs = ast.literal_eval(str(celery_task_kwargs).replace('\\', ''))
                            logger.info(task_kwargs)
                            task_kwargs['time_out'] = expected_duration_seconds
                            task_kwargs['process_id'] = process_id
                            task_kwargs['process_running_id'] = request['process_running_id']

                            if str(task_detail[str('process_type')]) == 'NORMAL':
                                #pool.apply_async(executeTaskOnModule, args = (celery_module, celery_task_function, task_kwargs,), callback = celeryTaskCallback)
                                result = executeTaskOnModule(pool, celery_module, celery_task_function, task_kwargs)
                            elif str(task_detail[str('process_type')]) == 'CELERY':
                                #pool.apply_async(executeTaskOnCelery, args = (celery_module, celery_task_function, task_kwargs, expected_duration_seconds,), callback = celeryTaskCallback)
                                result = executeTaskOnCelery(celery_module, celery_task_function, task_kwargs, expected_duration_seconds)

                            process_task_data = {'current_status': 'STARTED'}
                            process_update = util_func.sendPutRequest(service_config.HTTP_LONG_PROCESS_REQUEST + '/' + str(task_kwargs['process_running_id']), process_task_data)
                        else:
                            #pool.apply_async(executeTaskOnModule, args = (celery_module, celery_task_function, expected_duration_seconds,), callback = celeryTaskCallback)
                            result = executeTaskOnModule(celery_module, celery_task_function, time_out=expected_duration_seconds)

                pool.close()
                pool.join()

        except Exception, e:
            logger.error(e)



if __name__ == '__main__':

    try:
        startSystem()
    except Exception, e:
        print e
    #cProfile.run('startSystem()')


