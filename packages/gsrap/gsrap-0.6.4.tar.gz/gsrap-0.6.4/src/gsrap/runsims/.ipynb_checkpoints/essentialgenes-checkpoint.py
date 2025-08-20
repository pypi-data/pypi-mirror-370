


def essential_genes_on_media(logger, model, expcon, media, essential):
        
    
    # prepare biomass sheet for excel output
    df_E = pnd.DataFrame()
    
    
    # get involved media:
    if essential == False:
        return df_E
    if media == '-':
        logger.info(f"No media provided: essential genes prediction will be skipped.")
        return df_E
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    

    # define rows
    for g in model.genes:
        if g.id in ['spontaneous', 'orphan']:
            continue
        df_E.loc[f"{g.id}", 'name'] = g.name    
        df_E.loc[f"{g.id}", 'involving'] = '; '.join([r.id for r in g.reactions])
    
    
    logger.info(f"Predicting essential genes on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_E[f'{medium}'] = None
        logger.debug(f"Predicting essential genes on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # verify growth:
        obj = verify_growth(model, boolean=False)
        if obj in ['infeasible', 0]:
            df_E[f'{medium}'] = 'NA'
            continue
    
        
        single = cobra.flux_analysis.single_gene_deletion(model)
        for index, row in single.iterrows(): 
            gid = list(row['ids'])[0]  # they are single deletions
            if gid in ['spontaneous', 'orphan']:
                continue
                

            if row['status'] == 'infeasible': 
                df_E.loc[f"{gid}", medium] = 'True'
            elif row['growth'] < get_optthr():
                df_E.loc[f"{gid}", medium] = 'True'
            else: 
                df_E.loc[f"{gid}", medium] = round(row['growth'], 3)
    
    return df_E