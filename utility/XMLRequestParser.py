'''
Created on Sep 30, 2009

This module handles parsing of xml read from the messages

@author: Amosun Sunday
'''
from xml.dom.minidom import parseString
from xml.etree.ElementTree import ElementTree
import datetime
import SqlAlchemy as alchemy
import ItemsLogic as itemlogic
import os


totsize = 0


def parseXMLRequestNew(filename):
    root = ElementTree(file=filename)
    #Create an iterator
    iter = root.getiterator()
    retDict = {}
    #for element in iter:
    #print str(datetime.datetime.now())
    return getAttributes(iter[0])
    #print str(datetime.datetime.now())


def getAttributes(elmt):
    retDict = {}

    if elmt.getchildren():
        child_list = []
        #Can also use: "for child in element.getchildren():"
        new_dict = {}
        for child in elmt:
            if new_dict.has_key(child.tag):
                child_list.append(getAttributes(child))
                new_dict[child.tag] = child_list
            else:
                child_list = []
                child_list.append(getAttributes(child))
                new_dict[child.tag] = child_list

        retDict[elmt.tag] = new_dict

    if elmt.keys():
        for name, value in elmt.items():
            retDict[name] = value

    return retDict

#<FileSummary TotalItemCount="50" TotalAmount="8238142"/></FileHeader>

def buildHeader(params, headerval):
    vNum = str(params['VersionNumber'])
    testFileInd = str(params['TestFileIndicator'])
    crDate = str(datetime.date.today())[8:10] + str(datetime.date.today())[5:7] + str(datetime.date.today())[0:4]
    crTime = str(str(params['CreationTime']))
    filid = str(params['FileID'])
    retVal = """<?xml version="1.0" encoding="UTF-8"?><FileHeader xmlns="urn:schemas-ncr-com:ECPIX:%s:FileStructure:%s" VersionNumber="%s" TestFileIndicator="%s" CreationDate="%s" CreationTime="%s" FileID="%s">""" % (
    headerval, vNum,
    vNum,
    testFileInd,
    crDate,
    crTime,
    filid)
    return retVal


def buildItemsRejects(params):
    strAmt = "%.2f" % float(params['amount'])
    instr_type = ''
    if str(params['instrumenttype']) == 'DR':
        instr_type = 'DB'
    else:
        instr_type = str(params['instrumenttype'])

    retVal = """<Item ItemSeqNo="%s" PayorBankRoutNo="%s" Amount="%s" AccountNo="%s" SerialNo="%s" TransCode="%s" PresentingBankRoutNo="%s" PresentmentDate="%s" CycleNo="%s" ClearingType="%s" CurrencyInd="%s" ReturnReason="%s" InstrumentType="%s"><AddendA BOFDRoutNo="%s" BOFDBusDate="%s" DepositorAcct="%s" /></Item>""" % (
    str(params['itemseqno']),
    str(params['payorbankroutno']),
    strAmt.replace('.', ''),
    str(params['accountno']),
    str(params['serialno']),
    str(params['transcode']),
    str(params['presentingbankroutno']),
    str(params['presentmentdate']),
    str(params['cycleno']),
    str(params['clearingtype']),
    str(params['currencyind']),
    str(params['returnreason']),
    instr_type,
    str(params['bofdroutno']),
    str(params['bofdbusdate']),
    str(params['depositoracct']).strip())
    return retVal


def handleNoneDictValue2(dictionary, fld, s):
    try:
        retVal = dictionary[fld]
        if s == 's':
            return str(retVal).strip()
        elif s == 'd':
            return float(retVal)
        elif s == 'i':
            return int(retVal)
    except Exception, e:
        if s == 's':
            return ''
        elif s == 'd':
            return 0.00
        elif s == 'i':
            return 0


