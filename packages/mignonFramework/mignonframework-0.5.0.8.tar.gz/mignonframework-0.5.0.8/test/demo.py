from mignonFramework import jsonContrast, Logger



js1 = {"id": 4, "hazardCode": "12", "hazardName": "1", "hazardType": "船舶故障", "discoveryTime": "2025-07-10 00:00:00",
       "discoveryLocation": "1", "hazardDescription": "1", "reportingUnit": "1", "auditStatus": "1",
       "reviewStatus": "1", "assignedUnit": "1", "assignmentTime": "2025-07-15 00:00:00", "rectificationStatus": "1",
       "rectificationFeedback": None, "rectificationAttachment": "1", "finalStatus": "11", "remarks": None,
       "createBy": "1", "updateBy": "1", "createTime": "2025-08-12 14:42:19", "updateTime": "2025-08-12 14:42:19",
       "deleted": 0, "status": 1}

js2 = {"id": 4, "hazardCode": "12", "hazardName": "1", "hazardType": "船舶故障", "discoveryTime": "2025-07-10 00:00:00",
       "discoveryLocation": "1", "hazardDescription": "1", "reportingUnit": "1", "auditStatus": "1",
       "reviewStatus": "1", "assignedUnit": "1", "assignmentTime": "2025-07-15 00:00:00", "rectificationStatus": "1",
       "rectificationFeedback": None, "rectificationAttachment": "1", "finalStatus": "11", "remarks": "1",
       "createBy": "1", "updateBy": "1", "createTime": "2025-08-12 14:42:19", "updateTime": "2025-08-12 14:42:19",
       "deleted": 0, "status": 1}


jsonContrast(js1, js2)