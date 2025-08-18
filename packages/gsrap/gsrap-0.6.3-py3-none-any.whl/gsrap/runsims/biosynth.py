import pandas as pnd
import gempipe


from ..commons import apply_medium_given_column



def biosynthesis_on_media(logger, model, dbexp, media, biosynth):
    
    
    # check if requested
    df_S = pnd.DataFrame()
    if not biosynth:
        return df_S
    
    
    # prepare sheet for excel output
    df_S['name'] = None
    for m in model.metabolites:
        if m.id.endswith('_c'):
            df_S.loc[m.id, 'name'] = m.name
            
            
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: metabolites biosynthesis check will be skipped.")
        return df_S
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in dbexp['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(dbexp['media'].columns)}.")
        return 1
    
    
    logger.info(f"Checking metabolites biosynthesis on {len(media)} media...")
    for medium in media:
        if medium not in dbexp['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_S[f'{medium}'] = None
        logger.debug(f"Checking metabolites biosynthesis on medium '{medium}'...")
            
            
        # apply medium :
        response = apply_medium_given_column(logger, model, medium, dbexp['media'][medium])
        if response == 1: return 1
            
    
        for m in model.metabolites:
            if m.id.endswith('_c'):
                dem = '/'
                binary, obj_value, status = gempipe.can_synth(model, m.id)


                # check if it's dead-end metabolite (dem)
                if binary == False:
                    dem = False
                    is_consumed = False
                    is_produced = False
                    for r in m.reactions:
                        if m.id in [m2.id for m2 in r.reactants]:
                            is_consumed = True
                        if m.id in [m2.id for m2 in r.products]:
                            is_produced = True
                    if   is_consumed and not is_produced:
                        dem = 'no_production'
                    elif is_produced and not is_consumed:
                        dem = 'no_consumption' 

                
                if status == 'infeasible': 
                    df_S.loc[m.id, f'{medium}'] = 'infeasible'
                elif obj_value == 0:
                    if dem == '/':
                        df_S.loc[m.id, f'{medium}'] = 'blocked'
                    else:
                        df_S.loc[m.id, f'{medium}'] = dem
                else:
                    df_S.loc[m.id, f'{medium}'] = obj_value
            
    
    return df_S

