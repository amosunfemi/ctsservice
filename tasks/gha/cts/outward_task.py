import time
from tasks.celery import celery
from tasks.celery import SqlAlchemyTask
from tasks.celery import log_handler
import utility.XMLRequestParser as xmlparser
import service_config
import utility.utility_functions as util_func

def generateOutwardFiles(kwargs):
    date_created, process_id = util_func.getValueFromDict(kwargs, 'date_created'), util_func.getValueFromDict(kwargs, 'process_running_id')
    retlist = []
    try:
        res = group(processFileInwardContent.subtask((filetoprocess, kwargs)) for filetoprocess in os.listdir(folder_name)).apply_async()
        retlist = res.get()

    except Exception, e:
        logger.error(e)

    return retlist, process_id

def fetchOutwardItems(date_created):
    #date_created = date_created, status = 'ACTIVE', acct_status = 'VALID', auth_status = 'Y'
    filters = [dict(name='date_created', op='eq', val=date_created), dict(name='status', op='eq', val='ACTIVE'), dict(name='acct_status', op='eq', val='VALID'),
                dict(name='auth_status', op='eq', val='Y')]
    params = dict(q=json.dumps(dict(filters=filters)))
    response = util_func.sendGetRequest(service_config.HTTP_OUTWARD_ITEMS, filters)
    return response.json()['objects']




def getNextFileID():
    output =""
    try:
        response = util_func.sendGetRequest(service_config.HTTP_SEQUENCE_REQUEST + 'CTS_SEQ_OUTFILE_ID')

    except Exception, e:
        logger.error(e)

    return output


def executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid):
    logic = itemlogic.ItemsLogic()
    lovlogic = LovLogic()
    try:
        filename, filename_done, imgfilename, imgfilename_done = xmlparser.buildCTSXml(file_header, list_to_file, file_footer, routeno, fileid)#listofitems, routno_brn,  userid,  fileID = None, status = None


        os.rename(rootdir  + filename, rootdir + filename.replace('280100', routeno))
        os.rename(rootdir  + filename_done, rootdir  + filename_done.replace('280100', routeno))
        os.rename(rootdir  + imgfilename, rootdir  + imgfilename.replace('280100', routeno))
        os.rename(rootdir  + imgfilename_done, rootdir  + imgfilename_done.replace('280100', routeno))

        logic.saveInItemCollection(list_to_file, routeno, '', fileID = fileid, status = 'PROCESSED', action = 'save', item_status = 'PROCESSED', filename = filename.replace('280100', routeno))
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), filename)
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), filename_done)
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), imgfilename)
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), imgfilename_done)
    except Exception, e:
        logger.error(e)


def executeFileGeneration2(file_header, list_to_file, file_footer, routeno, fileid):
    logic = itemlogic.ItemsLogic()
    lovlogic = LovLogic()
    try:
        filename, filename_done, imgfilename, imgfilename_done = xmlparser.buildCTSXml2(file_header, list_to_file, file_footer, routeno, fileid)#listofitems, routno_brn,  userid,  fileID = None, status = None
        logic.saveInItemCollection(list_to_file, routeno, '', fileID = fileid, status = 'PROCESSED', action = 'save', item_status = 'PROCESSED', filename = filename.replace('280100', routeno))

        os.rename(xrootdir  + filename, xrootdir + filename.replace('280100', routeno))
        os.rename(xrootdir  + filename_done, xrootdir  + filename_done.replace('280100', routeno))
        os.rename(xrootdir  + imgfilename, xrootdir  + imgfilename.replace('280100', routeno))
        os.rename(xrootdir  + imgfilename_done, xrootdir  + imgfilename_done.replace('280100', routeno))


        moveXmlFileToBackUp(lovlogic.getAchOutDir(), filename)
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), filename_done)
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), imgfilename)
        moveXmlFileToBackUp(lovlogic.getAchOutDir(), imgfilename_done)
    except Exception, e:
        logger.error(e)



def moveXmlFileToBackUp(rootdir, file_name):
    logic = LovLogic()
    try:
        dateStr = str(datetime.date.today())[8:10] + '-' + str(datetime.date.today())[5:7] + '-' + str(datetime.date.today())[0:4]
        currbackupdir = logic.getOutwardFileBackUpDir() +  dateStr
        if not os.path.exists(currbackupdir):
            os.makedirs(currbackupdir)
        shutil.copy(rootdir + file_name, currbackupdir)
    except Exception, e:
        logger.error(e)



