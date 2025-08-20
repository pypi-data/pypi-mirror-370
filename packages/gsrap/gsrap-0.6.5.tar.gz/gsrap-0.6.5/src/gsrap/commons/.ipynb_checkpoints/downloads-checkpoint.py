import requests
import io
import threading
import time
import tempfile
import json
import glob


import gdown
import pandas as pnd



def get_dbuni(logger):
    
    
    sheet_id = "1dXJBIFjCghrdvQtxEOYlVNWAQU4mK-nqLWyDQeUZqek"
    #sheet_id = "1dCVOOnpNg7rK3iZmTDz3wybW7YrUNoClnqezT9Q5bpc" # alternative
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    response = requests.get(url)  # download the requested file
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)   # load into memory
        exceldb = pnd.ExcelFile(excel_data)
    else:
        logger.error(f"Error during download. Retry! If persists, please contact the developer.")
        return 1
    
    
    # check table presence
    sheet_names = exceldb.sheet_names
    for i in ['T', 'R', 'M', 'authors']: 
        if i not in sheet_names:
            logger.error(f"Sheet '{i}' is missing!")
            return 1
        
        
    # load the tables
    dbuni = {}
    dbuni['T'] = exceldb.parse('T')
    dbuni['R'] = exceldb.parse('R')
    dbuni['M'] = exceldb.parse('M')
    dbuni['authors'] = exceldb.parse('authors')
    
    
    # check table headers
    headers = {}
    headers['T'] = ['rid', 'rstring', 'kr', 'gpr_manual', 'name', 'author', 'notes']
    headers['R'] = ['rid', 'rstring', 'kr', 'gpr_manual', 'name', 'author', 'notes']
    headers['M'] = ['pure_mid', 'formula', 'charge', 'kc', 'name', 'inchikey', 'author', 'notes']
    headers['authors'] = ['username', 'first_name', 'last_name', 'role', 'mail']
    for i in dbuni.keys(): 
        if set(dbuni[i].columns) != set(headers[i]):
            logger.error(f"Sheet '{i}' is missing the columns {set(headers[i]) - set(dbuni[i].columns)}.")
            return 1
        
    return dbuni



def get_dbexp(logger):
    
    
    sheet_id = "1qGbIIipHJgYQjk3M0xDWKvnTkeInPoTeH9unDQkZPwg"
    #sheet_id = "1qxTRf30SeT9WJFYxWm2ChCxkTR0sTn7BbDOFhUuUQIE"   # alternative
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    response = requests.get(url)  # download the requested file
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)   # load into memory
        exceldb = pnd.ExcelFile(excel_data)
    else:
        logger.error(f"Error during download. Retry! If persists, please contact the developer.")
        return 1
    
    
    # check table presence
    sheet_names = exceldb.sheet_names
    for i in ['media', 'PM1', 'PM2A', 'PM3B', 'PM4A', 'MWF', 'DNA', 'RNA', 'PROTS', 'LIPIDS_PL', 'LIPIDS_FA', 'authors']: 
        if i not in sheet_names:
            logger.error(f"Sheet '{i}' is missing!")
            return 1
        
        
    # load the tables
    dbexp = {}
    dbexp['media'] = exceldb.parse('media')
    dbexp['PM1'] = exceldb.parse('PM1')
    dbexp['PM2A'] = exceldb.parse('PM2A')
    dbexp['PM3B'] = exceldb.parse('PM3B')
    dbexp['PM4A'] = exceldb.parse('PM4A')
    dbexp['MWF'] = exceldb.parse('MWF')
    dbexp['DNA'] = exceldb.parse('DNA')
    dbexp['RNA'] = exceldb.parse('RNA')
    dbexp['PROTS'] = exceldb.parse('PROTS')
    dbexp['LIPIDS_PL'] = exceldb.parse('LIPIDS_PL')
    dbexp['LIPIDS_FA'] = exceldb.parse('LIPIDS_FA')
    dbexp['authors'] = exceldb.parse('authors')
    
    
    # format tables (media):
    # assign substrates as index
    dbexp['media'].index = dbexp['media'].iloc[:, 1]
    # remove first 2 useless column (empty & substrates)
    dbexp['media'] = dbexp['media'].iloc[:, 2:]
    
    
    # format tables (Biolog(R)):
    for sheet in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        # assign wells as index
        dbexp[sheet].index = dbexp[sheet].iloc[:, 2]
        # remove first 3 useless columns
        dbexp[sheet] = dbexp[sheet].iloc[:, 3:]
        
        
    # format tables (biomass):
    dbexp['MWF'].index = dbexp['MWF'].iloc[:, 0]   # assign index
    dbexp['MWF'] = dbexp['MWF'].iloc[:, 1:]        # remove meaningless columns
    #
    dbexp['DNA'].index = dbexp['DNA'].iloc[:, 0]   # assign index
    dbexp['DNA'] = dbexp['DNA'].iloc[:, 1:]        # remove meaningless columns
    #
    dbexp['RNA'].index = dbexp['RNA'].iloc[:, 0]   # assign index
    dbexp['RNA'] = dbexp['RNA'].iloc[:, 1:]        # remove meaningless columns
    # 
    dbexp['PROTS'].index = dbexp['PROTS'].iloc[:, 1]   # assign index
    dbexp['PROTS'] = dbexp['PROTS'].iloc[:, 2:]        # remove meaningless columns
    #
    dbexp['LIPIDS_PL'].index = dbexp['LIPIDS_PL'].iloc[:, 1]   # assign index
    dbexp['LIPIDS_PL'] = dbexp['LIPIDS_PL'].iloc[:, 2:]        # remove meaningless columns
    #
    dbexp['LIPIDS_FA'].index = dbexp['LIPIDS_FA'].iloc[:, 1]   # assign index
    dbexp['LIPIDS_FA'] = dbexp['LIPIDS_FA'].iloc[:, 2:]        # remove meaningless columns
    
    
    return dbexp



