import gempipe



def apply_medium_given_column(logger, model, medium, column, is_reference=False):
        
        
    # retrieve metadata
    description = column.iloc[0]
    doi = column.iloc[1]
    author = column.iloc[2]
    units = column.iloc[3]

    
    # convert substrates to dict
    column = column.iloc[4:]
    column = column.to_dict()

    
    # add trace elements:
    column['fe2'] = 'NL'
    column['mobd'] = 'NL'
    column['cobalt2'] = 'NL'


    # reset exchanges
    gempipe.reset_growth_env(model)    
    modeled_rids = [r.id for r in model.reactions]


    for substrate, value in column.items():

        if type(value)==float:
            continue   # empty cell, exchange will remain close

            
        # check if exchange is modeled
        if is_reference == False: 
            if f'EX_{substrate}_e' not in modeled_rids:
                logger.error(f"No exchange reaction found for substrate '{substrate}' in medium '{medium}'.")
                return 1
        else:  # external reference models might follow different standards.
            # The exr might not be present. 
            if f'EX_{substrate}_e' not in modeled_rids:
                logger.info(f"Reference has no exchange reaction for '{substrate}' in medium '{medium}': this substrate will be ignored.")
                continue


        # case "not limiting"
        value = value.strip().rstrip()
        if value == 'NL':   # non-limiting case
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = -1000


        # case "single value"
        elif '+-' not in value and '±' not in value:  # single number case
            value = value.replace(' ', '')  # eg "- 0.03" --> "-0.03"
            try: value = float(value)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value}.")
                return 1
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = value


        # case "with experimental error"
        else:  # value +- error
            if '±' in value: 
                value, error = value.split('±', 1)
            else: value, error = value.split('+-', 1)
            value = value.rstrip()
            error = error.strip()
            value = value.replace(' ', '')  # eg "- 0.03" --> "-0.03"
            try: value = float(value)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value} +- {error}.")
                return 1
            try: error = float(error)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value} +- {error}.")
                return 1
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = value -error
            model.reactions.get_by_id(f'EX_{substrate}_e').upper_bound = value +error

    return 0