


def clean_formula(formula):
    
    # avoid confusion with 'C':
    formula = formula.replace('Ca', '').replace('Co', '').replace('Cu', '').replace('Cd', '').replace('Cr', '').replace('Cs', '').replace('Cl', '')   
    # avoid confusion with 'N':
    formula = formula.replace('Na', '').replace('Nb', '').replace('Ni', '').replace('Ne', '')
    # avoid confusion with 'P':
    formula = formula.replace('Pd', '').replace('Pt', '').replace('Pb', '').replace('Po', '')
    # avoid confusion with 'S':
    formula = formula.replace('Sc', '').replace('Si', '').replace('Sn', '').replace('Sb', '').replace('Se', '')
    
    return formula



def get_CNPS_sources(model):
    
    CNPS_sources = {'C': set(), 'N': set(), 'P': set(), 'S': set()}
    for r in model.reactions: 
        if len(r.metabolites)==1 and list(r.metabolites)[0].id.endswith('_e'):
            m = list(r.metabolites)[0]
            
            formula = m.formula
            formula = clean_formula(formula)
            
            if 'C' in formula: CNPS_sources['C'].add(r.id)
            if 'N' in formula: CNPS_sources['N'].add(r.id)
            if 'P' in formula: CNPS_sources['P'].add(r.id)
            if 'S' in formula: CNPS_sources['S'].add(r.id)
    
    return CNPS_sources


    
def get_source_name(atom):
    
    if atom=='C': return 'carbon'
    elif atom=='N': return 'nitrogen'
    elif atom=='P': return 'phosphorus'
    elif atom=='S': return 'sulfur'
    
    
    
def cnps_on_media(logger, model, expcon, media, cnps):
    
    
    # prepare biomass sheet for excel output
    df_C = pnd.DataFrame()
    
    
    # get involved media:
    if cnps == '-':
        return df_C
    if media == '-':
        logger.info(f"No media provided: alternative substrate analysis will be skipped.")
        return df_C
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # get main/starting C/N/P/S sources:
    if cnps == 'std': cnps = 'glc__D,nh4,pi,so4'
    startings = cnps.split(',')
    if len(startings) != 4: 
        logger.error(f"Starting sources must be 4: C, N, P, and S, in this order ({len(startings)} provided: {startings}).")
        return 1
    modeled_rids = [r.id for r in model.reactions]
    source_to_exr = {}
    for mid, source in zip(startings, ['C','N','P','S']):
        if mid.endswith('_e'): 
            mid_e = mid
        else: mid_e = mid + '_e'
        exr_id = f'EX_{mid_e}'
        if exr_id not in modeled_rids:
            logger.error(f"Expected exchange for {source} source not found (provided metabolite: '{mid}'; expected exchange: '{exr_id}').")
            return 1
        else:
            m = model.metabolites.get_by_id(mid_e)
            if source not in clean_formula(m.formula):
                logger.error(f"{source} source provided ('{mid}') does not contain {source} atoms.")
                return 1
            else:
                source_to_exr[source] = exr_id
            

    # define rows
    CNPS_sources = get_CNPS_sources(model)
    for source in ['C','N','P','S']:
        for exr_id in CNPS_sources[source]:
            m = list(model.reactions.get_by_id(exr_id).metabolites)[0]
            df_C.loc[f"[{source}] {exr_id}", 'source'] = get_source_name(source)
            df_C.loc[f"[{source}] {exr_id}", 'exchange'] = exr_id 
            df_C.loc[f"[{source}] {exr_id}", 'name'] = m.name    
    
    
    logger.info(f"Performing alternative substrate analysis on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_C[f'{medium}'] = None
        logger.debug(f"Performing alternative substrate analysis on medium '{medium}'...")
        
        
        not_part = set()
        for source in ['C','N','P','S']:
            for exr_id in CNPS_sources[source]:
                
                # apply medium
                response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
                if response == 1: return 1
            
                
                # maybe the starting substrate is not part of the medium
                if source_to_exr[source] not in list(model.medium.keys()):
                    not_part.add(f"[{source}] {source_to_exr[source]}")
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"NA"
                    continue
                
            
                model.reactions.get_by_id(source_to_exr[source]).lower_bound = -0
                obj0 = verify_growth(model, boolean=False)
                model.reactions.get_by_id(exr_id).lower_bound = -1000
                obj1 = verify_growth(model, boolean=False)
                
                
                if obj1 == 'infeasible':
                    df_C.loc[f"[{source}] {exr_id}", medium] = 'infeasible'
                elif obj0 == 'infeasible':
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"{obj1} (Δ=/)"
                else:
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"{obj1} (Δ={obj1-obj0})"
        
    
        # log if some starting source was not contained in this medium
        if not_part != set(): 
            logger.debug(f"Specified starting sources {not_part} were not contained in medium '{medium}'.")
    
    return df_C