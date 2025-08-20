import time
import random
import os
import sys
import glob
import pickle
import copy


import pandas as pnd
from Bio.KEGG import REST
from Bio.KEGG.KGML import KGML_parser
#from Bio.Graphics.KGML_vis import KGMLCanvas   # <-- riquires reportlab



def download_raw_txtfiles(logger, outdir, usecache):
    

    # generate a README reporting the KEGG version number
    time.sleep(0.5)
    res_string = REST.kegg_info('kegg').read()
    RELEASE_kegg = copy.deepcopy(res_string)
    with open(f"{outdir}/kdown/RELEASE.txt", "w") as file:
        file.write(res_string)



    # get the list of the items included in the different databases: 
    databases = [
        'reaction',
        'compound',
        'enzyme',  # ec
        'orthology',
        'module', 
        'pathway',
    ]
    for db in databases:
        time.sleep(0.5)
        res_string = REST.kegg_list(db).read()
        with open(f"{outdir}/kdown/{db}.txt", "w") as file:
            file.write(res_string)



    # mix the items to download to be respectful/compliant
    items_to_download = []

    for db in databases:
        with open(f"{outdir}/kdown/{db}.txt", 'r') as file:
            res_string = file.read()
            rows = res_string.split('\n')
            for row in rows:
                item_id = row.split('\t', 1)[0]
                if item_id == '': continue
                items_to_download.append({'db': db, 'id': item_id})

    random.shuffle(items_to_download)



    # download the items
    for item in items_to_download:
        if usecache:
            if os.path.isfile(f"{outdir}/kdown/{item['db']}/{item['id']}.txt"):
                continue  # already downloaded, don't waste time
        time.sleep(0.5)
        try:
            res_string = REST.kegg_get(f"{item['db']}:{item['id']}").read()
        except: 
            logger.info(f"An error occurred during kegg_get of item {item['db']}:{item['id']}. Skipping the item.")
            continue
        os.makedirs(f"{outdir}/kdown/{item['db']}", exist_ok=True)
        with open(f"{outdir}/kdown/{item['db']}/{item['id']}.txt", "w") as file:
            file.write(res_string)
            
               
    return RELEASE_kegg



def create_dict_ko(logger, outdir):
    
    dict_ko = {}         # main output
    dict_headers = {}   # to track the available headers
    
    
    for file in glob.glob(f'{outdir}/kdown/orthology/K*.txt'):
        
        
        # create new item: 
        ko_id = file.rsplit('/', 1)[-1].replace('.txt', '')
        if ko_id not in dict_ko.keys():  
            dict_ko[ko_id] = {
                'kr_ids': set(),
                'symbols': set(),
                'name': None,
                'ecs': set(),
                'cogs': set(),
                'gos': set(),
            }   
        else:
            logger.error(f"{ko_id} already included!")
            return 1
        
        
        # read associated text file: 
        with open(file, 'r') as r_handler:
            file_content = r_handler.read().strip()
            
            
            # split rows:
            rows = file_content.split('\n')
            curr_header = None
            for row in rows:
                
                
                # track the headers
                header = row[:12]
                if header not in dict_headers.keys():
                    dict_headers[header] = {}
                    dict_headers[header]['cnt'] = 0
                    dict_headers[header]['ko_ids'] = set()
                dict_headers[header]['cnt'] += 1
                dict_headers[header]['ko_ids'].add(ko_id)
                
                
                # get the content
                if header == '///':
                    continue    # should be the end of the file
                if header != curr_header and header != '            ':
                    curr_header = header
                content = row[12:]
                
                
                # parse the entry: 
                if curr_header == 'ENTRY       ':
                    ko_id_content = content.strip().split(' ', 1)[0]
                    if ko_id_content != ko_id: 
                        logger.info(f"{ko_id} appears with a different ID in its file ({ko_id_content}).")
                        #return 1
                        
                        
                # parse the gene symbols
                if curr_header == 'SYMBOL      ':
                    symbols = content.strip().split(', ')
                    for symbol in symbols: 
                        if '.' in symbol:
                            continue 
                        dict_ko[ko_id]['symbols'].add(symbol)
                    # guarantee at least 1 symbol:
                    if dict_ko[ko_id]['symbols'] == set():
                        dict_ko[ko_id]['symbols'] = set([ko_id])
                        
                
                # parse the name / ECs
                if curr_header == 'NAME        ':
                    if '[' in content:
                        name = content.rsplit('[', 1)[0].strip()
                    else: name = content.strip()
                    dict_ko[ko_id]['name'] = name
                    if '[EC:' in content: 
                        ecs = content.rsplit('[EC:', 1)[1].replace(']','').split(' ')
                        for ec in ecs:
                            dict_ko[ko_id]['ecs'].add(ec)
                        
                        
                # parse the COG / GO terms
                if curr_header == 'DBLINKS     ':
                    if content.startswith('COG: '):
                        cogs = content[len('COG: '):].strip().split(' ')
                        for cog in cogs:
                            dict_ko[ko_id]['cogs'].add(cog)
                    if content.startswith('GO: '):
                        gos = content[len('GO: '):].strip().split(' ')
                        for go in gos:
                            dict_ko[ko_id]['gos'].add(go)
                        
                        
                # parse the reactions
                if curr_header == 'REACTION    ':
                    kr_ids = content.split(' ')
                    kr_ids = [i.strip() for i in kr_ids]
                    kr_ids = [i for i in kr_ids if i != '']
                    for kr_id in kr_ids: 
                        if len(kr_id)!=6 or kr_id[0]!='R':
                            #logger.info(f'{ko_id} is linked to a badly formatted reaction ID: {kr_id}.')
                            continue
                        else:
                            dict_ko[ko_id]['kr_ids'].add(kr_id)
                  
            
    logger.info(f'Number of unique items (K): {len(dict_ko.keys())}.')
    logger.debug('Metrics (K):\n\n'+ ''.join([f"'{header}': {dict_headers[header]['cnt']}\n" for header in dict_headers.keys()]))
    
    
    return dict_ko



