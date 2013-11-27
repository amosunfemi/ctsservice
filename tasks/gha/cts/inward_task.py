import time
import os
from tasks.celery import celery
from celery import group
from celery.registry import tasks
from tasks.celery import SqlAlchemyTask
from utility.xml2dict import XML2Dict
from utility.amt2word.num2word_EN import Num2Word_EN
import utility.utility_functions as util_func
import io
import datetime
import service_config
from utility.xml2dict import XML2Dict
import fnmatch
from tasks.celery import logger
import os
import json


n2w = Num2Word_EN()

date_created = str(datetime.date.today())[0:4] + '-' + str(datetime.date.today())[5:7] + '-' + str(datetime.date.today())[8:10]
time_created = str(datetime.datetime.now())[11:13] + ':' + str(datetime.datetime.now())[14:16] + ':' + str(datetime.datetime.now())[17:19]
file_image_array = []
filetoprocess = []
folder_name, image_folder = '', ''
xml = XML2Dict()
folder_name, image_folder = '', ''
cashletter_id, creation_time, creation_date, file_id, sessionnumber, sessiondate, bundle_id = '', '', '', '', '', '', ''


@celery.task(name="tasks.gha.cts.InwardTasks.processFileInwardContent", base=SqlAlchemyTask)
def processFileInwardContent(filetoprocess, param_dict):
    '''Process the file content'''
    retlist = []
    try:
        folder_name, image_folder, xml_backup_dir, img_backup_dir = param_dict['folder_name'], param_dict['image_folder'], param_dict['xml_backup_folder'], param_dict['image_backup_folder']
        logger.info('Processing File :' + filetoprocess)
        if not fnmatch.fnmatch(filetoprocess, '*.XML'):
            return []
        file_item_content = xml.parse(folder_name  + filetoprocess)

        if 'FileHeader' in file_item_content and 'CashLetterHeader' in file_item_content['FileHeader']:

            items = file_item_content['FileHeader']['CashLetterHeader']['BundleHeader']['Item']
            cashletter_id = file_item_content['FileHeader']['CashLetterHeader']['CLID']['value']
            creation_time = file_item_content['FileHeader']['CreationTime']['value']
            creation_date = file_item_content['FileHeader']['CreationDate']['value']
            file_id = file_item_content['FileHeader']['FileID']['value']
            sessionnumber = util_func.getValueFromDict(file_item_content['FileHeader'], 'SessionNumber')
            sessionnumber = util_func.getValueFromDict(sessionnumber, 'value')
            sessiondate = file_item_content['FileHeader']['SessionDate']['value']
            bundle_id = file_item_content['FileHeader']['CashLetterHeader']['BundleHeader']['BundleID']['value']


            header_info = {'image_folder':image_folder, 'date_created':date_created, 'cashletter_id': cashletter_id, 'creation_time': creation_time, 'creation_date': creation_date, 'file_id': file_id,
                           'sessionnumber': sessionnumber, 'sessiondate': sessiondate, 'bundle_id': bundle_id, 'xml_file_name': os.path.split(str(filetoprocess))[1]}
            logger.info('Header info set')
            if type(items) == list:
                for item in items:
                    inward_resp, header_info, file_image_arr, itemseqno = saveItemByType(item, header_info)
                    retlist.append({'ItemSeqNo': itemseqno, 'Status': inward_resp[1]})

            else:
                inward_resp, header_info, file_image_arr, itemseqno = saveItemByType(items, header_info)
                retlist.append({'ItemSeqNo': itemseqno, 'Status': inward_resp[1]})


            if 'xml_file_name' in header_info:
                util_func.moveFileToBackUp(folder_name, xml_backup_dir, header_info['xml_file_name'], header_info['date_created'])
            if 'img_file_name' in header_info:
                util_func.moveFileToBackUp(folder_name, img_backup_dir, header_info['img_file_name'], header_info['date_created'])

            logger.info('File Moved')
    except Exception, e:
        logger.error(e)

    logger.info(retlist)

    return retlist

def saveItemByType(item, header_info):
    if 'ImageViewDetail' in item:
        return saveItem(item, header_info, item['ImageViewDetail'])
    else:
        return saveItem(item, header_info)