def buildCTSItems(params, imgfilename, imgfilecontent, openfilename):
    logger = alchemy.returnLogger()

    global totsize
    ilgoic = itemlogic.ItemsLogic()
    strAcctNo = str(handleNoneDictValue2(params, 'accountno', 's'))

    try:
        #print params
        strAmt = "%.2f" % float(handleNoneDictValue2(params, 'amount', 's'))
        strColType = ''
        strInstrType = str(handleNoneDictValue2(params, 'instrumenttype', 's'))
        strAcctNo = str(handleNoneDictValue2(params, 'accountno', 's'))

        if strInstrType == 'CR':
            strColType = '20'
        elif strInstrType == 'DB':
            strInstrType = 'DB'
            strColType = '22'
        elif strInstrType == 'DR':
            strColType = '22'
            strInstrType = 'DB'

        pDate = str(handleNoneDictValue2(params, 'presentmentdate', 's')).split('-')
        bofd = str(handleNoneDictValue2(params, 'bofdbusdate', 's')).split('-')
        bofdbusdate = bofd[2] + bofd[1] + bofd[0]
        presDate = pDate[2] + pDate[1] + pDate[0]#str(datetime.date.today())[8:10]+ str(datetime.date.today())[5:7] + str(datetime.date.today())[0:4]
        frontImg, backImg = ilgoic.retrieveCTSUploadItemImage(str(handleNoneDictValue2(params, 'itemseqno', 's')))
        frontimglength, backimglength = len(frontImg), len(backImg)
        if frontimglength > 0:
            frontimgoffset = totsize
            totsize = totsize + len(frontImg)
            print totsize
            openfilename.write(frontImg)
        else:
            frontimgoffset = totsize

        if backimglength:
            totsize = totsize + len(backImg)
            backimgoffset = frontimgoffset + len(frontImg)
            print backimgoffset
            openfilename.write(backImg)
        else:
            backimgoffset = totsize

        depacct = str(handleNoneDictValue2(params, 'depositoracct', 's'))

        '''
        Need to improve on this, its specific to Ecobank
        '''
        if str(handleNoneDictValue2(params, 'payorbankroutno', 's')) == '130100' and len(
                str(handleNoneDictValue2(params, 'payorbankroutno', 's'))) >= 16:
            strAcctNo = strAcctNo[0:3] + strAcctNo[6:len(strAcctNo)]

        if len(depacct) < 13:
            depacct = str(depacct).zfill(13)

        retVal = """<Item ItemSeqNo="%s" PayorBankRoutNo="%s" Amount="%s" AccountNo="%s" SerialNo="%s" TransCode="%s" PresentingBankRoutNo="%s" PresentmentDate="%s" CycleNo="%s" NumOfImageViews="2" ClearingType="%s" DocType="%s" MICRRepairFlags="%s" SpecialHandling="%s" TruncatingRTNo="%s" IQAIgnoreInd="%s" CurrencyInd="%s" RepresentmentCnt="%s" CashValueInd="%s" InstrumentType="%s"><AddendA BOFDRoutNo="%s" BOFDBusDate="%s" DepositorAcct="%s"/>
                    <ImageViewDetail ViewFormat="JFIF" CompressionType="JPEG" ViewSideIndicator="Front Gray" ViewDescriptor="Full" ImageAvailable="Y">
                    <ImageViewData ImageDataLength="%s" ImageDataOffset="%s" FileName="%s" ClippingOrigin="0"/>
                    </ImageViewDetail>
                    <ImageViewDetail ViewFormat="JFIF" CompressionType="JPEG" ViewSideIndicator="Back Gray" ViewDescriptor="Full" ImageAvailable="Y">
                    <ImageViewData ImageDataLength="%s" ImageDataOffset="%s" FileName="%s" ClippingOrigin="0"/>
                    </ImageViewDetail>
                    </Item>""" % (str(handleNoneDictValue2(params, 'itemseqno', 's')),
                      str(handleNoneDictValue2(params, 'payorbankroutno', 's')),
                      strAmt.replace('.', ''),
                      strAcctNo,
                      str(handleNoneDictValue2(params, 'serialno', 's')),
                      str(handleNoneDictValue2(params, 'transcode', 's')),
                      str(handleNoneDictValue2(params, 'presentingbankroutno', 's')),
                      presDate,
                      str(handleNoneDictValue2(params, 'cycleno', 's')),
                      str(handleNoneDictValue2(params, 'clearingtype', 's')),
                      str(handleNoneDictValue2(params, 'doctype', 's')),
                      str(handleNoneDictValue2(params, 'micrrepairflags', 's')),
                      '0',
                      str(handleNoneDictValue2(params, 'truncatingrtno', 's')),
                      str(handleNoneDictValue2(params, 'iqaignoreind', 's')),
                      str(handleNoneDictValue2(params, 'currencyind', 's')),
                      str(handleNoneDictValue2(params, 'representmentcnt', 's')),
                      str(handleNoneDictValue2(params, 'cashvalueind', 's')),
                      strInstrType,
                      str(handleNoneDictValue2(params, 'truncatingrtno', 's')),
                      bofdbusdate,
                      depacct,
                      frontimglength,
                      frontimgoffset,
                      imgfilename,
                      backimglength,
                      backimgoffset,
                      imgfilename)


    except Exception, e:
        print str(handleNoneDictValue2(params, 'itemseqno', 's'))
        logger.error(e)
    return retVal


