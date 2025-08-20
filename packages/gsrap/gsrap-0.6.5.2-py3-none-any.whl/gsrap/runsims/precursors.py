import pandas as pnd
import gempipe



from ..commons import get_biomass_dict
from ..commons import apply_medium_given_column
from ..commons import get_biomass_df_structure



def precursors_on_media(logger, model, universe, dbexp, media, cond_col_dict, precursors):
    
                
    # check if requested
    df_E = pnd.DataFrame()
    if not precursors:
        return df_E
    df_E = get_biomass_df_structure(logger, df_E, model, universe, dbexp, cond_col_dict)

        
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: blocked biomass precursors check will be skipped.")
        return df_E
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in dbexp['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(dbexp['media'].columns)}.")
        return 1
            
    
    logger.info(f"Checking blocked biomass precursors on {len(media)} media...")
    for medium in media:
        if medium not in dbexp['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_E[f'{medium}'] = None
        logger.debug(f"Checking blocked biomass precursors on medium '{medium}'...")
            
            
        # apply medium :
        response = apply_medium_given_column(logger, model, medium, dbexp['media'][medium])
        if response == 1: return 1
    
            
        # check separately for each biomass precursor:
        # force 'atp_c' as first:
        universal_precs = ['atp_c'] + [m.id for m in universe.reactions.Biomass.reactants if m.id not in ['atp_c', 'h2o_c']]
        for mid in universal_precs:
            # skip conditional precursors: 
            if mid in [m.id for m in model.reactions.Biomass.reactants]:
                
            
                response, flux, status = gempipe.can_synth(model, mid=mid)
                if response == True:
                    df_E.loc[mid, f'{medium}'] = '/'
                else:
                    df_E.loc[mid, f'{medium}'] = 'blocked'
    
    
    return df_E