def generateOutgoingFiles(date_created, routeno):
    #pool = Pool(None)
    errMsg = ''
    output = ''
    try:
            logic = itemlogic.ItemsLogic()

            retlist = logic.retrieveSavedItemByDateCreated(date_created)
            list_to_file = []
            y = 0
            rem = len(retlist) % 50
            for x in range(abs(len(retlist) / 50)):
                if x == 0:

                    list_to_file = retlist[x:50 * (x + 1)]
                    y = (50 * (x + 1))
                else:
                    list_to_file = retlist[y:50 * (x + 1)]
                    y = (50 * (x + 1))

                file_header = dict()
                file_footer = dict()
                fileid = getNextFileID()
                file_header['VersionNumber'] = '040001'
                file_header['TestFileIndicator'] = 'P'
                file_header['CreationDate'] = str(datetime.date.today())[0:4]  + str(datetime.date.today())[5:7]  + str(datetime.date.today())[8:10]
                file_header['CreationTime'] = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16]  + str(datetime.datetime.now())[17:19]
                file_header['FileID'] = fileid

                file_footer['TotalItemCount'] = len(list_to_file)#getItemCountFileID(fileid)

                file_footer['TotalAmount'] = getItemAmountTotal(list_to_file)#getAmountTotalByFileID(fileid)

                #target=doChequeAlert, args=(fetchCustomerByApplication(appcode), appcode)
                executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid)
                #p = Process(target=executeFileGeneration, args=(file_header, list_to_file, file_footer, routeno, fileid,))
                #p.start()


                #result = pool.apply_async(executeFileGeneration, [file_header, list_to_file, file_footer, routeno, fileid])
                #executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid)
                #xmlparser.buildCTSXml(file_header, list_to_file, file_footer, routeno, fileid)


            if rem > 0:
                list_to_file = retlist[abs(len(retlist) / 50) * 50 : len(retlist)]
                file_header = dict()
                file_footer = dict()
                fileid = getNextFileID()
                file_header['VersionNumber'] = '040001'
                file_header['TestFileIndicator'] = 'P'
                file_header['CreationDate'] = str(datetime.date.today())[0:4]  + str(datetime.date.today())[5:7]  + str(datetime.date.today())[8:10]
                file_header['CreationTime'] = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16]  + str(datetime.datetime.now())[17:19]
                file_header['FileID'] = fileid

                file_footer['TotalItemCount'] = len(list_to_file)#getItemCountFileID(fileid)

                file_footer['TotalAmount'] = getItemAmountTotal(list_to_file)#getAmountTotalByFileID(fileid)

                #executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid)
                executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid)
                #p = Process(target=executeFileGeneration, args=(file_header, list_to_file, file_footer, routeno, fileid,))
                #p.start()


                #result = pool.apply_async(executeFileGeneration, [file_header, list_to_file, file_footer, routeno, fileid])
                #xmlparser.buildCTSXml(file_header, list_to_file, file_footer, routeno, fileid)


    except Exception, e:
        logger.error(e)
        errMsg = str(e)

    if errMsg != '':
        output = errMsg
    return sj.dumps(output)


def generateOutgoingFiles2(date_created, routeno):
    #pool = Pool(None)
    errMsg = ''
    output = ''
    try:
            logic = itemlogic.ItemsLogic()

            retlist = logic.retrieveSavedItemByDateCreated2(date_created)
            list_to_file = []
            y = 0
            rem = len(retlist) % 50
            for x in range(abs(len(retlist) / 50)):
                if x == 0:

                    list_to_file = retlist[x:50 * (x + 1)]
                    y = (50 * (x + 1))
                else:
                    list_to_file = retlist[y:50 * (x + 1)]
                    y = (50 * (x + 1))

                file_header = dict()
                file_footer = dict()
                fileid = getNextFileID()
                file_header['VersionNumber'] = '040001'
                file_header['TestFileIndicator'] = 'P'
                file_header['CreationDate'] = str(datetime.date.today())[0:4]  + str(datetime.date.today())[5:7]  + str(datetime.date.today())[8:10]
                file_header['CreationTime'] = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16]  + str(datetime.datetime.now())[17:19]
                file_header['FileID'] = fileid

                file_footer['TotalItemCount'] = len(list_to_file)#getItemCountFileID(fileid)

                file_footer['TotalAmount'] = getItemAmountTotal(list_to_file)#getAmountTotalByFileID(fileid)

                #target=doChequeAlert, args=(fetchCustomerByApplication(appcode), appcode)
                executeFileGeneration2(file_header, list_to_file, file_footer, routeno, fileid)
                #p = Process(target=executeFileGeneration, args=(file_header, list_to_file, file_footer, routeno, fileid,))
                #p.start()


                #result = pool.apply_async(executeFileGeneration, [file_header, list_to_file, file_footer, routeno, fileid])
                #executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid)
                #xmlparser.buildCTSXml(file_header, list_to_file, file_footer, routeno, fileid)


            if rem > 0:
                list_to_file = retlist[abs(len(retlist) / 50) * 50 : len(retlist)]
                file_header = dict()
                file_footer = dict()
                fileid = getNextFileID()
                file_header['VersionNumber'] = '040001'
                file_header['TestFileIndicator'] = 'P'
                file_header['CreationDate'] = str(datetime.date.today())[0:4]  + str(datetime.date.today())[5:7]  + str(datetime.date.today())[8:10]
                file_header['CreationTime'] = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16]  + str(datetime.datetime.now())[17:19]
                file_header['FileID'] = fileid

                file_footer['TotalItemCount'] = len(list_to_file)#getItemCountFileID(fileid)

                file_footer['TotalAmount'] = getItemAmountTotal(list_to_file)#getAmountTotalByFileID(fileid)

                #executeFileGeneration(file_header, list_to_file, file_footer, routeno, fileid)
                executeFileGeneration2(file_header, list_to_file, file_footer, routeno, fileid)
                #p = Process(target=executeFileGeneration, args=(file_header, list_to_file, file_footer, routeno, fileid,))
                #p.start()


                #result = pool.apply_async(executeFileGeneration, [file_header, list_to_file, file_footer, routeno, fileid])
                #xmlparser.buildCTSXml(file_header, list_to_file, file_footer, routeno, fileid)


    except Exception, e:
        print e
        errMsg = str(e)

    if errMsg != '':
        output = errMsg
    return sj.dumps(output)