def create_dict_c(logger, outdir):
    
    dict_c = {}         # main output
    dict_headers = {}   # to track the available headers
    
    
    for file in glob.glob(f'{outdir}/kdown/compound/C*.txt'):
        
        
        # create new item: 
        kc_id = file.rsplit('/', 1)[-1].replace('.txt', '')
        if kc_id not in dict_c.keys():  
            dict_c[kc_id] = {
                'kr_ids': set(), 
                'map_ids': set(), 
                'md_ids': set()
            }   
        else:
            logger.error(f"{kc_id} already included!")
            return 1
        
        
        # read associated text file: 
        with open(file, 'r') as r_handler:
            file_content = r_handler.read().strip()
            
            
            # split rows:
            rows = file_content.split('\n')
            curr_header = None
            for row in rows:
                
                
                # track the headers
                header = row[:12]
                if header not in dict_headers.keys():
                    dict_headers[header] = {}
                    dict_headers[header]['cnt'] = 0
                    dict_headers[header]['kc_ids'] = set()
                dict_headers[header]['cnt'] += 1
                dict_headers[header]['kc_ids'].add(kc_id)
                
                
                # get the content
                if header == '///':
                    continue    # should be the end of the file
                if header != curr_header and header != '            ':
                    curr_header = header
                content = row[12:]
                
                
                # parse the entry: 
                if curr_header == 'ENTRY       ':
                    kc_id_content = content.strip().split(' ', 1)[0]
                    if kc_id_content != kc_id: 
                        logger.info(f"{kc_id} appears with a different ID in its file ({kc_id_content}).")
                        #return 1
                        
                        
                # parse the reactions
                if curr_header == 'REACTION    ':
                    kr_ids = content.split(' ')
                    kr_ids = [i.strip() for i in kr_ids]
                    kr_ids = [i for i in kr_ids if i != '']
                    for kr_id in kr_ids: 
                        if len(kr_id)!=6 or kr_id[0]!='R':
                            logger.info(f'{kc_id} is linked to a badly formatted reaction ID: {kr_id}.')
                        else:
                            dict_c[kc_id]['kr_ids'].add(kr_id)
                        
                
                # parse maps (pathways)
                if curr_header == 'PATHWAY     ':
                    map_id = content.strip().split(' ')[0]    # one per row
                    if len(map_id)!=8 or map_id[:3]!='map':
                        # handle cases like eg "map01100(G00003)" (C05860)
                        if len(map_id)!=16 or map_id[8:10]!='(G' or map_id[15]!=')':
                            logger.info(f'{kc_id} is linked to a badly formatted pathway ID: {map_id}.')
                        else:
                            map_id = map_id[:8]
                            dict_c[kc_id]['map_ids'].add(map_id)
                    else:
                        dict_c[kc_id]['map_ids'].add(map_id)
                        
                            
                # parse modules 
                if curr_header == 'MODULE      ':
                    md_id = content.strip().split(' ')[0]    # one per row
                    if len(md_id)!=6 or md_id[0]!='M':
                        logger.info(f'{kc_id} is linked to a badly formatted module ID: {md_id}.')
                    else:
                        dict_c[kc_id]['md_ids'].add(md_id)


    logger.info(f'Number of unique items (C): {len(dict_c.keys())}.')
    logger.debug('Metrics (C):\n\n'+ ''.join([f"'{header}': {dict_headers[header]['cnt']}\n" for header in dict_headers.keys()]))
    
    
    return dict_c



