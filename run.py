#!flask/bin/python
from app.models.models import *
from app.models.gha.cts.models import *

from app.models.add_hoc_sql_runner import ScalarQuery, Query

from app import apimanager, app, db, api

def preprocessor(data):
    for i, img in enumerate(data['image_details']):
        data['image_details'][i]['imagedata'] = str(img['imagedata'])
        #json.dumps(data, use_decimal=True)
    return data




#apimanager.create_api(CTSBankDetail, url_prefix='/cts/api/v1.0', collection_name='bankdetail', methods=['GET', 'POST', 'DELETE', 'PUT'])

apimanager.create_api(BaseUser, url_prefix='/cts/api/v1.0', collection_name='user', methods=['GET', 'POST'])
apimanager.create_api(BaseLongProcesses, url_prefix='/cts/api/v1.0', collection_name='processes_status', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(BaseLongProcessTask, url_prefix='/cts/api/v1.0', collection_name='process_task_list', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(BaseMenus, url_prefix='/cts/api/v1.0', collection_name='menu', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(BaseUserGroup, url_prefix='/cts/api/v1.0', collection_name='usergroup', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(BaseTask, url_prefix='/cts/api/v1.0', collection_name='task', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(BaseUserGroupTask, url_prefix='/cts/api/v1.0', collection_name='user_task', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(BaseUser, url_prefix='/cts/api/v1.0', collection_name='user', methods=['GET', 'POST', 'PUT'], exclude_columns=['password'])
apimanager.create_api(BaseAuditLog, url_prefix='/cts/api/v1.0', collection_name='audit_log', methods=['GET', 'POST'])

api.add_resource(ScalarQuery, '/cts/api/v1.0/db_scala_service/<string:dbstring_code>', endpoint = 'sql_service')
api.add_resource(Query, '/cts/api/v1.0/db_query_service/<string:dbstring_code>', endpoint = 'sql_query_service')

#ghana cts specific tables.
#This will be ready and dynamically loaded

#TODO: find a way to load all models dynamically. This will reduce having to modify this run file

apimanager.create_api(CTSInwardCheque, url_prefix='/cts/api/v1.0', collection_name='inward', results_per_page=50, methods=['GET', 'POST', 'PUT'], allow_patch_many=True, preprocessors={'POST': [preprocessor]})
apimanager.create_api(CTSImageDetail, url_prefix='/cts/api/v1.0', collection_name='inward_image', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(CTSBankRoutingNo, url_prefix='/cts/api/v1.0', collection_name='bankroutingno', methods=['GET', 'POST'])
apimanager.create_api(CTSBranchRoutingNo, url_prefix='/cts/api/v1.0', collection_name='branchroutingno', methods=['GET', 'POST'])
apimanager.create_api(CTSOutwardCheque, url_prefix='/cts/api/v1.0', collection_name='outward', results_per_page=50, methods=['GET', 'POST', 'PATCH'], allow_patch_many=True)
apimanager.create_api(CTSRejectCodesDetails, url_prefix='/cts/api/v1.0', collection_name='rejectcodes', methods=['GET', 'POST', 'PUT'])
apimanager.create_api(CTSUploadedData, url_prefix='/cts/api/v1.0', collection_name='branch_upload', methods=['GET', 'POST', 'PUT'])





db.create_all()

app.run(debug = True, port=app.config.get('SERVER_PORT'))