def getNextItemSerialNo():
    output =""
    try:
        logic = LovLogic()
        filterResult = logic.executeQuery("select  CTS_OUT_ITEMS_SEQ.nextval from dual")
        for row in filterResult:
            return str(row[0]).zfill(10)


    except Exception, e:
        print e

    return output





def getCustAccounDetail(accountno):
    '''
    '''
    output ={}
    try:
        logic = LovLogic()
        '''
        Need to validate GLs to for CTS
        '''
        filterResult = logic.executeQuerycbs("""select distinct trim(cod_acct_no), trim(cod_cust), trim(nam_cust_shrt),
         trim(nam_ccy_short), trim(cod_acct_stat), trim(txt_acct_status)
                                                from ch_acct_mast, ba_ccy_code,  BA_ACCT_STATUS
                                                where ch_acct_mast.cod_ccy = ba_ccy_code.cod_ccy
                                                and ch_acct_mast.cod_acct_stat = BA_ACCT_STATUS.cod_acct_status
                                                and trim(cod_acct_no) ='%s'""" % accountno)
        for row in filterResult:
            acct_status = 'VALID'
            if str(row[4]) == '1':
                acct_status = 'CLOSED'

            if str(row[4]) == '7':
                acct_status = 'DORMANT'

            if str(row[4]) == '5':
                acct_status = 'CLOSED'

            if str(row[4]) == '2':
                acct_status = 'BLOCKED'

            if str(row[4]) == '3':
                acct_status = 'DEBIT BLOCKED'

            if str(row[4]) == '11':
                acct_status = 'DEBIT BLOCKED'

            if str(row[4]) == '14':
                acct_status = 'DEBIT BLOCKED'


            output = {'acct_no' : str(row[0]), 'cust_no': str(row[1]), 'name': str(row[2]), 'curr_ind': str(row[3]), 'acct_status': acct_status}



    except Exception, e:
        print e

    return output


def handleNoneDictValue(dictionary, fld, s):
    try:
        if s == 's' and dictionary[fld] is not None and str(dictionary[fld]) != 'None':
            return str(dictionary[fld])
        elif s == 's':
            return ''
        elif s == 'd' and dictionary[fld]:
            return float(dictionary[fld])
        elif s == 'i' and dictionary[fld]:
            return int(dictionary[fld])
        elif s == 'l' and dictionary[fld]:
            return long(dictionary[fld])
    except Exception, e:
        if s == 's':
            return ''
        elif s == 'd':
            return 0.00
        elif s == 'i':
            return 0

def returnCustDetailsNonJSON(cust_acct):
    '''
    Get detail of the Customer already saved in the ACH system. Return data as a dictionary.
    Internal Usage not exposed.
    '''
    output = {}
    if cust_acct:

        try:
            logic = LovLogic()
            filterResult = logic.executeQuery("select acct_no, cust_no, acct_name, cur_ind, acct_status from ACH_CUST_ACCT WHERE acct_no = '%s'" % cust_acct)

            for row in filterResult:
                output = {'acct_no' : str(row[0]), 'cust_no': str(row[1]), 'acct_name': str(row[2]), 'cur_ind': str(row[3]), 'acct_status': str(row[4])}
                break


        except Exception, e:
            logger.error(e)

    return output

