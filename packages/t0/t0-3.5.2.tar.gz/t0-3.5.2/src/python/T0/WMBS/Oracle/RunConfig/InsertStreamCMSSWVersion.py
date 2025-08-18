"""
_InsertStreamCMSSWVersion_

Oracle implementation of InsertStreamCMSSWVersion

"""

from WMCore.Database.DBFormatter import DBFormatter

class InsertStreamCMSSWVersion(DBFormatter):

    def execute(self, binds, conn = None, transaction = False):

        sql = """DECLARE
                   cnt NUMBER(1);
                 BEGIN
                   SELECT COUNT(*)
                   INTO cnt
                   FROM run_stream_cmssw_assoc
                   WHERE run_id = :RUN
                   AND stream_id = (SELECT id FROM stream WHERE name = :STREAM)
                   ;
                   IF (cnt = 0)
                   THEN
                     INSERT INTO run_stream_cmssw_assoc
                     (RUN_ID, STREAM_ID, ONLINE_VERSION)
                     SELECT :RUN,
                            (SELECT id FROM stream WHERE name = :STREAM),
                            id
                     FROM cmssw_version
                     WHERE name = :VERSION
                     ;
                   END IF;
                 EXCEPTION
                   WHEN DUP_VAL_ON_INDEX THEN NULL;
                 END;
                 """

        self.dbi.processData(sql, binds, conn = conn,
                             transaction = transaction)

        return
