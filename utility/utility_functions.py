import requests
import json
import shutil

headers = {'Content-Type': 'application/json'}


def getPendingRequest(url, filter, param):
    response = requests.get(url, params=param, headers=headers)
    return response.json()['objects']

def sendGetRequest(url, filters=None, page_tofetch = None):
    '''Fetch data from the server'''
    if page_tofetch:
        url = url + '?page=' + page_tofetch
    if filters:
        params = dict(q=json.dumps(dict(filters=filters)))
        response = requests.get(url, params=params, headers=headers)
    else:
        response = requests.get(url, headers=headers)      

    return response



def getScalaValue(url, db_string_code):
    '''Use this function to get FileID, ItemCount etc.'''
    output =""
    try:
        response = sendGetRequest(url + db_string_code)

    except Exception, e:
        logger.error(e)

    return response['result']

def runStoreSql



def sendPostRequest(url, data, param=None):
    '''Call Post to save new data'''
    
    if param:
        response = requests.post(url, data=json.dumps(data), params=param, headers=headers)
    elif param is None:
        response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json(), response.status_code


def sendPutRequest(url, data, param=None):
    '''Call Update to save new data'''

    if param:
        response = requests.put(url, data=json.dumps(data), params=param, headers=headers)
    elif param is None:
        response = requests.put(url, data=json.dumps(data), headers=headers)
    return response.json(), response.status_code

def sendPatchRequest(url, data, param=None):
    '''Call Post to save new data'''

    if param:
        response = requests.patch(url, data=json.dumps(data), params=param, headers=headers)
    elif param is None:
        response = requests.patch(url, data=json.dumps(data), headers=headers)
    return response.json(), response.status_code

def getValueFromDict(param_dict, field):
    if field in param_dict:
        return param_dict[field]
    else:
        return None

def extractValueFromXml2Dict(dict_to_parse):
    '''Get the dictionary value from XML2Dict dictionary'''
    retdict = dict()
    for (k, v) in dict_to_parse.iteritems():
        if 'value' in v:
            retdict[k] = v['value']
        if type(v) is dict and 'value' not in v:
            retdict[k] = extractValueFromXml2Dict(v)

    return retdict


def moveFileToBackUp(folder_name, xml_backup_dir, file_name, date_created):

    try:

        currbackupdir = xml_backup_dir +  date_created
        if not os.path.exists(currbackupdir):
            os.makedirs(currbackupdir)
        shutil.move(folder_name + file_name, currbackupdir + '/' + str(file_name))
    except Exception, e:
        logger.error(e)
