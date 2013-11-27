#!flask/bin/python
import json
import requests
import datetime
import utility.utility_functions as util_func

headers = {'Content-Type': 'application/json'}



def loadBaseLongProcessTask():

	inward_task_data = {'code': 'inward_file', 'status':'ACTIVE', 'process_type':'NORMAL', 'description': 'Ghana CTS Inward Cheque File Loading', 'expected_duration_seconds': 600000,
			'role_access': 'admin', 'country': 'GHA', 'task_module_name': 'tasks.gha.cts.inward_task', 'celery_task': 'processIncomingInwardFiles',
			'celery_task_kwargs': '''{'folder_name': '/Users/sundayamosun/git/newrepo/ctsservice/inward/', 'image_folder': '/Users/sundayamosun/git/newrepo/ctsservice/inward/',
			'image_backup_folder': '/Users/sundayamosun/git/newrepo/ctsservice/inward/image_backup/', 'xml_backup_folder': '/Users/sundayamosun/git/newrepo/ctsservice/inward/xml_backup/'}''', 'application': 'CTS'}

	util_func.sendPostRequest('http://localhost:5002/cts/api/v1.0/process_task_list', data)

def loadBaseLongProcesses():

    data = {'process_id': '1', 'start_time': str(datetime.datetime.now()),
            'submitted_by': 'admin', 'current_status': 'NEW', 'retry': 'N', 'attempt_count': 0, }

    util_func.sendPostRequest('http://localhost:5002/cts/api/v1.0/processes_status', data)
    


if __name__ == '__main__':
    #loadBaseLongProcessTask()
    loadBaseLongProcesses()
