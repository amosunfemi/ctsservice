__author__ = 'sundayamosun'


#SEQUENCES
#CONVENTION IS APPLICATION NAME FOLLOWED BY DB OBJECT TYPE AND NAME

CTS_SEQ_OUTFILE_ID="select nextval('cts_outfileid_seq')"
CTS_OUTWARDITEM_COUNT="select count(*) from cts_outward_cheque where date_created=:date_created"
LARGE_FLD_TEST="select * from cts_inward_cheque"
DB_TYPE="POSTGRESQL"
