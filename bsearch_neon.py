#!/usr/bin/env python3
import psycopg2
import requests
import os
import time

# We know that, e.g. three days ago everything was fine. It is possible to
# mannualy create a branch at specific time with UI and get it's LSN.
start = 0x2EB3898
# Last lsn, `select pg_current_wal_flush_lsn()`
end   = 0x3779AD8

# Database info
project = "silent-morning-200885"
db_creds = f"kelvich:{os.environ['PGPASSWORD']}"
headers = {
    "Authorization": f"Bearer {os.environ['NEON_API_KEY']}",
    "Content-Type": "application/json"
}

def query_branch(query, branch):
    endpoint_name = branch['endpoints'][0]['id']
    connstr = f"postgres://{db_creds}@{endpoint_name}.eu-central-1.aws.neon.tech/neondb"
    conn = psycopg2.connect(connstr)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    print(f"Checking \"{query}\" at lsn \"{branch['branch']['parent_lsn']}\": -> {result}")
    return result

def create_branch(parent_id, lsn):
    branch = requests.post(f'https://console.neon.tech/api/v2/projects/{project}/branches',
        headers=headers,
        data=f'{{"endpoints":[{{"type":"read_write"}}],"branch":{{"name":"branch_{lsn}","parent_id":"{parent_id}","parent_lsn":"{lsn}"}}}}'
    ).json()
    print(f"Creating branch at lsn = {lsn}")
    return branch

def delete_branch(branch, lsn):
    branch_id = branch['branch']['id']
    branch = requests.delete(f'https://console.neon.tech/api/v2/projects/{project}/branches/{branch_id}',
        headers=headers
    ).json()
    print(f"Deleted branch at lsn = {lsn}")
    time.sleep(2)
    return branch

def query_at_lsn(parent_id, query, lsni):
    lsn = f"0/{lsni:X}"
    branch = create_branch(parent_id, lsn)
    ret = query_branch(query, branch)
    delete_branch(branch, lsn)
    return ret

def bsearch_rightmost(parent_id, l, r, query):
    while l < r:
        m = (l + r)//2
        if query_at_lsn(parent_id, query, m):
            l = m + 1
        else:
            r = m
    print(f"Converged at 0/{l:X}")

# Find out name of the main branch
resp = requests.get(f'https://console.neon.tech/api/v2/projects/{project}/branches', headers=headers)
main_branch_id = next(b for b in (resp.json()['branches']) if b['name'] == "main")["id"]
print(f"Main branch id is: \"{main_branch_id}\"")

# Do the bsearch
bsearch_rightmost(main_branch_id, start, end, "SELECT count(*) > 1 FROM users")
print("Finishing")