def create_dict_r(logger, outdir):
    
    dict_r = {}         # main output
    dict_headers = {}   # to track the available headers
    
    
    for file in glob.glob(f'{outdir}/kdown/reaction/R*.txt'):
        
        
        # create new item: 
        kr_id = file.rsplit('/', 1)[-1].replace('.txt', '')
        if kr_id not in dict_r.keys():  
            dict_r[kr_id] = {
                'map_ids': set(), 
                'md_ids': set(), 
                'ko_ids': set()
            }  
        else:
            logger.error(f"{kr_id} already included!")
            return 1
        
        
        # read associated text file: 
        with open(file, 'r') as r_handler:
            file_content = r_handler.read().strip()
            
            
            # split rows:
            rows = file_content.split('\n')
            curr_header = None
            for row in rows:
                
                
                # track the headers
                header = row[:12]
                if header not in dict_headers.keys():
                    dict_headers[header] = {}
                    dict_headers[header]['cnt'] = 0
                    dict_headers[header]['kr_ids'] = set()
                dict_headers[header]['cnt'] += 1
                dict_headers[header]['kr_ids'].add(kr_id)
                
                  
                # get the content
                if header == '///':
                    continue    # should be the end of the file
                if header != curr_header and header != '            ':
                    curr_header = header
                content = row[12:]
                
                
                # parse the entry: 
                if curr_header == 'ENTRY       ':
                    kr_id_content = content.strip().split(' ', 1)[0]
                    if kr_id_content != kr_id: 
                        logger.info(f"{kr_id} appears with a different ID in its file ({kr_id_content}).")
                        #return 1
                        
                
                # parse maps (pathways)
                if curr_header == 'PATHWAY     ':
                    map_id = content.strip().split(' ')[0]    # one per row
                    if len(map_id)!=7 or map_id[:2]!='rn':
                        logger.info(f'{kr_id} is linked to a badly formatted pathway ID: {map_id}.')
                    else:
                        map_id = 'map' + map_id[2:]
                        dict_r[kr_id]['map_ids'].add(map_id)
                        
                        
                # parse modules 
                if curr_header == 'MODULE      ':
                    md_id = content.strip().split(' ')[0]    # one per row
                    if len(md_id)!=6 or md_id[0]!='M':
                        logger.info(f'{kr_id} is linked to a badly formatted module ID: {md_id}.')
                    else:
                        dict_r[kr_id]['md_ids'].add(md_id)
                        
                        
                # parse orthologs 
                if curr_header == 'ORTHOLOGY   ':
                    ko_id = content.strip().split(' ')[0]    # one per row
                    if len(ko_id)!=6 or ko_id[0]!='K':
                        logger.info(f'{kr_id} is linked to a badly formatted ortholog ID: {ko_id}.')
                    else:
                        dict_r[kr_id]['ko_ids'].add(ko_id)

    
    logger.info(f'Number of unique items (R): {len(dict_r.keys())}.')
    logger.debug('Metrics (R):\n\n'+ ''.join([f"'{header}': {dict_headers[header]['cnt']}\n" for header in dict_headers.keys()]))
    
    
    return dict_r



