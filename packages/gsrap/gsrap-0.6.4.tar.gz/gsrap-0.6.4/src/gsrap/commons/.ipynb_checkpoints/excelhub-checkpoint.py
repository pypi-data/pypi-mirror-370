import pandas as pnd



def write_excel_model(model, filepath, df_E, df_B, df_P, df_S):
    
    df_M = []
    df_R = []
    df_T = []
    df_A = []
    
    
    # format df_E:  # biomass precursors biosynthesis
    if df_E is not None:
        df_E.insert(0, 'mid', '')  # new columns as first
        df_E['mid'] = df_E.index
        df_E = df_E.reset_index(drop=True)
    
    # format df_B:  # biomass assembly
    if df_B is not None:
        df_B.insert(0, 'mid', '')  # new columns as first
        df_B['mid'] = df_B.index
        df_B = df_B.reset_index(drop=True)
    
    # format df_P:  phenotype screening (Biolog(R))
    if df_P is not None:
        df_P.insert(0, 'plate:well', '')  # new columns as first
        df_P['plate:well'] = df_P.index
        df_P = df_P.reset_index(drop=True)
        
    # format df_S:  metabolite synthesis
    if df_S is not None:
        df_S.insert(0, 'mid', '')  # new columns as first
        df_S['mid'] = df_S.index
        df_S = df_S.reset_index(drop=True)
            
        
    for m in model.metabolites: 
        
        # get kc codes: 
        if 'kegg.compound' not in m.annotation.keys():  kc_ids = ''
        else:  
            kc_ids = m.annotation['kegg.compound']
            if type(kc_ids) == str: kc_ids = [kc_ids]
            kc_ids = '; '.join([i for i in kc_ids if i!='CXXXXX'])
        
        df_M.append({'mid': m.id, 'formula': m.formula, 'charge': m.charge, 'kc': kc_ids, 'name': m.name})

        
    for r in model.reactions:
        
        # handle artificial reactions
        if r.id == 'Biomass':
            df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'biomass', 'name': r.name})
                
        elif len(r.metabolites) == 1:
            if len(r.metabolites)==1 and list(r.metabolites)[0].id.rsplit('_',1)[-1] == 'e': 
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'exchange', 'name': r.name})
            elif r.lower_bound < 0 and r.upper_bound > 0:
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'sink', 'name': r.name})
            elif r.lower_bound == 0 and r.upper_bound > 0:
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'demand', 'name': r.name})
        
        else: # more than 1 metabolite involved
            
            # get kr codes: 
            if 'kegg.reaction' not in r.annotation.keys():  kr_ids = ''
            else:  
                kr_ids = r.annotation['kegg.reaction']
                if type(kr_ids) == str: kr_ids = [kr_ids]
                kr_ids = '; '.join([i for i in kr_ids if i!='RXXXXX'])

            # introduce reaction in the correct table: 
            r_dict = {'rid': r.id, 'rstring': r.reaction, 'kr': kr_ids, 'gpr': r.gene_reaction_rule, 'name': r.name}
            if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites])) == 1:
                df_R.append(r_dict)
            else: df_T.append(r_dict)
    
    
    df_M = pnd.DataFrame.from_records(df_M)
    df_R = pnd.DataFrame.from_records(df_R)
    df_T = pnd.DataFrame.from_records(df_T)
    df_A = pnd.DataFrame.from_records(df_A)
    with pnd.ExcelWriter(filepath) as writer:
        df_M.to_excel(writer, sheet_name='Metabolites', index=False)
        df_R.to_excel(writer, sheet_name='Reactions', index=False)
        df_T.to_excel(writer, sheet_name='Transporters', index=False)
        df_A.to_excel(writer, sheet_name='Artificials', index=False)
        if df_E is not None and len(df_E)!=0: df_E.to_excel(writer, sheet_name='Precursors', index=False)
        if df_B is not None: df_B.to_excel(writer, sheet_name='Biomass', index=False)
        if df_P is not None and len(df_P)!=0: df_P.to_excel(writer, sheet_name='Biolog®', index=False)
        if df_S is not None and len(df_S.columns)>2: df_S.to_excel(writer, sheet_name='Biosynth', index=False) 
        
        
    sheets_dict = {
        'model_id': model.id,
        'Metabolites': df_M,
        'Reactions': df_R,
        'Transporters': df_T,
        'Artificials': df_A,
        'Precursors': df_E,
        'Biomass': df_B,
        'Biolog': df_P,
        'Biosynth': df_S,
    }
    return sheets_dict



def comparative_table(logger, outdir, sheets_dicts):
    
    
    # create topology table (reaction presence / absence matrix): 
    df_topology = pnd.DataFrame()
    for sheets_dict in sheets_dicts:
        for index, row in sheets_dict['Reactions'].iterrows():
            if row['rid'] not in df_topology.index:
                df_topology.loc[row['rid'], 'rstring'] = row['rstring']
                df_topology.loc[row['rid'], 'kr'] = row['kr']
                df_topology.loc[row['rid'], 'name'] = row['name']
            df_topology.loc[row['rid'], sheets_dict['model_id']] = 1
    for sheets_dict in sheets_dicts:  # replace missing values:
        df_topology = df_topology.fillna({sheets_dict['model_id']: 0})
        
        
    # create GPR table (reaction presence / absence matrix): 
    df_gprs = pnd.DataFrame()
    for sheets_dict in sheets_dicts:
        for index, row in sheets_dict['Reactions'].iterrows():
            if row['rid'] not in df_gprs.index:
                df_gprs.loc[row['rid'], 'rstring'] = row['rstring']
                df_gprs.loc[row['rid'], 'kr'] = row['kr']
                df_gprs.loc[row['rid'], 'name'] = row['name']
            df_gprs.loc[row['rid'], sheets_dict['model_id']] = row['gpr']
    for sheets_dict in sheets_dicts:  # replace missing values:
        df_gprs = df_gprs.fillna({sheets_dict['model_id']: 'missing'})
        
    
    with pnd.ExcelWriter(f"{outdir}/comparison.mkmodel.xlsx") as writer:
        df_topology.to_excel(writer, sheet_name='Topology', index=False)
        df_gprs.to_excel(writer, sheet_name='GPRs', index=False)
    logger.info(f"'{outdir}/comparison.mkmodel.xlsx' created!")
        
    