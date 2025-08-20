import warnings
import logging



def remove_forced(logger, model, universe, force_removal):
    
    
    if force_removal != '-':
        removed_rids = []
        forced_rids = force_removal.split(',')
        
        modeled_rids = [r.id for r in model.reactions]
        universal_rids = [r.id for r in universe.reactions]
        
        for rid in forced_rids: 
            
            if rid not in universal_rids:
                logger.info(f"Ignoring reaction ID '{rid}' since it's not included in the universe.")
                continue
            
            if rid not in modeled_rids:
                logger.debug(f"Requested reaction ID '{rid}' was already excluded from the model.")
            else:
                removed_rids.append(rid)

        # remove collected reactions:
        with warnings.catch_warnings():
            # avoid warnings like "python3.9/site-packages/cobra/core/group.py:147: UserWarning: need to pass in a list"
            model.remove_reactions(removed_rids) # this works also with rids instaead of Rs

        logger.info(f"Reactions forcibly removed: {removed_rids}.")
        


def remove_disconnected(logger, model):
    
    
    to_remove = []
    for m in model.metabolites:
        if len(m.reactions) == 0:
            to_remove.append(m)
    model.remove_metabolites(to_remove)
    logger.info(f"Removed {len(to_remove)} disconnected metabolites.")
    
    
    return model

    
    
def remove_universal_orphans(logger, model):
    
    
    to_remove = []
    for r in model.reactions:
        if len(r.metabolites) != 1 and r.id != 'Biomass':  # exclude artificials
            if r.gene_reaction_rule == '': 
                logger.debug(f"Removing universal orphan '{r.id}'...")
                to_remove.append(r.id)
            
    
    # trick to avoid the WARNING "cobra/core/group.py:147: UserWarning: need to pass in a list" 
    # triggered when trying to remove reactions that are included in groups. 
    with warnings.catch_warnings():  # temporarily suppress warnings for this block
        warnings.simplefilter("ignore")  # ignore all warnings
        cobra_logger = logging.getLogger("cobra.util.solver")
        old_level = cobra_logger.level
        cobra_logger.setLevel(logging.ERROR)   

        model.remove_reactions(to_remove) 
        logger.info(f"Removed {len(to_remove)} universal orphan reactions.")

        # restore original behaviour: 
        cobra_logger.setLevel(old_level)   
            

    return model
    
    
    
def remove_sinks_demands(logger, model): 
    
    
    to_remove = []
        
        
    for r in model.reactions: 
        if len(r.metabolites) == 1:    # sinks / damands / exchanges
            m = list(r.metabolites)[0]
            if m.id.endswith('_e') == False:   # sinks / damands
                if len(m.reactions) == 1 and list(m.reactions)[0].id == r.id:
                    # if it's associated only with this reaction:
                    logger.debug(f"Removing unused sink/demand '{r.id}'...")
                    to_remove.append(r.id)
                    
    model.remove_reactions(to_remove) 
    logger.info(f"Removed {len(to_remove)} disconnected sink/demand reactions.")
    
    
    return model