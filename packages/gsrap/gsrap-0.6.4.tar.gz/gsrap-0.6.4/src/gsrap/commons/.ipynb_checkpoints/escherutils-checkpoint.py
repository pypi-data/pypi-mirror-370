

def print_json_tree(data, level=0, max_level=2):
    # explore contents of a json object
    
    if level > max_level:
        return
    indent = '  ' * level
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{indent}{key}")
            print_tree(value, level + 1, max_level)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{indent}[{i}]")
            print_tree(item, level + 1, max_level)
            
            

def count_undrawn_rids(logger, universe, lastmap):
    
    
    rids = set([r.id for r in universe.reactions])
    
    drawn_rids = set()
    for key, value in lastmap['json'][1]['reactions'].items():
        drawn_rids.add(value['bigg_id'])
        
        
    remainings = rids - drawn_rids
    filename = lastmap['filename']
    logger.debug(f"Last universal map version detected: '{filename}'.")
    if len(remainings) > 0:
        logger.info(f"Our universal map is {len(remainings)} reactions behind. Please draw!")
    else:
        logger.info(f"Our universal map is {len(remainings)} reactions behind. Thank you ♥")
        