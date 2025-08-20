from importlib import resources


import pandas as pnd
import gempipe


from ..commons import apply_medium_given_column
from ..commons import verify_growth

from .gapfillutils import get_repository_nogenes
from .gapfillutils import import_from_universe



def edit_trans_reacs(model, exr):
    
    pass
    


def biolog_on_media(logger, model, universe, expcon, media, biolog, exclude_orphans, cnps):
    
    
    # load assets:
    official_pm_tables = {}
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        with resources.path("gsrap.assets", f"{pm}.csv") as asset_path: 
            official_pm_tables[pm] = pnd.read_csv(asset_path, index_col=1, names=['plate','substrate','source','u1','u2','u3','u4','kc','cas'])
    
    
    # check if requested
    df_P = pnd.DataFrame()
    if biolog == '-':  # 'cnps' is != '-' as checked during main()
        return df_P
    
    
    # format starting C/N/P/S sources as EXR:
    if len(cnps.split(',')) != 4:
        logger.error("Parameter --cnps must be formatted as 4 comma-sperated metabolite IDs (order: C, N, P and S).")
        return 1
    cnps = cnps.split(',')
    # add '_e and 'EX_' where needed.
    cnps = [i + '_e' for i in cnps if i.endswith('_e')==False]
    cnps = ["EX_" + i for i in cnps if i.startswith('EX_')==False]
    cnps = {source: exr for source, exr in zip(['carbon', 'nitrogen','sulfur','phosphorus'], cnps)}
    
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: Biolog(R)-based model curation will be skipped.")
        return df_P
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # get plates for this strain
    avail_plates = []
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        if biolog in expcon[pm].columns: 
            avail_plates.append(pm)
    if avail_plates == []:
        logger.info(f"No Biolog(R) plates found for strain '{biolog}': Biolog(R)-based model curation will be skipped.")
        return df_P
    else:
        logger.debug(f"Found {len(avail_plates)} Biolog(R) plates for '{biolog}': {sorted(avail_plates)}.")
        
        
    # get kc-to-exr dict using built-in annotations:
    kc_to_exr = {}
    for m in model.metabolites: 
        if m.id.endswith('_e') == False:
            continue
        if 'kegg.compound' not in m.annotation.keys():
            continue
        kc_ids = m.annotation['kegg.compound']
        if type(kc_ids) == str: kc_ids = [kc_ids]
        kc_ids = [i for i in kc_ids if i != 'CXXXXX']  
        for kc_id in kc_ids:
            kc_to_exr[kc_id] = f'EX_{m.id}'
        
        
    # prepare sheet for excel output
    for pm in avail_plates:
        for well, row in official_pm_tables[pm].iterrows():
            # write substrate name:
            df_P.loc[f"{pm}:{well}", 'substrate'] = row['substrate']
            
            
            # write source type:
            if pm in ['PM1', 'PM2A']: 
                df_P.loc[f"{pm}:{well}", 'source'] = 'carbon'
            elif pm == 'PM3B': 
                df_P.loc[f"{pm}:{well}", 'source'] = 'nitrogen'
            else:
                if well[0] in ['F','G','H']: df_P.loc[f"{pm}:{well}", 'source'] = 'sulfur'
                else: df_P.loc[f"{pm}:{well}", 'source'] = 'phosphorus'
            
            
            # get kc and write the correspondent exchange
            kc = row['kc']
            if type(kc)==float: 
                if row['substrate'] == 'Negative Control': 
                    df_P.loc[f"{pm}:{well}", 'exchange'] = ''   # nagative control well
                else:
                    df_P.loc[f"{pm}:{well}", 'exchange'] = 'missing KEGG codes'  # No C/D/G codes at all
            elif kc.startswith('C'):
                if kc not in kc_to_exr.keys():
                    df_P.loc[f"{pm}:{well}", 'exchange'] = f'NA ({kc})'   # kc available, but still no transporters in db.
                else:
                    df_P.loc[f"{pm}:{well}", 'exchange'] = kc_to_exr[kc]
            elif kc.startswith('D'):
                df_P.loc[f"{pm}:{well}", 'exchange'] = 'unhandled KEGG DRUG code'  # TODO manage exchanges in this case
            elif kc.startswith('G'):
                df_P.loc[f"{pm}:{well}", 'exchange'] = 'unhandled KEGG GLYCAN code'  # TODO manage exchanges in this case
            else:
                df_P.loc[f"{pm}:{well}", 'exchange'] = '???'  # there should be no other cases
    

                
    # get the repository of reactions:
    repository_nogenes = get_repository_nogenes(logger, universe, exclude_orphans)
    
    
    logger.info(f"Curating with {sorted(avail_plates)} Biolog(R) plates on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_P[f'{medium}'] = None
        logger.debug(f"Performing Biolog(R)-based curation on medium '{medium}'...")
        
        
        # apply medium both on universe and model:
        # (growth was already verified in 'gapfill_on_media')
        response = apply_medium_given_column(logger, repository_nogenes, medium, expcon['media'][medium])
        if response == 1: return 1
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # apply minimal medium to the universe: 
        if 'EX_photon870_e' in model.medium.keys():
            logger.debug("Setting universe on minimal medium 'M9photo'...")
            response = apply_medium_given_column(logger, universe, 'M9photo', expcon['media']['M9photo'])
            if response == 1: return 1
        elif 'EX_o2_e' not in model.medium.keys():
            logger.debug("Setting universe on minimal medium 'M9an'...")
            response = apply_medium_given_column(logger, universe, 'M9an', expcon['media']['M9an'])
            if response == 1: return 1
        elif 'EX_o2_e' in model.medium.keys():
            logger.debug("Setting universe on minimal medium 'M9'...")
            response = apply_medium_given_column(logger, universe, 'M9', expcon['media']['M9'])
            if response == 1: return 1
        else:
            logger.debug("No adequate minimal medium found for universe.")
            return 1
        
    
    
        # iterate pm:wells
        for index, row in df_P.iterrows():
            
            
            # get needed infos
            pm, well = index.split(':')
            source = row['source']
            exr = df_P.loc[f"{pm}:{well}", 'exchange']
            if exr.startswith('EX_') == False:
                exr = None
            start_exr = cnps[source]
            experimental = expcon[pm].loc[well, biolog]
            
            
            # check if 'start_exr' is in the medium (model or universe is the same here)
            if start_exr not in model.medium.keys():
                logger.error(f"Provided starting {source} source ('{start_exr}') is not used in '{medium}' medium. Please correct the --cnps parameter.")
                return 1
            
            
            # skip if transporters for this well are not yet implemented:
            if exr == None:
                continue
        
        
            # Ok the exr is contained in this medium. Proceed with the 2 FBAs:
            performed_gapfilling = False
            suggested_rids = None
            performed_transedit = False
            removing_rids = None
            
            with universe, repository_nogenes, model:
                
                
                # adabpt the atmsphere of the minimal medium:
                if 'EX_o2_e' not in model.medium.keys(): universe.reactions.get_by_id('EX_o2_e').lower_bound = 0 
                if 'EX_co2_e' not in model.medium.keys(): universe.reactions.get_by_id('EX_co2_e').lower_bound = 0 
                
                
                # save the lower bound for the new exr
                lb = repository_nogenes.reactions.get_by_id(start_exr).lower_bound
                
                
                # 1st FBA
                # universe
                if   source=='carbon':     universe.reactions.get_by_id('EX_glc__D_e').lower_bound = 0
                elif source=='nitrogen':   universe.reactions.get_by_id('EX_nh4_e').lower_bound = 0
                elif source=='phosphorus': universe.reactions.get_by_id('EX_pi_e').lower_bound = 0
                elif source=='sulfur':     universe.reactions.get_by_id('EX_so4_e').lower_bound = 0
                fba0_unive = verify_growth(universe, boolean=False)
                # repository
                repository_nogenes.reactions.get_by_id(start_exr).lower_bound = 0
                fba0_repos = verify_growth(repository_nogenes, boolean=False)
                # model
                model.reactions.get_by_id(start_exr).lower_bound = 0
                fba0_model = verify_growth(model, boolean=False)         
                
                
                # 2nd FBA
                # universe
                universe.reactions.get_by_id(exr).lower_bound = -1000
                fba1_unive = verify_growth(universe, boolean=False)
                # repository
                repository_nogenes.reactions.get_by_id(exr).lower_bound = lb
                fba1_repos = verify_growth(repository_nogenes, boolean=False)
                # model
                model.reactions.get_by_id(exr).lower_bound = lb
                fba1_model = verify_growth(model, boolean=False)
                   
                 
                
                # universe cannot utilize this substrate: 
                if (fba1_unive == 'infeasible') \
                or (fba0_unive == 'infeasible' and fba1_unive != 'infeasible' and fba1_unive < get_optthr()) \
                or (fba0_unive != 'infeasible' and fba1_unive != 'infeasible' and fba1_unive <= fba0_unive):

                    logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): universe is unable. Please expand and/or correct the universe.")
                    df_P.loc[index, f'{medium}'] = f"universe unable"
                    #return 1

                # model cannot utilize this substrate on medium:
                elif (fba1_model == 'infeasible') \
                  or (fba0_model == 'infeasible' and fba1_model != 'infeasible' and fba1_model < get_optthr()) \
                  or (fba0_model != 'infeasible' and fba1_model != 'infeasible' and fba1_model <= fba0_model):

                    # mismatch FN:
                    if experimental == 1:

                        # universe cannot reproduce experimental in the medium:
                        if (fba1_repos == 'infeasible') \
                        or (fba0_repos == 'infeasible' and fba1_repos != 'infeasible' and fba1_repos < get_optthr()) \
                        or (fba0_repos != 'infeasible' and fba1_repos != 'infeasible' and fba1_repos <= fba0_repos):

                            logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): universe is unable in this medium. Please expand and/or correct the universe.")
                            df_P.loc[index, f'{medium}'] = f"universe unable in medium"
                            #return 1 

                        # universe can be used for gapfilling:
                        else:
                            logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): gap-filling for this substrate...")
                            performed_gapfilling = True
                            
                            
                            # remove 'meanfa_c' sink (needed to model fatty acids / phospholips):
                            with repository_nogenes:
                                
                                with warnings.catch_warnings():
                                    # avoid warnings like "python3.9/site-packages/cobra/core/group.py:147: UserWarning: need to pass in a list"
                                    warnings.simplefilter("ignore")
                                    repository_nogenes.remove_reactions(["sn_meanfa_c"]) # this works also with rids instaead of Rs
                                    
                                #minflux = get_optthr() if fba1_model == 'infeasible' else fba1_model + get_optthr()
                                minflux = 0.1 if fba1_model == 'infeasible' else fba1_model + 0.1
                                suggested_rids = gempipe.perform_gapfilling(model, repository_nogenes, nsol=1, minflux=minflux, boost=False, verbose=False)
                                if suggested_rids == None:
                                    logger.error(f"The gap-filling problem seems too hard for substrate {pm}':'{well}':'{exr} in medium '{medium}'.")
                                    return 1

                                
                            df_P.loc[index, f'{medium}'] = '; '.join([f'+{i}' for i in suggested_rids]) 
                            logger.debug(f"Gap-filled {len(suggested_rids)} reactions on medium '{medium}' for substrate {pm}':'{well}':'{exr}: {suggested_rids}.")

                            
                    # it's a match! TN
                    else:
                        logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): TN match.")
                        df_P.loc[index, f'{medium}'] = f"/"

                # model can utilize this substrate on medium:
                else:

                    # mismatch FP
                    if experimental == 0:

                        logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): trying to improve accuracy of tranport reactions...")
                        df_P.loc[index, f'{medium}'] = f"TRANSPORT"
                        
                        edit_trans_reacs(model, exr)

                    # it's a match! TP
                    else:
                        logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): TP match.")
                        df_P.loc[index, f'{medium}'] = f"/"
            
            
            
            # apply modifications:
            if performed_gapfilling == True:
                for rid in suggested_rids:
                    import_from_universe(model, repository_nogenes, rid, gpr='')
            if performed_transedit == True:
                pass   # TODO
            

    return df_P