def get_eschermap(logger):
    
    
    lastmap = dict()  
    
    
    folder_id = "1YE4l8IFL9pRgonAmFCf2SMRnpGJCHjil"
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"

    
    # the temporary folder (/tmp/on-the-fly-code) will be deleted once exiting the with statement
    with tempfile.TemporaryDirectory() as tmp_dir:
        
        # get available versions without downloading: 
        try: contents = gdown.download_folder(folder_url, output=tmp_dir, quiet=True, skip_download=True)
        except: 
            logger.error("Listing of available universal Escher map versions failed. Retry. If persists, please contact the developer.")
            return 1
        
        if len(contents) == 0:
            logger.error("Online folder 'universe.escher' seems empty. Please contact the developer.")
            return 1
        
        
        # get the last version
        files = {i.path: i.id for i in contents}
        files = dict(sorted(files.items()))   # sort keys in alphabetical order
        last_file_name = list(files.keys())[-1]
        last_file_id = files[last_file_name]
        lastmap['filename'] = last_file_name
        
        
        # download last version:
        try: pathfile_tmpfolder = gdown.download(id=last_file_id, output=f"{tmp_dir}/{last_file_name}", quiet=True)
        except: 
            logger.error("Downloading of last-version universal Escher map failed. Retry. If persists, please contact the developer.")
            return 1
        
        # load json
        with open(pathfile_tmpfolder, 'r') as file:
            json_data = json.load(file)
            lastmap['json'] = json_data

        
    return lastmap
        
    
    
def get_databases(logger): 
    
    
    def run_with_result(func, logger, results_dict, key):
        result = func(logger)
        results_dict[key] = result
        
    
    results_dict = dict()
    t1 = threading.Thread(target=run_with_result, args=(get_dbuni, logger, results_dict, 'dbuni'))
    t2 = threading.Thread(target=run_with_result, args=(get_dbexp, logger, results_dict, 'dbexp'))
    t3 = threading.Thread(target=run_with_result, args=(get_eschermap, logger, results_dict, 'eschermap'))

    
    # wait for the longest download (assess every 0.001 seconds):
    t1.start()
    t2.start()
    t3.start()
    while t1.is_alive() or t2.is_alive() or t3.is_alive():
        time.sleep(0.001)  

        
    if type(results_dict['dbuni'])==int:
        return 1
    if type(results_dict['dbexp'])==int:
        return 1
    if type(results_dict['eschermap'])==int:
        return 1
    return (results_dict['dbuni'], results_dict['dbexp'], results_dict['eschermap'])



def format_expansion(logger, eggnog):
    
    
    # linux/macos usually perform argument axpansion befor passing the parameter to python.
    if type(eggnog) == list: # already expanded by the terminal
        if len(eggnog)==1 and '*' in eggnog[0]:
            original_eggnog = eggnog[0]
            eggnog = glob.glob(eggnog[0])  # glob will append only existing files to the list
            if eggnog == []:
                logger.info(f"No file matching '{original_eggnog}'.")
    
    
    elif type(eggnog) == str:  # in the terminal, it can be specified by using single quotes
        original_eggnog = False
        if eggnog != '-': # user wanted to specify something
            original_eggnog = eggnog
        eggnog = glob.glob(eggnog)  # glob will append only existing files to the list
        if original_eggnog and eggnog == []:
            logger.info(f"No file matching '{original_eggnog}'.")
            
            
    if eggnog == [] or eggnog == ['-']:
        eggnog = '-'   # return always a list except for ths case
        
        
    return eggnog
    