def sendCustAcctRequestToQueue(cust_acct, corr_id):
    '''
    For putting msgs into the queue for the
    core banking interface application.
    '''
    import json as sj
    import uuid

    header_dict = dict()


    header_dict['request_type'] = 'CIF_ACCT'
    header_dict['msg_type'] = '0'

    logic = itemlogic.ItemsLogic()



    out_dict = {'header' : header_dict, 'acct_no': cust_acct}

    try:
        msg_sender.generateMsg(msgtosend = sj.dumps(out_dict), corrid = corr_id)
    except Exception, e:
        logger.error(e)

def getCustomerDetailNonJSON(cust_acct):
    '''
    Just drop the customer acct as a request
    '''
    corr_id = str(uuid.uuid1())
    try:
        sendCustAcctRequestToQueue(cust_acct, corr_id)
    except Exception, e:
        logger.error(e)

def getBankBOGCodeNonJson(bankcode):
    try:
        output = ''
        logic = LovLogic()
        filterResult = logic.executeQuery("SELECT bog_code  FROM ACH_BANK_ROUTING_NO WHERE bank_routing_nbr='%s'" % bankcode)
        for row in filterResult:
            output = str(row[0])
            break
    except Exception, e:
        logger.error(e)

    return output


def getRoutingNoNonJSON(dir):
    ret_list = []
    try:
        logic = LovLogic()
        queryString = ''
        if dir == 'out':
            queryString = "SELECT bank_routing_nbr, bog_code, OUTWARD_GL, suspense_gl_code, INWARD_GL FROM ACH_BANK_ROUTING_NO"
        elif dir == 'in':
            queryString = "SELECT bank_routing_nbr, bog_code, INWARD_GL, suspense_gl_code, OUTWARD_GL FROM ACH_BANK_ROUTING_NO"
        elif dir == 'outrej':
            queryString = "SELECT bank_routing_nbr, bog_code, OUTWARD_RET_GL, suspense_gl_code, OUTWARD_GL FROM ACH_BANK_ROUTING_NO"
        elif dir == 'inrej':
            queryString = "SELECT bank_routing_nbr, bog_code, INWARD_RET_GL, suspense_gl_code, OUTWARD_GL FROM ACH_BANK_ROUTING_NO"
        filterResult = logic.executeQuery(queryString)
        for row in filterResult:
            retDict = {'routeno' : str(row[0]), 'name' : str(row[1]), 'gl_code' : str(row[2]), 'suspensegl' : str(row[3]), 'gl_code1' : str(row[4])}
            ret_list.append(retDict)
    except Exception, e:
        logger.error(e)

    return ret_list

def dbg(str):
    try:
        print(str)
    except Exception, e:
        print e

def getBranchesByBank(bank_code):
    ret_list = []
    try:
        logic = LovLogic()
        queryString = "select branch_routing_nbr from ACH_BRANCHES_ROUTING_NO where cc_routing_nbr = '%s'" % bank_code

        filterResult = logic.executeQuery(queryString)
        for row in filterResult:
            ret_list.append(str(row[0]))
    except Exception, e:
        logger.error(e)

    return ret_list

def getBranchBankCode(brn_code):
    ret_list = []
    try:
        logic = LovLogic()
        queryString = "select branch_routing_nbr from ACH_BRANCHES_ROUTING_NO where cc_routing_nbr = '%s'" % brn_code
        dbg(queryString)

        filterResult = logic.executeQuery(queryString)
        for row in filterResult:
            ret_list.append(str(row[0]))
    except Exception, e:
        logger.error(e)

    return ret_list

def putEntriesMessageInQueue(header, footer, itemlist, direction = None):
    '''
    For putting msgs into the queue for the
    core banking interface application.
    '''
    import json as sj
    import uuid
    item_list = list()
    header_dict = dict()

    header_dict['file_id'] = str(header['file_id'])
    #header_dict['creation_date'] = str(header['CreationDate'])
    #header_dict['creation_time'] = str(header['CreationTime'])
    if direction:
        if direction == 'out':
            header_dict['direction'] = 'out'
        if direction == 'in':
            header_dict['direction'] = 'in'
        if direction == 'outrej':
            header_dict['direction'] = 'outrej'
        if direction == 'exp':
            header_dict['direction'] = 'exp'
        if direction == 'exprej':
            header_dict['direction'] = 'exprej'

    header_dict['request_type'] = 'ENTRIES'
    header_dict['msg_type'] = '0'

    logic = itemlogic.ItemsLogic()


    footer_dict = {'total_item_count' : str(footer['TotalItemCount']), 'total_amount' : str(footer['TotalAmount'])}


    out_dict = {'header' : header_dict, 'items': itemlist, 'footer' : footer_dict}

    try:
        msg_sender.generateMsg(msgtosend = sj.dumps(out_dict), corrid = str(uuid.uuid1()))
    except Exception, e:
        logger.error(e)