def buildItems(params):
    logger = alchemy.returnLogger()
    strAcctNo = str(params['accountno'])
    try:
        #print params
        strAmt = "%.2f" % float(params['amount'])
        strColType = ''
        strInstrType = str(params['instrumenttype'])
        strAcctNo = str(params['accountno'])

        if strInstrType == 'CR':
            strColType = '20'
        elif strInstrType == 'DB':
            strInstrType = 'DB'
            strColType = '22'
        elif strInstrType == 'DR':
            strColType = '22'
            strInstrType = 'DB'
        presDate = str(datetime.date.today())[8:10] + str(datetime.date.today())[5:7] + str(datetime.date.today())[0:4]

        '''
        Need to improve on this, its specific to Ecobank
        '''
        if str(params['payorbankroutno']) == '130100' and len(str(params['payorbankroutno'])) >= 16:
            strAcctNo = strAcctNo[0:3] + strAcctNo[6:len(strAcctNo)]

        retVal = """<Item ItemSeqNo="%s" PayorBankRoutNo="%s" Amount="%s" AccountNo="%s" SerialNo="%s" TransCode="%s" PresentingBankRoutNo="%s" PresentmentDate="%s" CycleNo="%s" ClearingType="%s" DocType="%s" CollectionType="%s" MICRRepairFlags="%s" SpecialHandling="%s" TruncatingRTNo="%s" CurrencyInd="%s" RepresentmentCnt="%s" CashValueInd="%s" InstrumentType="%s" PayerName="%s" TransactionDetail="%s"><AddendA BOFDRoutNo="%s" BOFDBusDate="%s" DepositorAcct="%s" PayeeName="%s"/></Item>""" % (
        str(params['itemseqno']),
        str(params['payorbankroutno']),
        strAmt.replace('.', ''),
        strAcctNo,
        str(params['serialno']),
        str(params['transcode']),
        str(params['presentingbankroutno']),
        presDate,
        str(params['cycleno']),
        str(params['clearingtype']),
        str(params['doctype']),
        str(params['collection_type']),
        '000000',
        '0',
        str(params['presentingbankroutno']),
        str(params['currencyind']),
        str(params['representmentcnt']),
        str(params['cashvalueind']),
        strInstrType,
        str(params['payername']),
        str(params['transdetail'])[0:25],
        str(params['presentingbankroutno']),
        str(params['bofdbusdate']),
        str(params['depositoracct']).strip(),
        str(params['payeename']))
    except Exception, e:
        print strAcctNo
        logger.error(e)
    return retVal


