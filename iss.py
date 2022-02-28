import urllib.request
import requests
import time
import json 
from pathlib import Path
import sys, os
from datetime import datetime
import time
import io
import time
import os
import subprocess
import sys
import pandas as pd

def get_iss():
    seconds = 60*60
    mi_p_km = 1/1.609344
    iss_at = 'https://api.wheretheiss.at/v1/satellites/25544'
    try:
        iss_at = json.loads(requests.get(iss_at).text)
        iss_at['miles_per_second']=(iss_at['velocity']/seconds)* mi_p_km
        iss_at['converted_to_unit']='Miles'
        iss_at['converted_to_unit']='Seconds'
        print(f'current = {iss_at}')
        return iss_at 
    except requests.exceptions.RequestException as e:
        iss_at = { }
        iss_at['error'] = f'output is {e}'
        print(f'current = {iss_at}')
        return iss_at 

def json_process(iss_dict,did=None, home=None):
    log_time = datetime.fromtimestamp(time.time())
    log_time = log_time.ctime()
    print(log_time)
    if not did:
        did = home/'satelite'
        fid = did/'iss_logs.json'
    if did:
        fid = did/'iss_logs.json'
    
    if fid.exists():
        with open(fid,'r') as handle:
            iss_current =  json.load(handle)
    else:
        did.mkdir(exist_ok=True, parents=True)
        iss_current = { }
    iss_current[log_time]=iss_dict
    return iss_current, fid 

def to_html(current, did):
    df = pd.DataFrame.from_dict(current).T
    html = df.to_html()
    fid = did/'table.html'
    with open(fid,'w') as handle:
        handle.writelines(html)
    return html

def main(json_process = None, 
         get_iss = None,
         to_html = None,
         did = None):
    home = Path(os.path.expanduser('~'))
    if did:
        did = home/did
    else:
        did = home/'backup'
    iss_at = get_iss()
    #print(f' new {iss_at} \n\n')
    current, fid = json_process(iss_at,did,home)    
    with open(fid,'w') as handle:
            json.dump(current,handle)
    if to_html:
        html = to_html(current,did)
    line = '-'*20
    #print(f'{line} \ncurrent = {current}')
    return current

args = {
    'json_process':json_process,
    'get_iss':get_iss,
    'to_html':None,
    'did':'satelite'
}   

data = main(**args)


def run_process(process = None, command = None,fid = None):
    logname = '.log'
    env = os.environ.copy()
    with io.open(logname, 'wb') as writer, io.open(logname, 'rb', 0) as reader:
        process = subprocess.Popen(command, stdout=writer, shell=True, env=env)
        while process.poll() is None:
            sys.stdout.write(reader.read().decode('utf-8'))
            reader.read().decode('utf-8')
            sys.stdout.write(reader.read().decode('utf-8'))
        # Read the remaining
    with open(fid,'r') as hndl:
        data = json.load(hndl)
        data = pd.DataFrame.from_dict(data).T
    return data