def generateOutGoingGefuEntries(date_created):
    '''
    Not Done. Performance needed to be improved.
    '''
    logic = LovLogic()
    itemLogic = itemlogic.ItemsLogic()
    item_list1 = []
    item_list = []
    item_tot = 0
    errmsg = ''


    bank_list = getRoutingNoNonJSON('out')
    for bank in bank_list:
        bank_code = str(bank['routeno'])
        bank_name = str(bank['name'])
        print bank_name
        '''gl_code = str(bank['gl_code'])
        gl_code1 = str(bank['gl_code1'])
        bank_name = str(bank['name'])
        suspensegl = str(bank['suspensegl'])

        #print bank_code
        '''
        for row in getBranchesByBank(bank_code):
            print row
            item_list = itemLogic.retrieveCTSOutwardItemByDateCreatedAndRouteNoInstrType2(date_created, row, 'DB')
                #item_list = listofoutitems
            item_tot = item_tot +  len(item_list)
            #print item_list
            '''
            This is for the outgoing files.Change the accountno  to gl_code, for the gl entries
            '''
            #s = "bank code:%s, branch code %s,  total items %s" % (bank_code, row, str(len(item_list)))
            #print s
            if len(item_list) > 0:
                for item in item_list:
                    '''item is a credit item, need to create a debit item for the depositor's account'''
                    dep_item = {}
                    '''
                    lue(item, 'chequenumber', 's')
                    dep_item['transdetail'] = transaction_det
                    '''
                    dep_item['txndate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['itemseqno'] = str(handleNoneDictValue(item, 'itemseqno', 's')).zfill(12)
                    dep_item['amount'] = handleNoneDictValue(item, 'amount', 's')
                    '''dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')'''
                    dep_item['accountno'] = handleNoneDictValue(item, 'accountno', 's')
                    dep_item['serialno'] = handleNoneDictValue(item, 'serialno', 's')
                    dep_item['presentingbankroutno'] = handleNoneDictValue(item, 'presentingbankroutno', 's')
                    dep_item['presentmentdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['clearingtype'] = handleNoneDictValue(item, 'clearingtype', 's')
                    dep_item['truncatingrtno'] = handleNoneDictValue(item, 'truncatingrtno', 's')
                    dep_item['currencyind'] = handleNoneDictValue(item, 'currencyind', 's')
                    dep_item['instrumenttype'] = handleNoneDictValue(item, 'instrumenttype', 's')
                    dep_item['depositoracct'] = handleNoneDictValue(item, 'depositoracct', 's')
                    dep_item['transdetail'] =  bank_name+'Bank,CHQ. No:'+ handleNoneDictValue(item, 'serialno', 's') +'-'+ handleNoneDictValue(item, 'transdetail', 's')
                    dep_item['creationdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['payeename'] = handleNoneDictValue(item, 'payeename', 's')
                    dep_item['payername'] = handleNoneDictValue(item, 'payername', 's')
                    dep_item['payorbankroutno'] = handleNoneDictValue(item, 'payorbankroutno', 's')
                    dep_item['datecreated'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['acctstatus'] = handleNoneDictValue(item, 'acct_status', 's')
                    dep_item['acctname'] = handleNoneDictValue(item, 'accountname', 's')
                    item_list1.append(dep_item)
                    #item_list1.append(item)
    if len(item_list1) > 0:
        file_header = {'file_id' : handleNoneDictValue(item_list1[0], 'fileid', 's')}
        #file_footer = {'TotalItemCount' : len(item_list1), 'TotalAmount' : getItemAmountTotal(item_list1) / 2}
        file_footer = {'TotalItemCount' : len(item_list1), 'TotalAmount' : getItemAmountTotal(item_list1)}
        #item['itemseqno1'] = handleNoneDictValue(item, 'itemseqno', 's')
        dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')
        putEntriesMessageInQueue(file_header, file_footer, item_list1, direction = 'out')


        #s = "bank code:%s, total items %s" % (bank_code, str(len(item_list1)))
        #print s
        #item_list1 = []

        try:
            for item in item_list1:
                uniqueid = handleNoneDictValue(item, 'itemseqno1', 's')
                itemLogic.updateCTSOutwardItem('status', uniqueid,  '', '', '', '', 'UPLOADED')
                            #item_list = itemLogic.retrieveSavedItemByDateCreatedAndRouteNoInstrType2(date_created, bank_code, 'CR')
                            #itemLogic.saveInItemCollection(item_list, session.route_no, session.userid, file_header['file_id'], status = 'UPLOADED', action = 'save', item_status = 'UPLOADED')

        except Exception, e:
            errmsg = str(e)
            print e

    #print item_tot
    print("Completed Outward Cheques for " + str(item_tot) + " Transactions")
    return sj.dumps(errmsg)

def generateOutGoingGefuEntriesexp(date_created):
    '''
    Not Done. Performance needed to be improved.
    '''
    logic = LovLogic()
    itemLogic = itemlogic.ItemsLogic()
    item_list1 = []
    item_list = []
    item_tot = 0
    errmsg = ''


    bank_list = getRoutingNoNonJSON('out')
    for bank in bank_list:
        bank_code = str(bank['routeno'])
        bank_name = str(bank['name'])
        '''gl_code = str(bank['gl_code'])
        gl_code1 = str(bank['gl_code1'])
        bank_name = str(bank['name'])
        suspensegl = str(bank['suspensegl'])

        #print bank_code
        '''

        for row in getBranchesByBank(bank_code):
            item_list = itemLogic.retrieveCTSOutwardItemByDateCreatedAndRouteNoInstrTypeexp(date_created, row, 'DB')
                #item_list = listofoutitems
            item_tot = item_tot +  len(item_list)
            '''
            This is for the outgoing files.Change the accountno  to gl_code, for the gl entries
            '''
            #s = "bank code:%s, branch code %s,  total items %s" % (bank_code, row, str(len(item_list)))
            #print s
            if len(item_list) > 0:
                for item in item_list:
                    '''item is a credit item, need to create a debit item for the depositor's account'''
                    dep_item = {}
                    '''
                    lue(item, 'chequenumber', 's')
                    dep_item['transdetail'] = transaction_det
                    '''
                    dep_item['txndate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['itemseqno'] = str(handleNoneDictValue(item, 'itemseqno', 's')).zfill(12)
                    dep_item['amount'] = handleNoneDictValue(item, 'amount', 's')
                    '''dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')'''
                    dep_item['accountno'] = handleNoneDictValue(item, 'accountno', 's')
                    dep_item['serialno'] = handleNoneDictValue(item, 'serialno', 's')
                    dep_item['presentingbankroutno'] = handleNoneDictValue(item, 'presentingbankroutno', 's')
                    dep_item['presentmentdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['clearingtype'] = handleNoneDictValue(item, 'clearingtype', 's')
                    dep_item['truncatingrtno'] = handleNoneDictValue(item, 'truncatingrtno', 's')
                    dep_item['currencyind'] = handleNoneDictValue(item, 'currencyind', 's')
                    dep_item['instrumenttype'] = handleNoneDictValue(item, 'instrumenttype', 's')
                    dep_item['depositoracct'] = handleNoneDictValue(item, 'depositoracct', 's')
                    dep_item['transdetail'] =  bank_name+'Bank,Express CHQ. No:'+ handleNoneDictValue(item, 'serialno', 's') +'-'+ handleNoneDictValue(item, 'transdetail', 's')
                    dep_item['creationdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['payeename'] = handleNoneDictValue(item, 'payeename', 's')
                    dep_item['payername'] = handleNoneDictValue(item, 'payername', 's')
                    dep_item['payorbankroutno'] = handleNoneDictValue(item, 'payorbankroutno', 's')
                    dep_item['datecreated'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['acctstatus'] = handleNoneDictValue(item, 'acct_status', 's')
                    dep_item['acctname'] = handleNoneDictValue(item, 'accountname', 's')
                    item_list1.append(dep_item)
                    #item_list1.append(item)
    if len(item_list1) > 0:
        file_header = {'file_id' : handleNoneDictValue(item_list1[0], 'fileid', 's')}
        #file_footer = {'TotalItemCount' : len(item_list1), 'TotalAmount' : getItemAmountTotal(item_list1) / 2}
        file_footer = {'TotalItemCount' : len(item_list1), 'TotalAmount' : getItemAmountTotal(item_list1)}
        #item['itemseqno1'] = handleNoneDictValue(item, 'itemseqno', 's')
        dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')
        putEntriesMessageInQueue(file_header, file_footer, item_list1, direction = 'exp')


        #s = "bank code:%s, total items %s" % (bank_code, str(len(item_list1)))
        #print s
        #item_list1 = []

        try:
            for item in item_list1:
                uniqueid = handleNoneDictValue(item, 'itemseqno1', 's')
                itemLogic.updateCTSOutwardItem('status', uniqueid,  '', '', '', '', 'UPLOADED')
                            #item_list = itemLogic.retrieveSavedItemByDateCreatedAndRouteNoInstrType2(date_created, bank_code, 'CR')
                            #itemLogic.saveInItemCollection(item_list, session.route_no, session.userid, file_header['file_id'], status = 'UPLOADED', action = 'save', item_status = 'UPLOADED')

        except Exception, e:
            errmsg = str(e)
            print e

    #print item_tot
    print("Completed Outward Express Cheques for " + str(item_tot) + " Transactions")
    return sj.dumps(errmsg)


def getBranchCode(routingno):
    try:
        output = ''
        logic = LovLogic()
        filterResult = logic.executeQuery("select code from cts_branch_code where routingno = '%s'" % routingno)
        for row in filterResult:
            output = str(row[0])
            break
    except Exception, e:
        logger.error(e)

    return output
'''
def generateInwardRejectGefuEntries(date_created):



    return sj.dumps(errmsg)'''


def generateOutwardRejectReversalGefuEntries(date_created):
    '''
    Not Done. Performance needed to be improved.
    '''
    logic = LovLogic()
    itemLogic = itemlogic.ItemsLogic()
    item_list1 = []
    item_tot = 0
    errmsg = ''


    bank_list = getRoutingNoNonJSON('out')
    for bank in bank_list:
        bank_code = str(bank['routeno'])
        gl_code = str(bank['gl_code'])
        bank_name = str(bank['name'])
        suspensegl = str(bank['suspensegl'])

        #print bank_code
        #print (date_created, bank_code)
        item_list = itemLogic.retrieveCTSOutwardRejectedItems(date_created, bank_code, 'DB')
        #item_list = listofoutitems
        #print item_list
        item_tot = item_tot +  len(item_list)
        '''
        This is for the outgoing files.Change the accountno  to gl_code, for the gl entries
        '''

        if len(item_list) > 0:
            for item in item_list:
                    #print("inside loop")
                    '''item is a credit item, need to create a debit item for the depositor's account'''
                    dep_item = {}
                    '''
                    lue(item, 'chequenumber', 's')
                    dep_item['transdetail'] = transaction_det
                    '''
                    transaction_det =  bank_name + "Bank, CHQ RETURNED- " + handleNoneDictValue(item, 'serialno', 's')
                    dep_item['txndate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['itemseqno'] = str(handleNoneDictValue(item, 'itemseqno', 's')).zfill(12)
                    dep_item['amount'] = "-"+handleNoneDictValue(item, 'amount', 's')
                    '''dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')'''
                    dep_item['accountno'] = handleNoneDictValue(item, 'accountno', 's')
                    dep_item['serialno'] = handleNoneDictValue(item, 'serialno', 's')
                    dep_item['presentingbankroutno'] = handleNoneDictValue(item, 'presentingbankroutno', 's')
                    dep_item['presentmentdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['clearingtype'] = handleNoneDictValue(item, 'clearingtype', 's')
                    dep_item['truncatingrtno'] = handleNoneDictValue(item, 'truncatingrtno', 's')
                    dep_item['currencyind'] = handleNoneDictValue(item, 'currencyind', 's')
                    dep_item['instrumenttype'] = handleNoneDictValue(item, 'instrumenttype', 's')
                    dep_item['depositoracct'] = handleNoneDictValue(item, 'depositoracct', 's')
                    dep_item['transdetail'] =  transaction_det
                    dep_item['creationdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['payeename'] = handleNoneDictValue(item, 'payeename', 's')
                    dep_item['payername'] = handleNoneDictValue(item, 'payername', 's')
                    dep_item['payorbankroutno'] = handleNoneDictValue(item, 'payorbankroutno', 's')
                    dep_item['datecreated'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['acctstatus'] = handleNoneDictValue(item, 'acct_status', 's')
                    '''dep_item['transdetail'] = transaction_det'''
                    dep_item['acctname'] = handleNoneDictValue(item, 'accountname', 's')
                    item_list1.append(dep_item)

    if len(item_list1) > 0:
        file_header = {'file_id' : handleNoneDictValue(item_list1[0], 'fileid', 's')}
        file_footer = {'TotalItemCount' : len(item_list1), 'TotalAmount' : getItemAmountTotal(item_list1)}
        dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')

        putEntriesMessageInQueue(file_header, file_footer, item_list1, direction = 'outrej')

        #print len(item_list1)
                #item_list1 = []

        try:
            for item in item_list1:
                uniqueid = handleNoneDictValue(item, 'itemseqno', 's')
                itemLogic.updateCTSOutwardItem('status', uniqueid,  '', '', '', '', 'REVERSED')
                                #item_list = itemLogic.retrieveSavedItemByDateCreatedAndRouteNoInstrType2(date_created, bank_code, 'CR')
                                #itemLogic.saveInItemCollection(item_list, session.route_no, session.userid, file_header['file_id'], status = 'UPLOADED', action = 'save', item_status = 'UPLOADED')

        except Exception, e:
            errmsg = str(e)
            print e

    #print item_tot
    print("Completed Outward Cheques Reversal for " + str(item_tot) + " Transactions")
    return sj.dumps(errmsg)



def generateOutwardRejectReversalGefuEntriesexp(date_created):
    '''
    Not Done. Performance needed to be improved.
    '''
    logic = LovLogic()
    itemLogic = itemlogic.ItemsLogic()
    item_list1 = []
    item_tot = 0
    errmsg = ''


    bank_list = getRoutingNoNonJSON('out')
    for bank in bank_list:
        bank_code = str(bank['routeno'])
        gl_code = str(bank['gl_code'])
        bank_name = str(bank['name'])
        suspensegl = str(bank['suspensegl'])

        #print bank_code
        #print (date_created, bank_code)
        item_list = itemLogic.retrieveCTSOutwardRejectedItemsexp(date_created, bank_code, 'DB')
        #item_list = listofoutitems
        #print item_list
        item_tot = item_tot +  len(item_list)
        '''
        This is for the outgoing files.Change the accountno  to gl_code, for the gl entries
        '''

        if len(item_list) > 0:
            for item in item_list:
                    #print("inside loop")
                    '''item is a credit item, need to create a debit item for the depositor's account'''
                    dep_item = {}
                    '''
                    lue(item, 'chequenumber', 's')
                    dep_item['transdetail'] = transaction_det
                    '''
                    transaction_det =  bank_name + "Bank, EXP.CHQ RETURNED- " + handleNoneDictValue(item, 'serialno', 's')
                    dep_item['txndate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['itemseqno'] = str(handleNoneDictValue(item, 'itemseqno', 's')).zfill(12)
                    dep_item['amount'] = "-"+handleNoneDictValue(item, 'amount', 's')
                    '''dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')'''
                    dep_item['accountno'] = handleNoneDictValue(item, 'accountno', 's')
                    dep_item['serialno'] = handleNoneDictValue(item, 'serialno', 's')
                    dep_item['presentingbankroutno'] = handleNoneDictValue(item, 'presentingbankroutno', 's')
                    dep_item['presentmentdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['clearingtype'] = handleNoneDictValue(item, 'clearingtype', 's')
                    dep_item['truncatingrtno'] = handleNoneDictValue(item, 'truncatingrtno', 's')
                    dep_item['currencyind'] = handleNoneDictValue(item, 'currencyind', 's')
                    dep_item['instrumenttype'] = handleNoneDictValue(item, 'instrumenttype', 's')
                    dep_item['depositoracct'] = handleNoneDictValue(item, 'depositoracct', 's')
                    dep_item['transdetail'] =  transaction_det
                    dep_item['creationdate'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['payeename'] = handleNoneDictValue(item, 'payeename', 's')
                    dep_item['payername'] = handleNoneDictValue(item, 'payername', 's')
                    dep_item['payorbankroutno'] = handleNoneDictValue(item, 'payorbankroutno', 's')
                    dep_item['datecreated'] = handleNoneDictValue(item, 'date_created', 's')
                    dep_item['acctstatus'] = handleNoneDictValue(item, 'acct_status', 's')
                    '''dep_item['transdetail'] = transaction_det'''
                    dep_item['acctname'] = handleNoneDictValue(item, 'accountname', 's')
                    item_list1.append(dep_item)

    if len(item_list1) > 0:
        file_header = {'file_id' : handleNoneDictValue(item_list1[0], 'fileid', 's')}
        file_footer = {'TotalItemCount' : len(item_list1), 'TotalAmount' : getItemAmountTotal(item_list1)}
        dep_item['uniqueid'] = handleNoneDictValue(item, 'uniqueid', 's')

        putEntriesMessageInQueue(file_header, file_footer, item_list1, direction = 'exprej')

        #print len(item_list1)
                #item_list1 = []

        try:
            for item in item_list1:
                uniqueid = handleNoneDictValue(item, 'itemseqno', 's')
                itemLogic.updateCTSOutwardItem('status', uniqueid,  '', '', '', '', 'REVERSED')
                                #item_list = itemLogic.retrieveSavedItemByDateCreatedAndRouteNoInstrType2(date_created, bank_code, 'CR')
                                #itemLogic.saveInItemCollection(item_list, session.route_no, session.userid, file_header['file_id'], status = 'UPLOADED', action = 'save', item_status = 'UPLOADED')

        except Exception, e:
            errmsg = str(e)
            print e

    #print item_tot
    print("Completed Express Cheques Reversal for " + str(item_tot) + " Transactions")
    return sj.dumps(errmsg)




def getItemAmountTotal(file_list):
    totAmount = 0.00
    for row in file_list:
        #print "ItemSeqNo:%s Values:%s" % (handleNoneDictValue(row, 'itemseqno', 's'), str(handleNoneDictValue(row, 'amount', 'd')))
        totAmount += float(handleNoneDictValue(row, 'amount', 'd'))
    #totAmount = totAmount + [float(handleNoneDictValue(row, 'amount', 'd')) for row in file_list]
    return totAmount
