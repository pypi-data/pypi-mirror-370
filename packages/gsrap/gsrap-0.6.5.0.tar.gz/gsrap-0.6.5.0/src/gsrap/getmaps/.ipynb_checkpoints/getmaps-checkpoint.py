import shutil
import os
import pickle


from .kdown import download_raw_txtfiles
from .kdown import create_dict_ko
from .kdown import create_dict_c
from .kdown import create_dict_r
from .kdown import create_dict_map
from .kdown import create_dict_md
from .kdown import create_idcollection_dict
from .kdown import create_summary_dict

from .mnxdown import pull_mnx_ftp
from .mnxdown import create_mnxm_to_others
from .mnxdown import create_mnxr_to_others
from .mnxdown import create_others_to_mnx
from .mnxdown import compdict_from_to



def do_kdown(logger, outdir, usecache, keeptmp): 
    
    
    logger.info(f"Respectfully retrieving metabolic information from KEGG. Raw data are being saved into '{outdir}/kdown/'. Be patient, could take a couple of days...")
    os.makedirs(f'{outdir}/kdown/', exist_ok=True)
    
    response = download_raw_txtfiles(logger, outdir, usecache)
    if type(response) == int: return 1
    else: RELEASE_kegg = response
    
    
    logger.info("Parsing downloaded KEGG information...")

    response = create_dict_ko(logger, outdir)
    if type(response) == int: return 1
    else: dict_ko = response
    
    response = create_dict_c(logger, outdir)
    if type(response) == int: return 1
    else: dict_c = response
    
    response = create_dict_r(logger, outdir)
    if type(response) == int: return 1
    else: dict_r = response
    
    response = create_dict_map(logger, outdir)
    if type(response) == int: return 1
    else: dict_map = response
    
    response = create_dict_md(logger, outdir)
    if type(response) == int: return 1
    else: dict_md = response
    
    
    # create 'idcollection_dict' and 'summary_dict' dictionaries
    idcollection_dict = create_idcollection_dict(dict_ko, dict_c, dict_r, dict_map, dict_md)
    summary_dict = create_summary_dict(dict_c, dict_r, dict_map, dict_md)
    
        
    return (RELEASE_kegg, idcollection_dict, summary_dict)



def do_mnxdown(logger, outdir, usecache, keeptmp): 
    
    
    logger.info(f"Retrieving metabolic information from MetaNetX. Raw data are being saved into '{outdir}/mnxdown/'. This should take minutes...")
    os.makedirs(f'{outdir}/mnxdown/', exist_ok=True)
    
    response = pull_mnx_ftp(logger, outdir, usecache)
    if type(response) == int: return 1
    else: RELEASE_nmx = response
    
    
    logger.info("Parsing downloaded MetaNetX information (metabolites)...")
    
    # create the 'mnx_to_others' and 'others_to_mnx' dictionaries
    mnxm_to_others = create_mnxm_to_others(logger, outdir)
    others_to_mnxm = create_others_to_mnx(logger, mnxm_to_others)
    
    logger.info("Parsing downloaded MetaNetX information (reactions)...")
    
    # create the 'mnx_to_others' and 'others_to_mnx' dictionaries
    mnxr_to_others = create_mnxr_to_others(logger, outdir)
    others_to_mnxr = create_others_to_mnx(logger, mnxr_to_others)
    
    
    mnx_assets = (mnxm_to_others, others_to_mnxm, mnxr_to_others, others_to_mnxr)
    return (RELEASE_nmx, mnx_assets)



def main(args, logger):
    
    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # KEGG
    response = do_kdown(logger, args.outdir, args.usecache, args.keeptmp)
    if type(response) == int: return 1
    else: RELEASE_kegg, idcollection_dict, summary_dict = response[0], response[1], response[2]

    
    # MetaNetX
    response = do_mnxdown(logger, args.outdir, args.usecache, args.keeptmp)
    if type(response) == int: return 1
    else: RELEASE_nmx, mnx_assets = response[0], response[1]    
    # create compact dictionaries, with just the needed information, to save space:
    keggc_to_bigg = compdict_from_to(mnx_assets, 'm', 'kegg.compound', 'bigg.metabolite')
    keggr_to_bigg = compdict_from_to(mnx_assets, 'r', 'kegg.reaction', 'bigg.reaction')


    # create 'gsrap.maps':
    with open(f'{args.outdir}/gsrap.maps', 'wb') as wb_handler:
        pickle.dump({
            'RELEASE_kegg': RELEASE_kegg, 'idcollection_dict': idcollection_dict, 'summary_dict': summary_dict,
            'RELEASE_nmx': RELEASE_nmx, 'keggc_to_bigg': keggc_to_bigg, 'keggr_to_bigg': keggr_to_bigg,
        }, wb_handler)
    logger.info(f"'{args.outdir}/gsrap.maps' created!")
    
        
    # clean temporary files:
    if not args.keeptmp:
        shutil.rmtree(f'{args.outdir}/kdown', ignore_errors=True)
        shutil.rmtree(f'{args.outdir}/mnxdown', ignore_errors=True)
        logger.info(f"Temporary raw files deleted!")
    
    
    return 0