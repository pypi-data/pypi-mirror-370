import warnings

import pandas as pnd
import gempipe


from ..commons import get_biomass_dict
from ..commons import apply_medium_given_column
from ..commons import verify_growth
from ..commons import get_biomass_df_structure
from ..commons import fba_no_warnings

from .gapfillutils import get_repository_nogenes
from .gapfillutils import import_from_universe



def gapfill_on_media(logger, model, universe, dbexp, media, cond_col_dict, exclude_orphans):
    
    
    # check if requested (always)
    df_B = pnd.DataFrame()
    df_B = get_biomass_df_structure(logger, df_B, model, universe, dbexp, cond_col_dict)
         
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: gap-filling will be skipped.")
        return df_B
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in dbexp['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(dbexp['media'].columns)}.")
        return 1
        
        
    # get the repository of reactions:
    repository_nogenes = get_repository_nogenes(logger, universe, exclude_orphans)
    
    
    logger.info(f"Gap-filling for biomass on {len(media)} media...")
    for medium in media: 
        if medium not in dbexp['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_B[f'{medium}'] = None
        logger.debug(f"Gap-filling on medium '{medium}'...")
                    
            
        # apply medium both on universe and model:
        response = apply_medium_given_column(logger, repository_nogenes, medium, dbexp['media'][medium])
        if response == 1: return 1
        if not verify_growth(repository_nogenes):
            
            logger.error(f"Medium '{medium}' does not support growth of universe.")
            return 1
        
        response = apply_medium_given_column(logger, model, medium, dbexp['media'][medium])
        if response == 1: return 1
        if verify_growth(model):
            
            logger.debug(f"No need to gapfill model on medium '{medium}'.")
            # show result of vanilla FBA if --verbose:
            _, plain_objval, plain_status = fba_no_warnings(model)
            logger.debug(f"Plain FBA on medium '{medium}': {plain_objval} ({plain_status}).")
            continue


        # launch gap-filling separately for each biomass precursor:
        # force 'atp_c' as first:
        universal_precs = ['atp_c'] + [m.id for m in universe.reactions.Biomass.reactants if m.id not in ['atp_c', 'h2o_c']]
        for mid in universal_precs:
            # skip conditional precursors: 
            if mid in [m.id for m in model.reactions.Biomass.reactants]:
            
                # save time if it can already be synthesized
                if gempipe.can_synth(model, mid)[0]:
                    df_B.loc[mid, f'{medium}'] = '/'
                    logger.debug(f"Gap-filled 0 reactions on medium '{medium}' for '{mid}': [].")
                    continue   # save time!
                    
                    
                # remove 'meanfa_c' sink (needed to model fatty acids / phospholips):
                with repository_nogenes, model:
                    
                    # needed to avoid some infeasible solutions (its' temporary thanks to the 'with' statement)
                    repository_nogenes.reactions.Biomass.bounds = (0,0)
                    model.reactions.Biomass.bounds = (0,0)
                    
                    with warnings.catch_warnings():
                        # avoid warnings like "python3.9/site-packages/cobra/core/group.py:147: UserWarning: need to pass in a list"
                        warnings.simplefilter("ignore")
                        repository_nogenes.remove_reactions(["sn_meanfa_c"]) # this works also with rids instaead of Rs

                    #minflux = get_optthr()
                    minflux = 0.1
                    suggested_rids = gempipe.perform_gapfilling(model, repository_nogenes, mid, nsol=1, minflux=minflux, boost=True, verbose=False)
                    if suggested_rids == None:
                        logger.error(f"The gap-filling problem seems too hard for '{mid}' on medium '{medium}': should '{mid}' be included in '{medium}'?")
                        return 1
                
                
                df_B.loc[mid, f'{medium}'] = '; '.join([f'+{i}' for i in suggested_rids]) 
                logger.debug(f"Gap-filled {len(suggested_rids)} reactions on medium '{medium}' for '{mid}': {suggested_rids}.")
                for rid in suggested_rids:
                    import_from_universe(model, repository_nogenes, rid, gpr='')
                    
                    
        # if reached this point , the model should be ble to grow on this medium
        _, plain_objval, plain_status = fba_no_warnings(model)
        logger.debug(f"Plain FBA on medium '{medium}': {plain_objval} ({plain_status}).")
                
                
    return df_B

