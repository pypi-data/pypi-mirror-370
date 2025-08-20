import warnings


import cobra



def import_from_universe(model, universe, rid, bounds=None, gpr=None):

    
    # get the universal reaction
    ru = universe.reactions.get_by_id(rid)
    
    # create a new empty reaction
    r = cobra.Reaction(rid)
    model.add_reactions([r])
    r = model.reactions.get_by_id(rid)
    
    # copy the name
    r.name = ru.name
    
    # build string all universal metabolites are still there
    # (remove__disconnected is called later):
    r.build_reaction_from_string(ru.reaction)
    
    # set bounds
    if bounds != None: r.bounds = bounds
    else: r.bounds = ru.bounds
        
    # set GPR
    if gpr != None:
        r.gene_reaction_rule = gpr
    else:
        r.gene_reaction_rule = ''
    r.update_genes_from_gpr()



def include_forced(logger, model, universe, force_inclusion):
    
    
    if force_inclusion != '-':
        introduced_rids = []
        forced_rids = force_inclusion.split(',')
        
        modeled_rids = [r.id for r in model.reactions]
        universal_rids = [r.id for r in universe.reactions]
        
        for rid in forced_rids: 
            
            if rid not in universal_rids:
                logger.debug(f"Ignoring reaction '{rid}' since it's not included in the universe.")
                continue
            
            if rid not in modeled_rids:
                import_from_universe(model, universe, rid, gpr='')
                introduced_rids.append(rid)
                logger.debug(f"Reaction '{rid}' forcibly included as orphan.")
                
            else:
                logger.debug(f"Requested reaction '{rid}' was already included.")
                
        logger.info(f"Forcibly included {len(introduced_rids)} reactions as orphans.")
        
        

def get_repository_nogenes(logger, universe, exclude_orphans):
    # Provide a gene-free, evetually orphan-free  repository: reference or universe.


    # make an editable copy:
    repository_nogenes = universe.copy()
    
    
    if exclude_orphans:
            
        # collect orphan:
        to_remove = []
        for r in repository_nogenes.reactions: 
            if len(r.genes) == 0:
                if len(r.metabolites) != 1 and r.id != 'Biomass':   # exclude exchanges/sinks/demands/biomass
                    to_remove.append(r)
                    logger.debug(f"Removing orphan: {r.id} ({r.reaction}).")
              
        # remove orphan reactions:
        with warnings.catch_warnings():
            # avoid warnings like "python3.9/site-packages/cobra/core/group.py:147: UserWarning: need to pass in a list"
            warnings.simplefilter("ignore")
            repository_nogenes.remove_reactions(to_remove)
        logger.info(f"Removed {len(to_remove)} orphans before gap-filling.")

    # remove genes to avoid the "ValueError: id purP is already present in list"
    cobra.manipulation.delete.remove_genes(repository_nogenes, [g.id for g in repository_nogenes.genes], remove_reactions=False)

    
    return repository_nogenes




    
    

