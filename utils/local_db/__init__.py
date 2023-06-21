# DOCS : https://tinydb.readthedocs.io/en/latest/usage.html#updating-data
import os
from tinydb import TinyDB, Query, where
from tinydb.operations import add, delete, set, subtract
from tinydb.table import Document

def db_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)

#----- USE DIFF JSON FILES FRO DB -----
results_db = TinyDB(db_file_path('results.json'), indent=4)
analyte_db = TinyDB(db_file_path('analytes.json'), indent=4)


#----- METHODS -----------------------------
def new_requisition(item):
    # if requisition_id already exists  => append new data to test_results list
    # else if requisition_id is new one => insert into db
    try:
        condition = where('requisition_id') == item['requisition_id']
        if results_db.search(condition):
            results_db.upsert(lambda x: x['test_results'].append(item['test_results'][0]), condition)
        else:
            results_db.insert(item)
    except Exception as e:
        print(e)
    pass

def get_all_requisitions():
    try:
        return results_db.all()
    except Exception as e:
        print(e)
    pass

def new_analyte(item, table): # table = self.id
    try:
        if analyte_db.table(table).search(where('batch_id') == item['batch_id']):
            return False # WARN USER
        else:
            analyte_db.table(table).insert(item)
            return True
    except Exception as e:
        print(e)
    pass

#=================ITEM FORMATS=============
"""
FOR results_db
data = {
	'requisition_id': '',
	'test_results: [{
		'test_name'	: '',	# CRP, PCT, IL8, etc.,
		'value'		: '',	# float
		'calibration_id': '',	# string » ‘21_1’
		'normal_range'	: '',	# string
		'timestamp'	: '',	# either in milliseconds or formated “02/01/2021 01:22:30 PM”
		'image'		: ''	# string in base64
	}]
}

FOR analyte_db
data = {
	'test_name'		: '',
	'batch_id'	: '',
	'cal_id'	: '',
	'manufacturer'	: ''
}
"""
