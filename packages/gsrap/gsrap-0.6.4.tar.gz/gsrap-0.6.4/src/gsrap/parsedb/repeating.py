import pandas as pnd
import cobra


from .manual import get_deprecated_kos
from .manual import get_rids_with_mancheck_gpr



def check_gpr(logger, rid, row, kr_ids, idcollection_dict, addtype='R'): 
    
    itemtype = 'Reaction' if addtype=='R' else 'Transporter'
    
    # check presence of the GPR
    if pnd.isna(row['gpr_manual']): 
        logger.error(f"{itemtype} '{rid}' has missing GPR: '{row['gpr_manual']}'.")
        return 1
    
    # get ko_ids in this reaction:
    ko_ids_parsed = row['gpr_manual'].strip()
    ko_ids_parsed = ko_ids_parsed.replace(' and ', ',')
    ko_ids_parsed = ko_ids_parsed.replace(' or ', ',')
    ko_ids_parsed = ko_ids_parsed.replace('(', '')
    ko_ids_parsed = ko_ids_parsed.replace(')', '')
    ko_ids_parsed = ko_ids_parsed.split(',')
    
    
    # collect all the ko_ids for this reaction:
    if addtype=='R':
        ko_for_rid = set()   
        for kr_id in kr_ids:
            if kr_id == 'RXXXXX': 
                continue
            ko_for_rid = ko_for_rid.union(idcollection_dict['kr_to_kos'][kr_id])
            
    
    # check if these ko_ids exist:
    for ko_id in ko_ids_parsed:
        ko_id = ko_id.strip() 
        
        if ko_id in get_deprecated_kos():
            pass
        elif ko_id not in idcollection_dict['ko'] and ko_id != 'spontaneous' and ko_id != 'orphan':
            logger.error(f"{itemtype} '{rid}' has an invalid KEGG Ortholog: '{ko_id}'.")
            return 1
        
        
        # check if these ko_ids are really assigned to this reaction:
        if addtype=='R':
            if ko_id not in ko_for_rid and ko_id != 'spontaneous' and ko_id != 'orphan':
                if kr_id != 'RXXXXX':
                    if rid not in get_rids_with_mancheck_gpr():
                        logger.debug(f"Ortholog '{ko_id}' should not be linked to reaction '{rid}' (available for {kr_ids}: {ko_for_rid}).")
            
    
    # check if some ko_ids are missing from this reaction:
    if addtype=='R':
        missing_ko_ids = ko_for_rid - (set(ko_ids_parsed) - set(['spontaneous', 'orphan']))
        if len(missing_ko_ids) > 0:
            logger.error(f"Orthologs {missing_ko_ids} are missing from reaction '{rid}' ({kr_ids}).")
            return 1
            
            
    return 0
                


def add_reaction(logger, model, rid, row, kr_ids, addtype='R'):
    
    
    itemtype = 'Reaction' if addtype=='R' else 'Transporter'
    
    
    # create a frash reaction
    r = cobra.Reaction(rid)
    model.add_reactions([r])
    r = model.reactions.get_by_id(rid)
    
    
    # copy name and equation:
    r.build_reaction_from_string(row['rstring'])
    r.name = row['name'].strip()
    
    
    # handle bounds:
    if ' --> ' in row['rstring']:
        r.bounds = (0, 1000)
    else:
        r.bounds = (-1000,  1000)
    
    
    # handle GPR
    r.gene_reaction_rule = row['gpr_manual'].strip()
    if r.gene_reaction_rule == 'orphan': 
        r.gene_reaction_rule = ''    # don't want 'orphan' as artificial gene in adition to 'spontaneous'!
    r.update_genes_from_gpr()
    
    
    # handle metabolites:
    for m in r.metabolites:
        if m.formula == None or m.charge == None:
            logger.error(f"Metabolite '{m.id}' appears in '{r.id}' but was not previously defined.")
            return 1
        
        
    # add kr annotations to model
    r.annotation['kegg.reaction'] = kr_ids
        
        
    # check if unbalanced
    if r.check_mass_balance() != {}: 
        logger.error(f"{itemtype} '{r.id}' is unbalanced: {r.check_mass_balance()}.")
        return 1    
    
    
    return 0



def check_rstring_arrow(logger, rid, row, addtype='R'):
    
    itemtype = 'Reaction' if addtype=='R' else 'Transporter'
    
    
    if pnd.isna(row['rstring']): 
        logger.error(f"{itemtype} '{rid}' has no definition (rstring).")
        return 1
    if ' --> ' not in row['rstring'] and ' <=> ' not in row['rstring']:
        logger.error(f"{itemtype} '{rid}' has invalid arrow: '{row['rstring']}'.")
        return 1
        
        
    return 0



def check_author(logger, mrid, row, db, addtype='R'): 
    
    
    if addtype=='M':
        itemtype = 'Metabolite'
    elif  addtype=='R' :
        itemtype = 'Reaction'
    else: itemtype = 'Transporter'
    
    
    if pnd.isna(row['author']): 
        logger.error(f"{itemtype} '{mrid}' has no author.")
        return 1
    
    authors = set()
    for author in row['author'].split(';'):
        author = author.strip()
        authors.add(author)
        if author not in db['authors']['username'].to_list(): 
            logger.error(f"{itemtype} '{mrid}' has invalid author: '{author}'.")
            return 1
    
    
    return list(authors)
    
    
    
