# form connection DONE
# get data
    # >>------- support dynamic length
    # create threads
        # create worker
        # send data to worker
    #log when error, but retry it again in the last - queue



from asyncore import read
from glob import glob
from itertools import count
import psycopg2
import psycopg2.extras
import json
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

# FOR ENV VARIBLES
# from os import getenv
# from dotenv import find_dotenv, load_dotenv
# load_dotenv(find_dotenv())

# -----------  CONSTANT  ------------

recovery_db_name = 'DUMMY'
recovery_db_user=  'DUMMY'
recovery_db_password=  'DUMMY'
recovery_db_port=  'DUMMY'
recovery_db_url =  'DUMMY'

write_db_name =  'DUMMY'
write_db_user =  'DUMMY'
write_db_password =  'DUMMY'
write_db_port =  'DUMMY'
write_db_url =  'DUMMY'

# ------------- READ - WRITE SPECIFIC VARIABLES
read_table_name = "drafts"
write_table_name = "drafts_dummy"
offset = 0
data_limit = 1000
workers = 7
ROWS_TO_BE_APPENDED = 10000

# ------------- TABLE MAPPINGS (DONE via READ:WRITE) -----------

READ_WRITE_TABLE_MAPPING = {
    "id": "id",
    "draft_id": "draft_id",
    "company_id": "company_id",
    "notice_type": "notice_type",
    "document_type": "document_type",
    "archive": "archive",
    "author": "author",
    "role": "role",
    "updated": "updated",
    "created": "created",
    "author": "author",
    "draft_name": "draft_name",
    "case_type": "case_type",
    "is_vernacular": "is_vernacular",
    "author_id": "author_id",
    "language": "language",
    "s3_path": "s3_path",
    "is_deleted": "is_deleted",
}

# ---------- INITIALIZATION -------------

def check_and_form_db_connection():
    global recovery_connection
    global read_cursor

    if recovery_connection.closed:
        recovery_connection = psycopg2.connect(
        user=recovery_db_user,
        password=recovery_db_password,
        host=recovery_db_url,
        port=recovery_db_port,
        database=recovery_db_name)
        recovery_connection.autocommit = False
        read_cursor = recovery_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    global write_cursor
    global write_db_connection
    if write_db_connection.closed:
        write_db_connection = psycopg2.connect(
        user=write_db_user,
        password=write_db_password,
        host=write_db_url,
        port=write_db_port,
        database=write_db_name)
        write_cursor = write_db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        write_db_connection.autocommit = True


def get_all_data(mapping,offset):
    all_select_columns_for_read = ','.join(mapping.keys())
    db_query = f"select {all_select_columns_for_read} FROM {read_table_name} OFFSET {offset} LIMIT {data_limit}"
    print('////////reading-- ','data_limit:',data_limit,'offset:',offset)
    print(f'{db_query}')
    try:
        read_result = []
        read_cursor.execute(db_query)
        rows_result = read_cursor.fetchall()
        for row in rows_result:
            read_result.append(dict(row))
        return read_result
    except Exception as e:
        print(f"""

        print(f"====Failed to read data from {recovery_db_name} : {e}")
        offset : {offset}
        data_limit : {data_limit}

        """)
        raise Exception(e)


def clean_data(read_result):
    prod_result = []
    for row_dict in read_result:
        for key in row_dict:
            if isinstance(row_dict[key],dict):
                row_dict[key] = json.dumps(row_dict[key])

        row_as_list = tuple(row_dict.values())
        prod_result.append(row_as_list)
    return prod_result


def bulk_write_data(mapping,values_list,offset):
    write_columns = ','.join(mapping.values())
    write_query = f"INSERT INTO {write_table_name}({write_columns}) VALUES%s"
    print('|||||writing---','data_limit:',data_limit,'offset:',offset)

    try:
        psycopg2.extras.execute_values(write_cursor, write_query, values_list)
        write_db_connection.commit()
    except Exception as e:
        print(f"""
        
        ==========Failed to write data to {write_db_name} : {e}
        offset : {offset}
        data_limit : {data_limit}

        """)
        raise Exception(e)

# ------------- DATABASE CONNECTIVITY -----------

recovery_connection = psycopg2.connect(
    user=recovery_db_user,
    password=recovery_db_password,
    host=recovery_db_url,
    port=recovery_db_port,
    database=recovery_db_name)
recovery_connection.autocommit = False
read_cursor = recovery_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
# read_cursor = recovery_connection.cursor()

write_db_connection = psycopg2.connect(
    user=write_db_user,
    password=write_db_password,
    host=write_db_url,
    port=write_db_port,
    database=write_db_name)
write_cursor = write_db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
write_db_connection.autocommit = True


#---------------------ADD THIS IN LOOP or QUEUE------------

start_time = time.time()

def main(offset):
    check_and_form_db_connection()
    read_result = get_all_data(READ_WRITE_TABLE_MAPPING,offset)
    clean_result = clean_data(read_result)
    bulk_write_data(READ_WRITE_TABLE_MAPPING,clean_result,offset)
    completed_in = time.time()-start_time
    print('========process completed in =>',completed_in)



# MULTI-THREADING
# x=0
# batch_list = []
# while x<ROWS_TO_BE_APPENDED:
#     batch_list.append(x)
#     x=x+data_limit

# print(len(batch_list),batch_list)

# with ThreadPoolExecutor(max_workers=workers) as executor:
#     executor.map(main,batch_list)


# SINGLE BATCH OPERATION
x=0
batch_list = []
while x<ROWS_TO_BE_APPENDED:
    batch_list.append(x)
    main(x)
    x=x+data_limit
