import warnings



def log_metrics(logger, model):
    
    
    G = len([g.id for g in model.genes])
    R = len([r.id for r in model.reactions if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites]))==1 and len(r.metabolites)!=1 and r.id!='Biomass'])
    T = len([r.id for r in model.reactions if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites]))!=1 and len(r.metabolites)!=1 and r.id!='Biomass'])
    A = len([r.id for r in model.reactions if len(r.metabolites)==1 or r.id=='Biomass'])
    M = len([m.id for m in model.metabolites])
    uM = len(set([m.id.rsplit('_',1)[0] for m in model.metabolites]))
    gr = len([gr.id for gr in model.groups])
    bP = len(set([m.id for m in model.reactions.get_by_id('Biomass').reactants]) - set(['atp_c', 'h2o_c']))

    
    logger.info(f"Done! [G: {G}, R: {R}, T: {T}, A: {A}, uM: {uM}, bP: {bP}]")
    
    
    
def log_unbalances(logger, model):
    
    
    balance_threshold = 1e-10
    
    cnt_mass = 0
    cnt_charge = 0
    for r in model.reactions: 
        if len(r.metabolites) != 1 and r.id != 'Biomass':   # exclude artificials
            
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # avoids warnings like "UserWarning: 9.823 is not an integer (in formula C9.823H5.5789999999999935N3.6769999999999996O3.628P1.0)"

                
                check = r.check_mass_balance()
                for key, value in check.items():
                    if abs(value) > balance_threshold:

                        if key == 'charge':
                            cnt_charge += 1
                            break
                        else:
                            cnt_mass += 1
                            break
    
    logger.info(f"Found {cnt_mass} mass and {cnt_charge} charge unbalances >{balance_threshold}.")
        
        
        
def show_contributions(logger, db):
    
    # create a counter for each author
    cnt = {author: 0 for author in db['authors']['username']}
    cnt_tot = 0
    for rid, row in db['R'].iterrows():
        for author in row['author'].split(';'):
            author = author.rstrip().strip()
            cnt[author] += 1
            cnt_tot += 1
    for rid, row in db['T'].iterrows():
        for author in row['author'].split(';'):
            author = author.rstrip().strip()
            cnt[author] += 1
            cnt_tot += 1
        
    # compute percentages:
    pct = {author: cnt[author]/cnt_tot*100 for author in cnt.keys()}
    # sort in descending order: 
    pct = dict(sorted(pct.items(), key=lambda item: item[1], reverse=True))
    # convert to string:
    pct = {author: f'{round(pct[author],2)}%' for author in pct.keys()}
    logger.debug(f"Contributions: {pct}.")