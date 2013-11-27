import time
from tasks.celery import celery
from tasks.celery import SqlAlchemyTask
from tasks.celery import log_handler
import utility.XMLRequestParser as xmlparser
import service_config
import utility.utility_functions as util_func

def generateOutwardFiles(kwargs):
    '''Main entry function for the processhandler.
    Read through all of the parameter arguments and initialize the default parameters
    Read through all of the parameter arguments and initialize the default parameters'''

    date_created = kwargs.get('date_created', '')
    process_id = kwargs.get('process_running_id', '')
    item_per_file = kwargs.get('item_per_file', 1) #Make 1 to escape divison by zero error.
    route_no = kwargs.get('route_no', '')
    versionNumber = kwargs.get('versionNumber', '')
    testFileIndicator = kwargs.get('testFileIndicator', '')
    out_file_backup_dir = kwargs.get('outFileBackUpDir', '')
    outfile_date = kwargs.get('outFileDate', '')
    out_file_dir = kwargs.get('outfiledir', '')


    retlist = []
    file_header = dict('VersionNumber': versionNumber, 'TestFileIndicator': testFileIndicator)
    try:
        totalItemCount = fetchOutwardItems(outfile_date)[0]#util_func.getScalaValue(service_config.HTTP_SEQUENCE_REQUEST, 'CTS_OUTWARDITEM_COUNT')

        res = group(executeFileGeneration.subtask((file_header, file_bundle_count, out_file_dir, out_file_backup_dir, outfile_date)) for file_bundle_count in range(abs(len(totalItemCount) / item_per_file))).apply_async()

        retlist = res.get()
    except Exception, e:
        logger.error(e)
    return retlist, process_id


def fetchOutwardItems(date_created, page_tofetch = None):
    '''Fetch all outward items for the day.
    If page_to_fetch how many record to fetch for this request.'''
    #date_created = date_created, status = 'ACTIVE', acct_status = 'VALID', auth_status = 'Y'
    filters = [dict(name='date_created', op='eq', val=date_created), dict(name='status', op='eq', val='ACTIVE'), dict(name='acct_status', op='eq', val='VALID'),
                dict(name='auth_status', op='eq', val='Y')]
    params = dict(q=json.dumps(dict(filters=filters)))

    if page_tofetch:
        response = util_func.sendGetRequest(service_config.HTTP_OUTWARD_ITEMS, filters)
    else:
        response = util_func.sendGetRequest(service_config.HTTP_OUTWARD_ITEMS, filters, page_tofetch)
    
    return response.json()['objects'], response.json()['num_results'], response.json()['total_pages']

def updateItemsGenerated(item_list, filename, file_id, status = 'PROCESSED', item_status = 'PROCESSED'):
    
    '''Update Outward Items. Build filter list from the list of items.'''

    filter_list = [dict(name='itemseqno', op='eq', val=item['itemseqno']) for item in item_list]
    #for item in item_list:
    data = {'status': status, 'item_status': item_status, 'filename': filename, 'upload_fileid': file_id}
    response = util_func.sendPutRequest(service_config.HTTP_OUTWARD_ITEMS, data, param = filter_list)



@celery.task(name="tasks.gha.cts.OutwardTasks.executeFileGeneration", base=SqlAlchemyTask)
def executeFileGeneration(file_header, file_bundle_count, routeno, fileid, out_file_dir, out_file_backup_dir, outfile_date):
    '''Do the file generation.
    Update each item that the item was generated for.
    Move the file to the backup folder.'''

    try:
        list_to_file, rec_length = fetchOutwardItems(outfile_date, file_bundle_count)[0]
        file_footer = dict()
        file_header['FileID'] = util_func.getScalaValue(service_config.HTTP_SEQUENCE_REQUEST, 'CTS_SEQ_OUTFILE_ID')#getNextFileID()
        file_footer['TotalItemCount'] = len(list_to_file)
        file_footer['TotalAmount'] = getItemAmountTotal(list_to_file)
        filename, filename_done, imgfilename, imgfilename_done = xmlparser.buildCTSXml(file_header, list_to_file, file_footer, routeno, file_header['FileID'])#listofitems, routno_brn,  userid,  fileID = None, status = None

        updateItemsGenerated(list_to_file, filename, file_header['FileID'])
        #logic.saveInItemCollection(list_to_file, routeno, '', fileID = fileid, status = 'PROCESSED', action = 'save', item_status = 'PROCESSED', filename = filename.replace('280100', routeno))
        util_func.moveFileToBackUp(out_file_dir, out_file_backup_dir, filename, outfile_date)
        util_func.moveFileToBackUp(out_file_dir, out_file_backup_dir, imgfilename, outfile_date)
    except Exception, e:
        logger.error(e)



def getItemAmountTotal(file_list):
    totAmount = 0.00
    for row in file_list:
        #print "ItemSeqNo:%s Values:%s" % (handleNoneDictValue(row, 'itemseqno', 's'), str(handleNoneDictValue(row, 'amount', 'd')))
        totAmount += float(handleNoneDictValue(row, 'amount', 'd'))
    #totAmount = totAmount + [float(handleNoneDictValue(row, 'amount', 'd')) for row in file_list]
    return totAmount