def create_dict_map(logger, outdir):
    
    dict_map = {}         # main output
    dict_headers = {}   # to track the available headers
    
    
    for file in glob.glob(f'{outdir}/kdown/pathway/map*.txt'):
        
        
        # create new item: 
        map_id = file.rsplit('/', 1)[-1].replace('.txt', '')
        if map_id not in dict_map.keys():  
            dict_map[map_id] = {
                'md_ids': set(), 
                'name': None,
            }   
        else:
            logger.error(f"{map_id} already included!")
            return 1
        
        
        # read associated text file: 
        with open(file, 'r') as r_handler:
            file_content = r_handler.read().strip()
            
            
            # split rows:
            rows = file_content.split('\n')
            curr_header = None
            for row in rows:
                
                
                # track the headers
                header = row[:12]
                if header not in dict_headers.keys():
                    dict_headers[header] = {}
                    dict_headers[header]['cnt'] = 0
                    dict_headers[header]['map_ids'] = set()
                dict_headers[header]['cnt'] += 1
                dict_headers[header]['map_ids'].add(map_id)
                
                
                # get the content
                if header == '///':
                    continue    # should be the end of the file
                if header != curr_header and header != '            ':
                    curr_header = header
                content = row[12:]
                
                
                # parse the entry: 
                if curr_header == 'ENTRY       ':
                    map_id_content = content.strip().split(' ', 1)[0]
                    if map_id_content != map_id: 
                        logger.info(f"{map_id} appears with a different ID in its file ({map_id_content}).")
                        #return 1
                        
                        
                # parse the name:
                if curr_header == 'NAME        ': 
                    name = content.strip()
                    dict_map[map_id]['name'] = name

                        
                # parse modules 
                if curr_header == 'MODULE      ':
                    md_id = content.strip().split(' ')[0]    # one per row
                    if len(md_id)!=6 or md_id[0]!='M':
                        logger.info(f'{map_id} is linked to a badly formatted module ID: {md_id}.')
                    else:
                        dict_map[map_id]['md_ids'].add(md_id)

    
    logger.info(f'Number of unique items (map): {len(dict_map.keys())}.')
    logger.debug('Metrics (map):\n\n'+ ''.join([f"'{header}': {dict_headers[header]['cnt']}\n" for header in dict_headers.keys()]))
    
    
    return dict_map



def create_dict_md(logger, outdir):
    
    dict_md = {}         # main output
    dict_headers = {}   # to track the available headers
    
    
    for file in glob.glob(f'{outdir}/kdown/module/M*.txt'):
        
        
        # create new item: 
        md_id = file.rsplit('/', 1)[-1].replace('.txt', '')
        if md_id not in dict_md.keys():  
            dict_md[md_id] = {
                'name': None,
            }   
        else:
            logger.error(f"{md_id} already included!")
            return 1
        
        
        # read associated text file: 
        with open(file, 'r') as r_handler:
            file_content = r_handler.read().strip()
            
            
            # split rows:
            rows = file_content.split('\n')
            curr_header = None
            for row in rows:
                
                
                # track the headers
                header = row[:12]
                if header not in dict_headers.keys():
                    dict_headers[header] = {}
                    dict_headers[header]['cnt'] = 0
                    dict_headers[header]['md_ids'] = set()
                dict_headers[header]['cnt'] += 1
                dict_headers[header]['md_ids'].add(md_id)
                
                
                # get the content
                if header == '///':
                    continue    # should be the end of the file
                if header != curr_header and header != '            ':
                    curr_header = header
                content = row[12:]
                
                
                # parse the entry: 
                if curr_header == 'ENTRY       ':
                    md_id_content = content.strip().split(' ', 1)[0]
                    if md_id_content != md_id: 
                        logger.info(f"{md_id} appears with a different ID in its file ({md_id_content}).")
                        #return 1
                        
                        
                # parse the name:
                if curr_header == 'NAME        ': 
                    name = content.strip()
                    dict_md[md_id]['name'] = name

    
    logger.info(f'Number of unique items (M): {len(dict_md.keys())}.')
    logger.debug('Metrics (M):\n\n'+ ''.join([f"'{header}': {dict_headers[header]['cnt']}\n" for header in dict_headers.keys()]))
    
    
    return dict_md