def buildImageDetailStructure( image_detail, pic_index, image_folder, file_image_array, header_info, itemseqno):
    import base64
    image_dict = util_func.extractValueFromXml2Dict(image_detail)
    image_view_data, image_view_analysis = dict(), dict()
    if 'ImageViewData' in image_detail:
        image_view_data = util_func.extractValueFromXml2Dict(image_detail['ImageViewData'])

    if 'ImageViewAnalysis' in image_detail:
        image_view_analysis = util_func.extractValueFromXml2Dict(image_detail['ImageViewAnalysis'])

    if len(file_image_array) == 0:
        header_info['img_file_name'] = image_view_data['FileName']
        file_image_array = readImageInByteArrayFromFile(header_info['image_folder'] + image_view_data['FileName'])

    return {'compressiontype': util_func.getValueFromDict(image_dict, 'CompressionType'),
            'imageavailable': util_func.getValueFromDict(image_dict, 'ImageAvailable'),
            'viewdescriptor': image_dict['ViewDescriptor'],
            'viewformat': image_dict['ViewFormat'],
            'itemseqno': itemseqno,
            #'viewsideindicator': image_dict['ViewSideIndicator'],
            'clippingorigin': util_func.getValueFromDict(image_view_data, 'ClippingOrigin'),
            'filename': image_view_data['FileName'],
            'imagedatalength': image_view_data['ImageDataLength'],
            'imagedataoffset': image_view_data['ImageDataOffset'],
            'pic_index': pic_index,
            'bundle_id': header_info['bundle_id'],
            'cash_letterid': header_info['cashletter_id'],
            'imageprocessed': 'N',
            'imagequality': util_func.getValueFromDict(image_view_analysis, 'ImageQuality'),
            'imageusability': util_func.getValueFromDict(image_view_analysis, 'ImageUsability'),
            'imagingbankspecifictest': util_func.getValueFromDict(image_view_analysis, 'ImagingBankSpecificTest'),
            'source': util_func.getValueFromDict(image_view_analysis, 'Source'),
            'userfield': util_func.getValueFromDict(image_view_analysis, 'UserField'),
            'imagedata': str(base64.encodestring(getImageFromImageByteArray(file_image_array, long(image_view_data['ImageDataLength']), long(image_view_data['ImageDataOffset']))))
            }, file_image_array, header_info


def buildItemDetailStructure(item_detail, header_info):
    item_dict = util_func.extractValueFromXml2Dict(item_detail)
    addendum_dict = util_func.extractValueFromXml2Dict(item_detail['AddendA'])
    return {'itemseqno': item_dict['ItemSeqNo'],
            'payorbankroutno': item_dict['PayorBankRoutNo'],
            'amount': item_dict['Amount'],
            'accountno': item_dict['AccountNo'],
            'serialno': item_dict['SerialNo'],
            'collection_type': item_dict['CollectionType'],
            'transcode': item_dict['TransCode'],
            'presentingbankroutno': item_dict['PresentingBankRoutNo'],
            'presentmentdate': item_dict['PresentmentDate'],
            'cycleno': item_dict['CycleNo'],
            'clearingtype': item_dict['ClearingType'],
            'doctype': item_dict['DocType'],
            'micrrepairflags': item_dict['MICRRepairFlags'],
            'truncatingrtno': item_dict['TruncatingRTNo'],
            'currencyind': item_dict['CurrencyInd'],
            'item_status': item_dict['ItemStatus'],
            'representmentcnt': item_dict['RepresentmentCnt'],
            'cashvalueind': item_dict['CashValueInd'],
            'instrumenttype': item_dict['InstrumentType'],
            'max_decision_period': item_dict['MaxDecisionPeriod'],
            'bofdroutno': addendum_dict['BOFDRoutNo'],
            'bofdbusdate': addendum_dict['BOFDBusDate'],
            'depositoracct': addendum_dict['DepositorAcct'],
            'transdetail': item_dict['TransactionDetail'],
            'incoming_file_name': header_info['xml_file_name'],
            'date_created': date_created,
            'creationdate': header_info['creation_date'],
            'creationtime': header_info['creation_time'],
            'sessionnumber': header_info['sessionnumber'],
            'sessiondate': header_info['sessiondate'],
            'bundle_id': header_info['bundle_id'],
            'status': 'ACTIVE',
            'item_status': 'ACTIVE',
            'amountinwords': n2w.to_currency(float(item_dict['Amount']) * 100)
            }, item_dict['ItemSeqNo']

def readImageInByteArrayFromFile(image_file):
    try:
        file = io.FileIO(image_file, mode='r')
        filearray = file.readall()
        file.close()
        file = None
        return filearray
    except Exception, e:
            logger.error(e)

def getImageFromImageByteArray(barray, datalength, offset):
    try:
        return barray[offset:offset + datalength]
    except Exception, e:
        logger.error(e)


def saveItem( item, header_info, image_details = None):
    '''Save each item'''
    image_detail_coll = []
    file_image_arr = []

    if image_details:
        for i, image_detail in enumerate(image_details):
            image_detail_dict, file_image_arr, header_info = buildImageDetailStructure(image_detail, i + 1, image_folder, file_image_arr, header_info, item['ItemSeqNo']['value'])
            image_detail_coll.append(image_detail_dict)

    item_data, itemseqno = buildItemDetailStructure(item, header_info)
    item_data['image_details'] = image_detail_coll
    inward_resp = util_func.sendPostRequest(service_config.HTTP_INWARD_ITEM_REQUEST, item_data)
    return inward_resp, header_info, file_image_arr, itemseqno



def processIncomingInwardFiles(kwargs):
    folder_name, image_folder, process_id = util_func.getValueFromDict(kwargs, 'folder_name'), util_func.getValueFromDict(kwargs, 'image_folder'), \
                                            util_func.getValueFromDict(kwargs, 'process_running_id')
    retlist = []
    try:
        res = group(processFileInwardContent.subtask((filetoprocess, kwargs)) for filetoprocess in os.listdir(folder_name)).apply_async()
        retlist = res.get()

    except Exception, e:
        logger.error(e)

    return retlist, process_id





            
