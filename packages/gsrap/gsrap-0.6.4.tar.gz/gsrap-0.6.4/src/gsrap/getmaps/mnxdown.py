import urllib
import os


import pandas as pnd



def pull_mnx_ftp(logger, outdir, usecache):
    
    
    def single_pull(logger, outdir, url, filename, usecache):
        if (os.path.exists(f"{outdir}/mnxdown/{filename}") and usecache) == False:
            with urllib.request.urlopen(url) as response:
                with open(f"{outdir}/mnxdown/{filename}", 'wb') as out_file:
                    out_file.write(response.read())
                    logger.debug(f"Downloaded '{outdir}/mnxdown/{filename}'!")

                    
    RELEASE_mnx = None
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/CHANGELOG', 'CHANGELOG.txt', usecache) 
    with open(f"{outdir}/mnxdown/CHANGELOG.txt", "r") as f:
        RELEASE_mnx = f.read()
        
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/chem_depr.tsv', 'chem_depr.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/chem_isom.tsv', 'chem_isom.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/chem_prop.tsv', 'chem_prop.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/chem_xref.tsv', 'chem_xref.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/comp_depr.tsv', 'comp_depr.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/comp_prop.tsv', 'comp_prop.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/comp_xref.tsv', 'comp_xref.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/reac_depr.tsv', 'reac_depr.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/reac_prop.tsv', 'reac_prop.tsv', usecache) 
    single_pull(logger, outdir, 'https://www.metanetx.org/ftp/latest/reac_xref.tsv', 'reac_xref.tsv', usecache) 
            
               
    return RELEASE_mnx



def remove_comment_lines(filepath):
    filtered_lines = None
    with open(filepath, 'r') as infile:
        lines = infile.readlines()
        filtered_lines = [line for line in lines if not line.lstrip().startswith('#')]
    with open(filepath, 'w') as outfile:
        outfile.writelines(filtered_lines)


        
def create_mnxr_to_others(logger, outdir):
    
    
    # Remove lines beginning with "#". Better than using "comment='#'" inside pnd.read_csv(), 
    # as some IDs in 'reac_xref.tsv' are like "kegg.reaction:R04422#1" and "kegg.reaction:R04422#2"
    remove_comment_lines(f"{outdir}/mnxdown/reac_prop.tsv")
    remove_comment_lines(f"{outdir}/mnxdown/reac_xref.tsv")

    
    # load main tables:
    header_reac_prop = ['ID', 'mnx_equation', 'reference', 'ECs', 'is_balanced', 'is_transport',]
    reac_prop = pnd.read_csv(f"{outdir}/mnxdown/reac_prop.tsv", sep='\t', header=None, names=header_reac_prop)
    reac_prop = reac_prop.set_index('ID', drop=True, verify_integrity=True)

    header_reac_xref = ['source', 'ID', 'description']
    reac_xref = pnd.read_csv(f"{outdir}/mnxdown/reac_xref.tsv", sep='\t', header=None, names=header_reac_xref)
    reac_xref = reac_xref.set_index('source', drop=True, verify_integrity=True)
    
    
    # create 'mnx_to_others':
    # 'ec' info is exclusively in 'reac_prop'
    mnx_to_others = {}
    for index, row in reac_prop.iterrows(): 
        if index.startswith('MNXR'):   
            if index not in mnx_to_others.keys(): 
                mnx_to_others[index] = {
                    'ec': set(), 
                    'kegg.reaction': set(),
                    'metacyc.reaction': set(),
                    'bigg.reaction': set(),
                    'seed.reaction': set(),
                }
                
            if pnd.isna(row['ECs']) == False:
                for ec in row['ECs'].split(';'): 
                    mnx_to_others[index]['ec'].add(ec)
                    
    
    # fill 'mnx_to_others':
    for index, row in reac_xref.iterrows():

        # get 'dbid' and 'eqid'
        dbid = index.split(':')[0]
        if dbid == 'mnx': continue
        try: eqid = index.split(':')[1].split('#')[0]  # handle cases like like "kegg.reaction:R04422#1" and "kegg.reaction:R04422#2"
        except: continue   # eg this row "MNXR02	MNXR02	PROTON import/export at model boundary"
        if eqid.startswith('R_'):
            eqid = eqid[2:]
        if row['ID'].startswith('MNXR'):

            if   dbid in ['kegg.reaction', 'keggR']:
                mnx_to_others[row['ID']]['kegg.reaction'].add(eqid)
            elif dbid in ['metacyc.reaction', 'metacycR']:
                mnx_to_others[row['ID']]['metacyc.reaction'].add(eqid)
            elif dbid in ['bigg.reaction', 'biggR']:
                mnx_to_others[row['ID']]['bigg.reaction'].add(eqid)
            elif dbid in ['seed.reaction', 'seedR']:
                mnx_to_others[row['ID']]['seed.reaction'].add(eqid)
            
            
    logger.info(f"Collected information for {len(mnx_to_others.keys())} MNX reactions.")
    return mnx_to_others