def create_idcollection_dict(dict_ko, dict_c, dict_r, dict_map, dict_md):

    idcollection_dict = {}
    
    
    idcollection_dict['kc'] = set()
    for kc_id in dict_c.keys():
        idcollection_dict['kc'].add(kc_id)
        
        
    idcollection_dict['kr'] = set()
    for kr_id in dict_r.keys():
        idcollection_dict['kr'].add(kr_id)
        
        
    idcollection_dict['ko'] = set()
    for ko_id in dict_ko.keys():
        idcollection_dict['ko'].add(ko_id)
        
        
    idcollection_dict['kr_to_kos'] = {}
    for kr_id in dict_r.keys():
        idcollection_dict['kr_to_kos'][kr_id] = set()
        for ko_id in dict_r[kr_id]['ko_ids']:
            idcollection_dict['kr_to_kos'][kr_id].add(ko_id)
            
            
    idcollection_dict['kr_to_maps'] = {}
    for kr_id in dict_r.keys():
        idcollection_dict['kr_to_maps'][kr_id] = set()
        for map_id in dict_r[kr_id]['map_ids']:
            idcollection_dict['kr_to_maps'][kr_id].add(map_id)
            
            
    idcollection_dict['kr_to_mds'] = {}
    for kr_id in dict_r.keys():
        idcollection_dict['kr_to_mds'][kr_id] = set()
        for md_id in dict_r[kr_id]['md_ids']:
            idcollection_dict['kr_to_mds'][kr_id].add(md_id)
            
    
    idcollection_dict['ko_to_name'] = {}
    for ko_id in dict_ko.keys():
        idcollection_dict['ko_to_name'][ko_id] = dict_ko[ko_id]['name']
    
    
    idcollection_dict['ko_to_symbols'] = {}
    for ko_id in dict_ko.keys():
        idcollection_dict['ko_to_symbols'][ko_id] = set()
        for symbol in dict_ko[ko_id]['symbols']:
            idcollection_dict['ko_to_symbols'][ko_id].add(symbol)
            
            
    idcollection_dict['ko_to_ecs'] = {}
    for ko_id in dict_ko.keys():
        idcollection_dict['ko_to_ecs'][ko_id] = set()
        for ec in dict_ko[ko_id]['ecs']:
            idcollection_dict['ko_to_ecs'][ko_id].add(ec)
            
            
    idcollection_dict['ko_to_cogs'] = {}
    for ko_id in dict_ko.keys():
        idcollection_dict['ko_to_cogs'][ko_id] = set()
        for cog in dict_ko[ko_id]['cogs']:
            idcollection_dict['ko_to_cogs'][ko_id].add(cog)
            
            
    idcollection_dict['ko_to_gos'] = {}
    for ko_id in dict_ko.keys():
        idcollection_dict['ko_to_gos'][ko_id] = set()
        for go in dict_ko[ko_id]['gos']:
            idcollection_dict['ko_to_gos'][ko_id].add(go)
            
            
    idcollection_dict['map_to_name'] = {}
    for map_id in dict_map.keys():
        idcollection_dict['map_to_name'][map_id] = dict_map[map_id]['name']
        
        
    idcollection_dict['md_to_name'] = {}
    for md_id in dict_md.keys():
        idcollection_dict['md_to_name'][md_id] = dict_md[md_id]['name']
        
    
    return idcollection_dict



def create_summary_dict(dict_c, dict_r, dict_map, dict_md):

    summary_dict = []   # list fo dicts

    for i, map_id in enumerate(list(dict_map.keys())):
        
        
        # get total number of reactions in this map.
        # iterate dict_r looking at the linked maps for each reaction 
        kr_ids = set()
        for r_id in dict_r.keys():
            if map_id in dict_r[r_id]['map_ids']:
                kr_ids.add(r_id)
        
        
        # append the new elemnt (dict) to the list
        summary_dict.append({})
        summary_dict[i]['map_id'] = map_id
        summary_dict[i]['map_name'] = dict_map[map_id]['name']
        summary_dict[i]['kr_ids'] = kr_ids
        summary_dict[i]['cnt_r'] = len(kr_ids)
        summary_dict[i]['mds'] = []
        
        
        # get number of reactions per module involved.
        # iterate dict_r looking at the linked modules for each reaction 
        for k, md_id in enumerate(list(dict_map[map_id]['md_ids'])):
            kr_ids_md = set()
            for r_id in dict_r.keys():
                if md_id in dict_r[r_id]['md_ids']:
                    kr_ids_md.add(r_id)
            
            summary_dict[i]['mds'].append({})
            summary_dict[i]['mds'][k]['md_id'] = md_id
            summary_dict[i]['mds'][k]['md_name'] = dict_md[md_id]['name']
            summary_dict[i]['mds'][k]['kr_ids_md'] = kr_ids_md
            summary_dict[i]['mds'][k]['cnt_r_md'] = len(kr_ids_md)
        summary_dict[i]['mds'] = sorted(summary_dict[i]['mds'], key=lambda x: x['cnt_r_md'], reverse=True)
                    
          
    summary_dict = sorted(summary_dict, key=lambda x: x['cnt_r'], reverse=True)
    
    
    return summary_dict