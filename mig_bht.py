import psycopg2
import psycopg2.extras
import json
import time
from concurrent.futures import ThreadPoolExecutor

# -----------  CONSTANT  ------------

recovery_db_name = 'dummy'
recovery_db_user= 'dummy'
recovery_db_password='dummy'
recovery_db_port='dummy'
recovery_db_url = 'dummy'

write_db_name = 'dummy'
write_db_user = 'dummy'
write_db_password = 'dummy'
write_db_port = 'dummy'
write_db_url = 'dummy'

# ------------- READ - WRITE SPECIFIC VARIABLES
read_table_name = "case_links"
write_table_name = "case_links_bht_structure_from_stag"
offset = 0
data_limit = 10000
workers = 7
moving_data_size = 100000


# ------------- TABLE MAPPINGS (DONE via READ:WRITE) -----------

READ_WRITE_TABLE_MAPPING = {
    "id": "id",
    "company_id": "company_id",
    "loan_id": "loan_id",
    "notice_type": "notice_type",
    "document_type": "document_type",
    "status": "status",
    "s3_link": "s3_link",
    "s3_link_uuid": "s3_link_uuid",
    "data": "data",
    "updated": "updated",
    "created": "created",
    "author": "author",
    "role": "role",
    "allocation_month": "allocation_month",
    "is_closed": "is_closed",
    "stage_code": "stage_code",
    "case_type": "case_type",
    "is_in_case": "is_in_case",
    "case_id": "case_id",
    "iteration": "iteration",
    "archive": "archive",
    "is_linked_loan": "is_linked_loan",
    "linked_loan_id": "linked_loan_id",
    "local_pdf_file_name": "local_pdf_file_name",
    "primary_address": "primary_address",
    "batch_id": "batch_id",
    "tracking_id": "tracking_id",
    "notice_mode": "notice_mode",
    "notice_id": "notice_id",
    "author_id": "author_id"
}

# ---------- HELPER FUNCTIONS -------------

def check_and_form_db_connection():
    global recovery_connection
    global read_cursor

    if recovery_connection.closed:
        print(f"""
        ############# read connection formed again #############
        """)
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
        print(f"""
        ############# write connection formed again #############
        """)
        write_db_connection = psycopg2.connect(
        user=write_db_user,
        password=write_db_password,
        host=write_db_url,
        port=write_db_port,
        database=write_db_name)
        write_cursor = write_db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        write_db_connection.autocommit = True


def find_data_size_to_move():
    db_query = f"select count(id) as row_count FROM {read_table_name} WHERE document_type='Notice'"
    try:
        read_cursor.execute(db_query)
        row_result = read_cursor.fetchone()
        global moving_data_size
        moving_data_size = row_result['row_count']
        print('rows to move : ',moving_data_size)
        return moving_data_size
    except Exception as e:
        print(f"""

        print(f"====Failed to find the moving_data_size : {e}")

        """)
        raise Exception(e)


def get_all_data(mapping,offset):
    all_select_columns_for_read = ','.join(mapping.keys())
    db_query = f"select {all_select_columns_for_read} FROM {read_table_name} WHERE document_type='Notice' OFFSET {offset} LIMIT {data_limit}"
    print('/////reading-- ','data_limit:',data_limit,'offset:',offset)
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

write_db_connection = psycopg2.connect(
    user=write_db_user,
    password=write_db_password,
    host=write_db_url,
    port=write_db_port,
    database=write_db_name)
write_cursor = write_db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
write_db_connection.autocommit = True


#---------------------RUNNER------------

start_time = time.time()

def main(offset):
    check_and_form_db_connection()
    read_result = get_all_data(READ_WRITE_TABLE_MAPPING,offset)
    clean_result = clean_data(read_result)
    bulk_write_data(READ_WRITE_TABLE_MAPPING,clean_result,offset)
    completed_in = time.time()-start_time
    print('========process completed in =>',completed_in)


# MULTI-THREADING
"""
x=0
batch_list = []
while x<1000000:
    x=x+data_limit
    batch_list.append(x)

print(len(batch_list),batch_list)

with ThreadPoolExecutor(max_workers=workers) as executor:
    executor.map(main,batch_list)
"""


# SINGLE BATCH OPERATION
start_time = time.time()
check_and_form_db_connection()
moving_data_size = find_data_size_to_move()
x=0
batch_list = []
while x<=(moving_data_size+data_limit):
    x=x+data_limit
    batch_list.append(x)
    main(x)

print(f"""
----------------
process to read/write {moving_data_size} took {time.time()-start_time}
----------------
""")