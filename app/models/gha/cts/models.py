from app import db
from sqlalchemy.orm import relationship


class CTSUploadedData(db.Model):
    itemseqno = db.Column(db.String(50), primary_key=True)
    batchid = db.Column(db.String(50))
    batch_instrument_count = db.Column(db.String(50))
    scannedmicr = db.Column(db.String(50))
    chequeno = db.Column(db.String(50))
    micraccountno = db.Column(db.String(50))
    micr = db.Column(db.String(50))
    transcationcode = db.Column(db.String(5))
    routingno = db.Column(db.String(10))
    amount = db.Column(db.Float)
    scandate = db.Column(db.String(50))
    presentmentdate = db.Column(db.String(50))
    accountno = db.Column(db.String(50))
    accountname = db.Column(db.String(50))
    accountstatus = db.Column(db.String(50))
    acc_catagory = db.Column(db.String(50))
    pbranchcode = db.Column(db.String(5))
    repair_modification_str = db.Column(db.String(50))
    scanstationid = db.Column(db.String(50))
    payin_slip_amount = db.Column(db.Float)
    clearing_cycle = db.Column(db.String(5))
    branch_user_remarks = db.Column(db.Text)
    branch_user = db.Column(db.String(50))
    branch_narration = db.Column(db.String(50))
    branchdiscardflag = db.Column(db.String(5))
    endorsementstring = db.Column(db.String(50))
    frontiqastring = db.Column(db.String(50))
    doctype = db.Column(db.String(5))
    pbankroutingno = db.Column(db.String(10))
    imageserverip = db.Column(db.String(50))
    siteid = db.Column(db.String(50))
    volumeid = db.Column(db.String(50))
    volumename = db.Column(db.String(50))
    cabinetname = db.Column(db.String(50))
    presenting_bank_name = db.Column(db.String(50))
    iqadecision = db.Column(db.String(20))
    reariqastring = db.Column(db.String(20))
    pbranchname = db.Column(db.Text)
    param_1 = db.Column(db.String(50))
    frontimagepath = db.Column(db.Text)
    backimagepath = db.Column(db.Text)
    frontimage = db.Column(db.LargeBinary)
    backimage = db.Column(db.LargeBinary)
    pri_id = db.Column(db.Float)
    user_modified = db.Column(db.String(50))
    status = db.Column(db.String(20))


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseUploadedData %r>' % (self.itemseqno)



class CTSRejectCodesDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.String(20))
    description = db.Column(db.Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseRejectCodesDetails %r>' % (self.id)

class CTSInwardCheque(db.Model):
    uniqueid = db.Column(db.Integer, primary_key = True)
    itemseqno = db.Column(db.String(20), unique = True)
    amount = db.Column(db.Float)
    accountno = db.Column(db.String(20))
    serialno = db.Column(db.String(20))
    transcode = db.Column(db.String(5))
    presentingbankroutno = db.Column(db.String(20))
    presentmentdate = db.Column(db.String(20))
    cycleno = db.Column(db.String(20))
    clearingtype = db.Column(db.String(20))
    doctype = db.Column(db.String(20))
    doctype = db.Column(db.String(20))
    micrrepairflags = db.Column(db.String(20))
    specialhandling = db.Column(db.String(20))
    truncatingrtno = db.Column(db.String(20))
    iqaignoreind = db.Column(db.String(20))
    currencyind = db.Column(db.String(20))
    instrumenttype = db.Column(db.String(20))
    bofdroutno = db.Column(db.String(20))
    bofdbusdate = db.Column(db.String(20))
    depositoracct = db.Column(db.String(20))
    transdetail = db.Column(db.Text)
    creationdate = db.Column(db.String(20))
    creationtime = db.Column(db.String(20))
    fileid = db.Column(db.String(20))
    status = db.Column(db.String(20))
    payeename = db.Column(db.Text)
    payername = db.Column(db.String(20))
    cashvalueind = db.Column(db.String(20))
    representmentcnt = db.Column(db.String(5))
    payorbankroutno = db.Column(db.String(20))
    sessionnumber = db.Column(db.String(20))
    sessiondate = db.Column(db.String(20))
    returnreason = db.Column(db.String(20))
    returnreasoncomment = db.Column(db.String(20))
    corr_id = db.Column(db.String(20))
    max_decision_period = db.Column(db.String(5))
    item_status = db.Column(db.String(20))
    bundle_id = db.Column(db.String(20))
    cash_letterid = db.Column(db.String(20))
    accountname = db.Column(db.String(50))
    acct_status = db.Column(db.String(50))
    fileid_out = db.Column(db.String(50))
    date_created = db.Column(db.String(20))
    user_created = db.Column(db.String(20))
    collection_type = db.Column(db.String(20))
    user_modified = db.Column(db.String(50))
    auth_user = db.Column(db.String(50))
    auth_status = db.Column(db.String(1))
    date_modified = db.Column(db.String(20))
    time_modified = db.Column(db.String(10))
    micrcode = db.Column(db.String(10))
    amountinwords = db.Column(db.Text)
    incoming_file_name = db.Column(db.Text)
    accepted = db.Column(db.String(5))
    refer = db.Column(db.String(5))
    rejected = db.Column(db.String(5))
    remarks = db.Column(db.Text)
    instrcategory = db.Column(db.String(5))
    cbsstatus = db.Column(db.String(5))
    refer_reason = db.Column(db.String(20))
    refer_comment = db.Column(db.Text)
    fcy = db.Column(db.String(5))
    eod_status = db.Column(db.String(5))
    res_status = db.Column(db.String(10))
    rej_file = db.Column(db.Text)
    timestamp = db.Column(db.String(20))
    cbsno = db.Column(db.String(50))
    cbs_error_msg = db.Column(db.Text)
    cbs_rev_no = db.Column(db.String(20))
    cbs_rev_error_msg = db.Column(db.Text)


    image_details = db.relationship('CTSImageDetail',
                                backref=db.backref('owner',
                                                   lazy='dynamic'))



    def __repr__(self):
        return '<CTSInwardCheque %r, %r>' % (self.uniqueid, self.itemseqno)


class CTSImageDetail(db.Model):
    image_detail_id = db.Column(db.Integer, primary_key=True)
    itemseqno = db.Column(db.String(20))
    cash_letterid = db.Column(db.String(20))
    bundle_id = db.Column(db.String(20))
    viewformat = db.Column(db.String(20))
    compressiontype = db.Column(db.String(20))
    viewdescriptor = db.Column(db.String(20))
    imageavailable = db.Column(db.String(20))
    imagecreatorrouteno = db.Column(db.String(20))
    imagecreationdate = db.Column(db.String(20))
    imagedatalength = db.Column(db.Integer)
    imagedataoffset = db.Column(db.Integer)
    filename = db.Column(db.Text)
    imagereferencekeylength = db.Column(db.Integer)
    clippingorigin = db.Column(db.String(20))
    source = db.Column(db.String(20))
    imagereferencedata = db.Column(db.String(20))
    imagequality = db.Column(db.Integer)
    imageusability = db.Column(db.String(20))
    imagingbankspecifictest = db.Column(db.String(20))
    userfield = db.Column(db.String(50))
    imageprocessed = db.Column(db.String(50))
    pictype = db.Column(db.String(20))
    imgtemfilename = db.Column(db.Text)
    imagedata = db.Column(db.LargeBinary)
    pic_index = db.Column(db.Integer)
    image_display = db.Column(db.LargeBinary)
    uniqueid = db.Column(db.Integer, db.ForeignKey('cts_inward_cheque.uniqueid'))

    def preprocessor(data):
        for i, img in enumerate(data['image_details']):
            data['image_details'][i]['imagedata'] = str(img['imagedata'])
        #json.dumps(data, use_decimal=True)
        return data



    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<ImageDetail %r, %r>' % (self.itemseqno, self.uniqueid)


class CTSBankRoutingNo(db.Model):
    bank_routing_nbr = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    street_address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state_province = db.Column(db.String(20))
    country = db.Column(db.String(20))
    postal_zip_code = db.Column(db.String(20))
    clearing_status_code = db.Column(db.String(20))
    note = db.Column(db.Text)
    service_branch_routing_nbr = db.Column(db.String(20))
    designated_branch_routing_nbr = db.Column(db.String(20))
    central_bank_code = db.Column(db.String(20))

    bank_branches = db.relationship('CTSBranchRoutingNo',
                                backref=db.backref('owner',
                                                   lazy='dynamic'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<CTSBankRoutingNo %r>' % (self.bank_routing_nbr)


class CTSBranchRoutingNo(db.Model):
    branch_routing_nbr = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    street_address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state_province = db.Column(db.String(20))
    country = db.Column(db.String(20))
    postal_zip_code = db.Column(db.String(20))
    branch_number = db.Column(db.String(20))
    note = db.Column(db.Text)
    bank_routing_nbr = db.Column(db.String(20), db.ForeignKey('cts_bank_routing_no.bank_routing_nbr'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<BaseBankRoutingNo %r>' % (self.bank_routing_nbr)

class CTSOutwardCheque(db.Model):
    itemseqno = db.Column(db.String(20), primary_key=True)
    amount = db.Column(db.Float)
    accountno = db.Column(db.String(20))
    serialno = db.Column(db.String(20))
    transcode = db.Column(db.String(5))
    presentingbankroutno = db.Column(db.String(20))
    presentmentdate = db.Column(db.String(20))
    cycleno = db.Column(db.String(10))
    clearingtype = db.Column(db.String(10))
    doctype = db.Column(db.String(10))
    micrrepairflags = db.Column(db.String(10))
    specialhandling = db.Column(db.String(10))
    truncatingrtno = db.Column(db.String(10))
    iqaignoreind = db.Column(db.String(10))
    currencyind = db.Column(db.String(10))
    instrumenttype = db.Column(db.String(10))
    bofdroutno = db.Column(db.String(10))
    bofdbusdate = db.Column(db.String(20))
    depositoracct = db.Column(db.String(20))
    transdetail = db.Column(db.Text)
    creationdate = db.Column(db.String(10))
    creationtime = db.Column(db.String(10))
    fileid = db.Column(db.String(10))
    status = db.Column(db.String(10))
    payeename = db.Column(db.Text)
    payername = db.Column(db.Text)
    cashvalueind = db.Column(db.String(5))
    representmentcnt = db.Column(db.String(5))
    payorbankroutno = db.Column(db.String(10))
    sessionnumber = db.Column(db.String(10))
    sessiondate  = db.Column(db.String(10))
    date_created = db.Column(db.String(20))
    time_created = db.Column(db.String(20))
    user_created  = db.Column(db.String(50))
    gefu_txn_type = db.Column(db.String(10))
    gefu_acct_type = db.Column(db.String(10))
    acct_status = db.Column(db.String(50))
    accountname = db.Column(db.Text)
    item_status = db.Column(db.String(15))
    returnreason = db.Column(db.String(5))
    collection_type = db.Column(db.String(5))
    returnfileid = db.Column(db.String(5))
    upload_fileid = db.Column(db.String(20))
    user_modified = db.Column(db.String(50))
    auth_user = db.Column(db.String(50))
    auth_status = db.Column(db.String(1))
    date_modified = db.Column(db.String(20))
    time_modified = db.Column(db.String(10))
    instr_category = db.Column(db.String(5))
    rejected = db.Column(db.String(5))
    refer = db.Column(db.String(5))
    accepted = db.Column(db.String(5))
    uniqueid = db.Column(db.Float)
    eod_status = db.Column(db.String(10))
    fcy = db.Column(db.String(5))
    res_status = db.Column(db.String(10))
    filename = db.Column(db.Text)
    inent = db.Column(db.String(2))
    timestamp = db.Column(db.String(20))
    cbsstatus = db.Column(db.String(5))
    cbs_error_msg = db.Column(db.Text)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<CTSOutwardCheque %r>' % (self.itemseqno)