def buildFooter(params):
    strAmt = "%.2f" % float(params['TotalAmount'])
    return """<FileSummary TotalItemCount="%s" TotalAmount="%s"/></FileHeader>""" % (
    str(params['TotalItemCount']), strAmt.replace('.', ''))


def buildAchXml(paramHeader, itemList, paramFooter, routingNo, fileid):
    logger = alchemy.returnLogger()
    try:
        ach_out_dir = alchemy.getConfig()['others']['ach_out_dir']
        val = buildHeader(paramHeader, 'CXF')

        val = val + ''.join([buildItems(row) for row in itemList])

        val = val + buildFooter(paramFooter)

        dateStr = str(datetime.date.today())[8:10] + str(datetime.date.today())[5:7] + str(datetime.date.today())[0:4]
        timeStr = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16] + str(
            datetime.datetime.now())[17:19]

        filename = "CXF_" + "250100" + "_" + dateStr + "_" + paramHeader['CreationTime'] + "_01_" + fileid + ".xml"
        filename_done = "CXF_" + "250100" + "_" + dateStr + "_" + paramHeader[
            'CreationTime'] + "_01_" + fileid + ".xml" + ".done"
        myfile = open(ach_out_dir + filename, "w")
        myfiledone = open(ach_out_dir + filename_done, "w")
        myfile.write(val)
        myfile.close()
        myfiledone.close()
    except Exception, e:
        logger.error(e)


def buildCTSImgFile(itemList, filename):
    logger = alchemy.returnLogger()
    ilgoic = itemlogic.ItemsLogic()
    imgfilecontent = bytearray()
    retlist = []
    try:

        for item in itemList:
            itemseqno = item['itemseqno']
            frontImg, backImg = ilgoic.retrieveCTSUploadItemImage(itemseqno)
            retdict = {'itemseqno': itemseqno, 'frontimglength': len(frontImg), 'backimglength': len(backImg)}
            imgfilecontent.append(frontImg)
            retdict['frontimgoffset'] = len(imgfilecontent)
            imgfilecontent.append(backImg)
            retdict['backimgoffset'] = len(imgfilecontent)
            retlist.append(retdict)

        filename.write(imgfilecontent)
        filename.close()

    except Exception, e:
        logger.error(e)

    return retlist


def buildCTSXml(paramHeader, itemList, paramFooter, routingNo, fileid):
    logger = alchemy.returnLogger()
    global totsize
    totsize = 0
    try:
        ach_out_dir = alchemy.getConfig()['others']['ach_out_dir']
        dateStr = str(datetime.date.today())[8:10] + str(datetime.date.today())[5:7] + str(datetime.date.today())[0:4]
        timeStr = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16] + str(
            datetime.datetime.now())[17:19]

        imgfilename = "CIBF_" + "250100" + "_" + dateStr + "_" + paramHeader[
            'CreationTime'] + "_01_" + fileid + "_" + fileid + ".img"
        imgfilename_done = "CIBF_" + "250100" + "_" + dateStr + "_" + paramHeader[
            'CreationTime'] + "_01_" + fileid + "_" + fileid + ".img" + ".done"

        imgfilecontent = []

        #details = buildCTSImgFile(itemList, ach_out_dir + imgfilename)


        val = buildHeader(paramHeader, 'CXF')

        imgfile = open(ach_out_dir + imgfilename, "ab")

        val = val + ''.join([buildCTSItems(row, imgfilename, imgfilecontent, imgfile) for row in itemList])

        val = val + buildFooter(paramFooter)

        filename = "CXF_" + routingNo + "_" + dateStr + "_" + paramHeader['CreationTime'] + "_01_" + fileid + ".xml"
        filename_done = "CXF_" + routingNo + "_" + dateStr + "_" + paramHeader[
            'CreationTime'] + "_01_" + fileid + ".xml" + ".done"
        myfile = open(ach_out_dir + filename, "w")
        myfiledone = open(ach_out_dir + filename_done, "w")
        imgfiledone = open(ach_out_dir + imgfilename_done, "w")
        myfile.write(val)

        myfile.close()
        myfiledone.close()
        imgfiledone.close()
        imgfile.close()
    except Exception, e:
        logger.error(e)

    return filename, filename_done, imgfilename, imgfilename_done


