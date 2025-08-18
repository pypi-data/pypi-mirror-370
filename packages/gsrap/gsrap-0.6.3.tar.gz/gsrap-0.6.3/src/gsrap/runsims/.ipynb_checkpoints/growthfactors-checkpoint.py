


def growth_factors_on_media(logger, model, expcon, media, factors):
        
    
    # prepare biomass sheet for excel output
    df_F = pnd.DataFrame()
    
    
    # get involved media:
    if factors == False:
        return df_F
    if media == '-':
        logger.info(f"No media provided: essential genes prediction will be skipped.")
        return df_F
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # define rows
    df_F['mid'] = ''
    df_F['name'] = ''

    
    logger.info(f"Predicting growth factors on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_F[f'{medium}'] = None
        logger.debug(f"Predicting growth factors on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # verify growth:
        obj = verify_growth(model, boolean=False)
        if obj not in ['infeasible', 0]:
            df_F[f'{medium}'] = ''
        else:
            while obj in ['infeasible', 0]:
                res_dict = gempipe.sensitivity_analysis(model, scaled=False, top=1)
                for exr_id, value in res_dict.items():
                    if value < 0:
                        model.reactions.get_by_id(exr_id).lower_bound = -1000
                        obj = verify_growth(model, boolean=False)
                        df_F.loc[exr_id, f'{medium}'] = 'ADD'

         
    # populate 'mid'/'name' columns:
    for exr_id, row in df_F.iterrows():
        r = model.reactions.get_by_id(exr_id)
        m = list(r.metabolites)[0]
        df_F.loc[exr_id, 'mid'] = m.id.rsplit('_', 1)[0]
        df_F.loc[exr_id, 'name'] = m.name
    # replace index with 'mid':
    df_F = df_F.set_index('mid', drop=True)
        
        
    return df_F
