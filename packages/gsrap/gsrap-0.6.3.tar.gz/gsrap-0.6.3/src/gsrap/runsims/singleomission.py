


def omission_on_media(logger, model, expcon, media, omission):
        
    
    # define metabolites for single omission experiments  
    # Note: they are all universal
    pure_mids = set([
        # 20 aminoacids
        'ala__L', 'arg__L', 'asn__L', 'asp__L', 'cys__L', 
        'gln__L', 'glu__L', 'gly', 'his__L', 'ile__L', 
        'leu__L', 'lys__L', 'met__L', 'phe__L', 'pro__L', 
        'ser__L', 'thr__L', 'trp__L', 'tyr__L', 'val__L', 
        # 5 nucleotides
        'ade', 'gua', 'csn', 'thym', 'ura'])
    modeled_rids = [r.id for r in model.reactions]
    
    
    # prepare biomass sheet for excel output
    df_O = pnd.DataFrame()
    
    
    # get involved media:
    if omission == False:
        return df_O
    if media == '-':
        logger.info(f"No media provided: single omissions will be skipped.")
        return df_O
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
        
    # check if the target exchange reaction exists:
    for pure_mid in list(pure_mids):
        if f'EX_{pure_mid}_e' not in modeled_rids:
            logger.debug(f"Exchange reaction 'EX_{pure_mid}_e' not found during single omissions: it will be ignored.")
            df_O.loc[pure_mid, 'name'] = 'NA'
            pure_mids = pure_mids - set([pure_mid]) 
        else:  # initialize dataframe
            m = model.metabolites.get_by_id(f'{pure_mid}_e')
            df_O.loc[pure_mid, 'name'] = m.name
    
    
    logger.info(f"Performing single omissions on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_O[f'{medium}'] = None
        logger.debug(f"Performing single omissions on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1


        # set up exchange reactions:
        for pure_mid1 in pure_mids:
            for pure_mid2 in pure_mids:
                exr_id = f'EX_{pure_mid2}_e'
                
                if pure_mid2 != pure_mid1:
                    model.reactions.get_by_id(exr_id).lower_bound = -1000
                else:
                    model.reactions.get_by_id(exr_id).lower_bound = -0
                    
                    
            # perform FBA
            res_fba = verify_growth(model, boolean=False)
            df_O.loc[pure_mid1, f'{medium}'] = res_fba
               
            
    return df_O