def buildAchXmlRejects(paramHeader, itemList, paramFooter, routingNo, fileid):
    logger = alchemy.returnLogger()
    try:
        ach_out_dir = alchemy.getConfig()['others']['ach_out_dir']
        val = buildHeader(paramHeader, 'RRF')

        val = val + ''.join([buildItemsRejects(row) for row in itemList])

        val = val + buildFooter(paramFooter)

        dateStr = str(datetime.date.today())[8:10] + str(datetime.date.today())[5:7] + str(datetime.date.today())[
                                                                                       0:4]#str(datetime.date.today())[8:10] + str(datetime.date.today())[5:7] + str(datetime.date.today())[0:4]
        timeStr = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16] + str(
            datetime.datetime.now())[
                                                                                              17:19]#str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16] + str(datetime.datetime.now())[17:19]

        filename = "RRF_" + "250100" + "_" + dateStr + "_" + timeStr + "_01_" + fileid + ".xml"

        filename_done = "RRF_" + "250100" + "_" + dateStr + "_" + timeStr + "_01_" + fileid + ".xml" + ".done"

        myfile = open(ach_out_dir + filename, "w")
        myfiledone = open(ach_out_dir + filename_done, "w")
        myfile.write(val)
        myfile.close()
        myfiledone.close()
    except Exception, e:
        logger.error(e)


def parseXMLRequest(stringToParse):
    '''
    This method receive a string argument and parse it to extract values from the
    xml requests. This method returns a dictionary.
    '''
    logger = alchemy.returnLogger()
    try:
        retDict = {}
        doc = parseString(stringToParse)
        doc.normalize()
        for e in doc.childNodes:
            if e.hasChildNodes():
                retDict[e.nodeName] = parseNode(e)

    except Exception, e:
        logger.error(e)

    return retDict


def parseNode(nodeToParse):
    '''
    Handles iteration through elements with child nodes
    '''
    retDict = {}
    retlist = []
    for e in nodeToParse.childNodes:
        nodelabel = e.nodeName
        if e.hasChildNodes() == True and e.childNodes.length == 1:
            retDict[nodelabel] = e.childNodes[0].nodeValue
        elif not e.hasChildNodes():
            retDict[nodelabel] = ''
        elif e.hasChildNodes() and e.childNodes.length > 1:
            retlist.append(parseNode(e))
            retDict[nodelabel] = retlist

    return retDict


def parseAttr(nodeToParse):
    pass


if __name__ == '__main__':
    print datetime.datetime.now()
    retDict = parseXMLRequestNew('D:\Windows.old.000\Users\Sunday\workspace\PythonTestBed\src\pythonxml\gipss.xml')
    print retDict
    fileFooter = retDict['{urn:schemas-ncr-com:ECPIX:CXF:FileStructure:040001}FileHeader'][
        '{urn:schemas-ncr-com:ECPIX:CXF:FileStructure:040001}FileSummary']
    buildAchXml(retDict, retDict['{urn:schemas-ncr-com:ECPIX:CXF:FileStructure:040001}FileHeader'][
        '{urn:schemas-ncr-com:ECPIX:CXF:FileStructure:040001}Item'], fileFooter[0], '080881', '24')
    retDict.pop('{urn:schemas-ncr-com:ECPIX:CXF:FileStructure:040001}FileHeader')
    print retDict
    print datetime.datetime.now()