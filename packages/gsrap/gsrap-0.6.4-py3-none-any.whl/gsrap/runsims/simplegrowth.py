import pandas as pnd
import cobra
import gempipe


from ..commons import apply_medium_given_column
from ..commons import verify_growth




def grow_on_media(logger, model, dbexp, media, fva, universe_in_parsedb=False):
    
    
    # if working with the universe:
    if universe_in_parsedb:
        log_for_parsedb = []
    
    
    # check if requested
    df_G = pnd.DataFrame()
    obj_id = 'max(obj)'
    
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: growth simulations will be skipped.")
        return df_G
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in dbexp['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(dbexp['media'].columns)}.")
        return 1
    
    
    # prepare sheet for excel output
    df_G.loc[obj_id, 'name'] = f'Objective reaction {gempipe.get_objectives(model)}'
    for r in model.reactions:
        df_G.loc[r.id, 'name'] = r.name
        
        
    logger.info(f"Testing growth on {len(media)} media...")
    for medium in media: 
        if medium not in dbexp['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column con the excel output
        df_G[f'{medium}'] = '/'
        logger.debug(f"Growing on medium '{medium}'...")
                    
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, dbexp['media'][medium])
        if response == 1: return 1

    
        # perform FBA
        res_fba = verify_growth(model, boolean=False)
        df_G.loc[obj_id, f'{medium}'] = res_fba
        if universe_in_parsedb:
            log_for_parsedb.append(f"'{medium}': {res_fba}")
        
        
        # perform FVA if requested:
        if fva and (res_fba not in [0, 'infeasible']):
            logger.debug(f"FVA on medium '{medium}'...")
            df_fva = cobra.flux_analysis.flux_variability_analysis(model, model.reactions, fraction_of_optimum=0.9)
            for rid, row in df_fva.iterrows():
                df_G.loc[rid, f'{medium}'] = f"({round(row['minimum'], 3)}, {round(row['maximum'], 3)})"

    
    if universe_in_parsedb:
        logger.info(f"Results: {'; '.join(log_for_parsedb)}.")
    return df_G