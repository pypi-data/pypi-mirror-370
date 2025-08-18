import cobra


from .manual import get_deprecated_kos
from .manual import get_custom_groups



def translate_annotate_genes(logger, model, idcollection_dict):
    

       
    ko_to_name = idcollection_dict['ko_to_name']
    ko_to_symbols = idcollection_dict['ko_to_symbols']
    ko_to_ecs = idcollection_dict['ko_to_ecs']
    ko_to_cogs = idcollection_dict['ko_to_cogs']
    ko_to_gos = idcollection_dict['ko_to_gos']
    
    
    # translation dicts: assign to each KO a symbol that is unique in the universe model.
    ko_to_sym = {}
    sym_to_ko = {}
    cnt = 0
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        ko = g.id
        cnt += 1
        
        if ko in get_deprecated_kos():
            # if the ko is deprecated, it was not included in 'ko_to_symbols'
            ko_to_sym[ko] = ko
            sym_to_ko[ko] = ko
            continue
            
        for symbol in ko_to_symbols[ko]:  # iterate the available symbols for this KO
            if symbol not in sym_to_ko.keys():   # take the first available (not yet used)
                ko_to_sym[ko] = symbol
                sym_to_ko[symbol] = ko
                break
        
        if cnt != len(ko_to_sym):  # no symbol was assigned (symbol was already taken by another KO)
            cnt_dups = 2
            symbol = list(ko_to_symbols[ko])[0] + f'_{cnt_dups}'   # generate a new symbol
            while cnt != len(ko_to_sym):   # until a symbol is assigned
                if symbol not in sym_to_ko.keys():   # if the new symbol fits
                    ko_to_sym[ko] = symbol
                    sym_to_ko[symbol] = ko
                cnt_dups += 1
                symbol = list(ko_to_symbols[ko])[0] + f'_{cnt_dups}'   # retry with the next one
                

                
    
    # insert annotations
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        ko = g.id
        g.annotation['ko'] = ko
        
        if ko not in get_deprecated_kos():
            # deprecated kos are missing from these dicts
            g.name = ko_to_name[ko]
            g.annotation['symbols'] = list(ko_to_symbols[ko])
            g.annotation['ec'] = list(ko_to_ecs[ko])
            g.annotation['cog'] = list(ko_to_cogs[ko])
            g.annotation['go'] = list(ko_to_gos[ko])
        
    
        
    # finally apply translations of IDs
    translation_dict = ko_to_sym
    translation_dict['orphan'] = 'orphan'
    translation_dict['spontaneous'] = 'spontaneous'
    cobra.manipulation.rename_genes(model, translation_dict)
    
    
    return model
    


def set_up_groups(logger, model, idcollection_dict):
    

       
    kr_to_maps = idcollection_dict['kr_to_maps']
    map_to_name = idcollection_dict['map_to_name']
    kr_to_mds = idcollection_dict['kr_to_mds']
    md_to_name = idcollection_dict['md_to_name']
    
    
    # define groups of available contents
    groups = {}   # mixing maps and mds
    for r in model.reactions:
        
        if 'kegg.reaction' not in r.annotation.keys():
            continue   # Biomass, exchanges, demands, sinks, transporters
        kr_ids = r.annotation['kegg.reaction']
            
        for kr_id in kr_ids:
            if kr_id == 'RXXXXX':
                continue
            
            # insert maps
            for map_id in kr_to_maps[kr_id]:
                if map_id not in groups.keys():
                    groups[map_id] = set()
                groups[map_id].add(r)
                
            # insert mds
            for md_id in kr_to_mds[kr_id]:
                if md_id not in groups.keys():
                    groups[md_id] = set()
                groups[md_id].add(r)
                
    # finally insert groups
    for group_id in groups.keys():
                
        # get group name
        if group_id.startswith('map'):
            name = map_to_name[group_id]
        if group_id.startswith('M'):
            name = md_to_name[group_id]
                    
        actual_group = cobra.core.Group(
            group_id, 
            name = name,
            members = list(groups[group_id]),
            kind = 'partonomy',
        )
        model.add_groups([actual_group])
        
        
        
    # insert custom groups:
    custom_groups = get_custom_groups()
    for group_id in custom_groups.keys():
        actual_group = cobra.core.Group(
            group_id, 
            name = group_id,
            members = [model.reactions.get_by_id(rid) for rid in custom_groups[group_id]],
            kind = 'partonomy',
        )
        model.add_groups([actual_group])
        
        
    return model