def create_mnxm_to_others(logger, outdir):
    
    
    # Remove lines beginning with "#". Better than using "comment='#'" inside pnd.read_csv(), 
    # as some IDs in 'reac_xref.tsv' are like "kegg.reaction:R04422#1" and "kegg.reaction:R04422#2"
    remove_comment_lines(f"{outdir}/mnxdown/chem_prop.tsv")
    remove_comment_lines(f"{outdir}/mnxdown/chem_xref.tsv")


    # load main tables:
    header_chem_prop = ['ID', 'name', 'reference', 'formula', 'charge', 'mass', 'InChI', 'InChIKey', 'SMILES']
    chem_prop = pnd.read_csv(f"{outdir}/mnxdown/chem_prop.tsv", sep='\t', header=None, names=header_chem_prop)
    chem_prop = chem_prop.set_index('ID', drop=True, verify_integrity=True)

    header_chem_xref = ['source', 'ID', 'description']
    chem_xref = pnd.read_csv(f"{outdir}/mnxdown/chem_xref.tsv", sep='\t', header=None, names=header_chem_xref)
    chem_xref = chem_xref.set_index('source', drop=True, verify_integrity=True)
    
    
    # create 'mnx_to_others':
    # 'formula','charge','inchikey' info is exclusively in 'chem_prop'
    mnx_to_others = {}
    for index, row in chem_prop.iterrows(): 
        if index.startswith('MNXM'):   
            if index not in mnx_to_others.keys(): 
                mnx_to_others[index] = {
                    'formula': None, 
                    'charge': None, 
                    'inchikey': None,
                    'kegg.compound': set(),
                    'kegg.drug': set(),
                    'kegg.glycan': set(),
                    'metacyc.compound': set(),
                    'bigg.metabolite': set(),
                    'seed.compound': set(), 
                }

            if pnd.isna(row['formula']) == False:
                mnx_to_others[index]['formula'] = row['formula']
            if pnd.isna(row['charge']) == False:
                mnx_to_others[index]['charge'] = float(row['charge'])
            if pnd.isna(row['InChIKey']) == False:
                inchikey = row['InChIKey']
                inchikey = inchikey.replace('InChIKey=', '')
                mnx_to_others[index]['inchikey'] = inchikey
                
                
    # fill 'mnx_to_others':
    for index, row in chem_xref.iterrows():

        # get 'dbid' and 'eqid'
        dbid = index.split(':')[0]
        if dbid == 'mnx': continue
        try: eqid = index.split(':')[1].split('#')[0]  # handle cases like like "kegg.reaction:R04422#1" and "kegg.reaction:R04422#2"
        except: continue   # eg this row "MNXM02  MNXM02  OH(-)||hydroxyde"
        if eqid.startswith('M_'):
            eqid = eqid[2:]
        if row['ID'].startswith('MNXM'):  

            if   dbid in ['kegg.compound', 'keggC']:
                mnx_to_others[row['ID']]['kegg.compound'].add(eqid)
            elif dbid in ['metacyc.drug', 'keggD']:
                mnx_to_others[row['ID']]['kegg.drug'].add(eqid)
            elif dbid in ['metacyc.glycan', 'keggG']:
                mnx_to_others[row['ID']]['kegg.glycan'].add(eqid)
            elif dbid in ['metacyc.compound', 'metacycM']:
                mnx_to_others[row['ID']]['metacyc.compound'].add(eqid)
            elif dbid in ['bigg.metabolite', 'biggM']:
                mnx_to_others[row['ID']]['bigg.metabolite'].add(eqid)
            elif dbid in ['seed.compound', 'seedM']:
                mnx_to_others[row['ID']]['seed.compound'].add(eqid)


    logger.info(f"Collected information for {len(mnx_to_others.keys())} MNX metabolites.")
    return mnx_to_others



def compdict_from_to(mnx_assets, mr='m', dbfrom=None, dbto=None ):
    
    mnxm_to_others, others_to_mnxm, mnxr_to_others, others_to_mnxr = \
        mnx_assets[0], mnx_assets[1], mnx_assets[2], mnx_assets[3]
    
    if mr == 'm':
        return {key: mnxm_to_others[value][dbto] for key, value in others_to_mnxm[dbfrom].items()}
    if mr == 'r':
        return {key: mnxr_to_others[value][dbto] for key, value in others_to_mnxr[dbfrom].items()}
    
    keggc_to_bigg = compdict_from_to(mnx_assets, 'm', 'kegg.compound', 'bigg.metabolite')
    keggr_to_bigg = compdict_from_to(mnx_assets, 'r', 'kegg.reaction', 'bigg.reaction')



def create_others_to_mnx(logger, mnx_to_others):
    # convert 'mnx_to_others' into 'mnx_to_others':

    others_to_mnx = {}
    for mnxid, others in mnx_to_others.items():
        for db in others.keys():
            if db in ['formula', 'charge', 'inchikey']:
                continue   # for the metabolite dicts
            if db not in others_to_mnx.keys():
                others_to_mnx[db] = {}
            for otherid in others[db]:
                if otherid not in others_to_mnx[db].keys():
                    others_to_mnx[db][otherid] = mnxid
                
               
    for db in others_to_mnx.keys():
        logger.info(f"Collected crossrefs for {len(others_to_mnx[db].keys())} '{db}' items.")
    return others_to_mnx