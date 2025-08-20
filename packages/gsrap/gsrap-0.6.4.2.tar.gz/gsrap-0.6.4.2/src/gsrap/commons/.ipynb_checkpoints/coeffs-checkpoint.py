import warnings
from decimal import Decimal


import cobra



def get_uni_biom_coeff():
    
    return 0.00000001



def check_exp_biomass_data(logger, dbexp, biomass):
    
    
    # check if the strain ID is present:
    for sheet in ['MWF', 'DNA', 'RNA', 'PROTS', 'LIPIDS_PL', 'LIPIDS_FA']:
        if biomass not in dbexp[sheet]:
            logger.error(f"ID '{biomass}' not found in sheet '{sheet}'.")
            return 1

    
    # format data
    ftd = dict()  # fraction_to_decimals
    for sheet in ['MWF', 'DNA', 'RNA', 'PROTS', 'LIPIDS_PL', 'LIPIDS_FA']:
        fraction_db = dbexp[sheet][biomass].dropna() # they should be str
        fraction_db = fraction_db.iloc[4:] # ignore ['description', 'doi', 'author', 'units']) 
        ftd[sheet] = {i: Decimal(val) for i, val in fraction_db.items() if Decimal(val) != Decimal('0.0')} # convert to dict
        if sum(ftd[sheet].values()) != Decimal('1.0'):  # check if the sum gives 1 (g/gDW or mol/mol depending on 'sheet')
            logger.error(f"Biomass data provided in sheet '{sheet}' for ID '{biomass}' does not sum up to 1.0. Missing mass is {Decimal('1.0')-sum(ftd[sheet].values())}.")
            return 1
        
    
    # normalize if ashes are present: 
    if 'ASHES' in ftd['MWF'].keys():
        logger.info(f"Found 'ASHES' > 0 in '{biomass}' data: normalizing...")
        #
        # compute sum(gDW) without ashes: 
        del ftd['MWF']['ASHES']
        new_sum = Decimal(0.0)
        for key, value in ftd['MWF'].items():
            new_sum = new_sum + value
        #
        # normalize coefficients:
        for key, value in ftd['MWF'].items():
            ftd['MWF'][key] = ftd['MWF'][key] / new_sum
    
    
    return (ftd['MWF'], ftd['DNA'], ftd['RNA'], ftd['PROTS'], ftd['LIPIDS_PL'], ftd['LIPIDS_FA'])



def rstring_builder(reactant_to_coeffs, product_to_coeffs):
    
    
    rstring = ''
    
    # parse reactants
    for rid, coeff in reactant_to_coeffs.items():
        if rstring != '':
            rstring = rstring + ' + '
        rstring = rstring + f"{coeff} {rid}"
        
    # add arrow:
    rstring = rstring + ' --> '
    
    # parse products: 
    for rid, coeff in product_to_coeffs.items():
        if rstring.endswith(' --> ') == False:
            rstring = rstring + ' + '
        rstring = rstring + f"{coeff} {rid}"
    
    
    return rstring
    
    
    
def get_fraction_dict_charge_molweight(model, reactant_to_coeffs, product_to_coeffs):
    # written for DNA, but it's general!
    
    
    # define molecular formula and charge of DNA
    DNA_dict = dict()              # for 1 mol
    DNA_charge = Decimal('0.0')    # for 1 mol
    DNA_molweight = Decimal('0.0') # for 1 mol
    #
    # reactants
    for mid, coeff in reactant_to_coeffs.items():
        m = model.metabolites.get_by_id(mid)
        for key, value in m.elements.items():
            if key not in DNA_dict.keys():
                DNA_dict[key] = Decimal('0.0')
            DNA_dict[key] = DNA_dict[key] + (Decimal(value) * coeff)        # addition
        DNA_charge = DNA_charge + (m.charge * coeff)                        # addition
        DNA_molweight = DNA_molweight + (Decimal(m.formula_weight) * coeff) # addition
    #
    # products
    for mid, coeff in product_to_coeffs.items():
        m = model.metabolites.get_by_id(mid)
        for key, value in m.elements.items():
            if key not in DNA_dict.keys():
                DNA_dict[key] = Decimal('0.0')
            DNA_dict[key] = DNA_dict[key] - (Decimal(value) * coeff)        # subtraction
        DNA_charge = DNA_charge - (m.charge * coeff)                        # subtraction
        DNA_molweight = DNA_molweight - (Decimal(m.formula_weight) * coeff) # subtraction
        
        
    return DNA_dict, DNA_charge, DNA_molweight



def compute_exp_DNA_coeffs(logger, model, MWF, DNA):
    
    
    # define ATP costs for DNA synthesis per monomer (taken from https://doi.org/10.1186/1471-2180-5-39 )
    unwinding_helix = Decimal('1.0')   # mol(ATP) / mol(DNA)
    proofreading = Decimal('0.36')   # mol(ATP) / mol(DNA)
    discontinuous_synthesis = Decimal('0.006')   # mol(ATP) / mol(DNA)
    negative_supercoiling = Decimal('0.005')   # mol(ATP) / mol(DNA)
    methylation = Decimal('0.001')   # mol(ATP) / mol(DNA)
    # real DNA synthesis takes deoxyribonucleotide-triphosphates as precursors, so DNA assembly (modeled as monophosphates) costs an additional 2 mol ATP per mol DNA.
    incorporation = Decimal('2.0')
    atp_cost_DNA = sum([unwinding_helix, proofreading, discontinuous_synthesis, negative_supercoiling, methylation, incorporation])
    
    
    # define the rstring:
    reactant_to_coeffs = {
        'damp_c': DNA['damp'],
        'dtmp_c': DNA['dtmp'],
        'dcmp_c': DNA['dcmp'],
        'dgmp_c': DNA['dgmp'],
        'atp_c': atp_cost_DNA,
        'h2o_c': atp_cost_DNA,
    }
    product_to_coeffs = {
        #'DNA_c': Decimal('1.0'),
        'adp_c': atp_cost_DNA,
        'pi_c': atp_cost_DNA,
        'h_c': atp_cost_DNA,
    }
    
    
    # define molecular formula and charge of DNA_c
    DNA_dict, DNA_charge, DNA_molweight = get_fraction_dict_charge_molweight(model, reactant_to_coeffs, product_to_coeffs)
        
        
    # adjust coefficients to match MWF
    product_to_coeffs['DNA_c'] = Decimal('1.0')
    factor = MWF['DNA'] / DNA_molweight * 1000   # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
    for mid, coeff in reactant_to_coeffs.items():
        reactant_to_coeffs[mid] = reactant_to_coeffs[mid] * factor
    for mid, coeff in product_to_coeffs.items():
        product_to_coeffs[mid] = product_to_coeffs[mid] * factor

        
    return (reactant_to_coeffs, product_to_coeffs)



def compute_exp_RNA_coeffs(logger, model, MWF, RNA):
    
    
    # define ATP costs for RNA synthesis per monomer (taken from https://doi.org/10.1186/1471-2180-5-39 )
    discarding_segments = Decimal('0.38')
    modification = Decimal('0.02')
    # real RNA synthesis takes ribonucleotide-triphosphates as precursors, so RNA assembly (modeled as monophosphates) costs an additional 2 mol ATP per mol RNA.
    incorporation = Decimal('2.0')
    atp_cost_RNA = sum([discarding_segments, modification, incorporation])
    
    
    # define the rstring:
    reactant_to_coeffs = {
        'amp_c': RNA['amp'],
        'ump_c': RNA['ump'],
        'cmp_c': RNA['cmp'],
        'gmp_c': RNA['gmp'],
        'atp_c': atp_cost_RNA,
        'h2o_c': atp_cost_RNA,
    }
    product_to_coeffs = {
        #'RNA_c': Decimal('1.0'),
        'adp_c': atp_cost_RNA,
        'pi_c': atp_cost_RNA,
        'h_c': atp_cost_RNA,
    }
    
    
    # define molecular formula and charge of RNA_c
    RNA_dict, RNA_charge, RNA_molweight = get_fraction_dict_charge_molweight(model, reactant_to_coeffs, product_to_coeffs)
        
    
    # adjust coefficients to match MWF
    product_to_coeffs['RNA_c'] = Decimal('1.0')
    factor = MWF['RNA'] / RNA_molweight * 1000   # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
    for mid, coeff in reactant_to_coeffs.items():
        reactant_to_coeffs[mid] = reactant_to_coeffs[mid] * factor
    for mid, coeff in product_to_coeffs.items():
        product_to_coeffs[mid] = product_to_coeffs[mid] * factor

        
    return (reactant_to_coeffs, product_to_coeffs)



def compute_exp_PROTS_coeffs(logger, model, MWF, PROTS):
    
    
    # define ATP costs for PROTS synthesis (taken from https://doi.org/10.1186/1471-2180-5-39 )
    activation_and_incorporation = Decimal('4.0')
    mRNA_synthesis = Decimal('0.2')
    proofreading = Decimal('0.1')
    assembly_and_modification = Decimal('0.006')
    atp_cost_PROTS = sum([activation_and_incorporation, mRNA_synthesis, proofreading, assembly_and_modification])
    
    
    # define the rstring
    aas = ['ala__L', 'arg__L', 'asn__L', 'asp__L', 'cys__L', 'gln__L', 'glu__L', 'gly', 'his__L', 'ile__L', 'leu__L', 'lys__L', 'met__L', 'phe__L', 'pro__L', 'ser__L', 'thr__L', 'trp__L', 'tyr__L', 'val__L']
    reactant_to_coeffs = {}
    for aa in aas: reactant_to_coeffs[f"{aa}_c"] = PROTS[aa]
    reactant_to_coeffs['atp_c'] = atp_cost_PROTS
    reactant_to_coeffs['h2o_c'] = atp_cost_PROTS
    product_to_coeffs = {
        #'PROTS_c': Decimal('1.0'),
        'adp_c': atp_cost_PROTS,
        'pi_c': atp_cost_PROTS,
        'h_c': atp_cost_PROTS,
    }


    # define molecular formula and charge of PROTS_c
    PROTS_dict, PROTS_charge, PROTS_molweight = get_fraction_dict_charge_molweight(model, reactant_to_coeffs, product_to_coeffs)
        
    
    # adjust coefficients to match MWF
    product_to_coeffs['PROTS_c'] = Decimal('1.0')
    factor = MWF['PROTS'] / PROTS_molweight * 1000   # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
    for mid, coeff in reactant_to_coeffs.items():
        reactant_to_coeffs[mid] = reactant_to_coeffs[mid] * factor
    for mid, coeff in product_to_coeffs.items():
        product_to_coeffs[mid] = product_to_coeffs[mid] * factor

        
    return (reactant_to_coeffs, product_to_coeffs)



def compute_exp_LIPIDS_coeffs(logger, model, MWF, LIPIDS_PL, LIPIDS_FA):
    
    
    # produce mean fatty-acid assembly reaction rstring:
    reactant_to_coeffs = {}
    product_to_coeffs = {}
    for puremid, coeff in LIPIDS_FA.items():
        reactant_to_coeffs[f"{puremid}_c"] = coeff
    product_to_coeffs[f"meanfa_c"] = 1
    rstring = rstring_builder(reactant_to_coeffs, product_to_coeffs)
    
    
    # add mean fatty-acid assembly reaction
    r = cobra.Reaction('MEANFA')
    model.add_reactions([r])
    r = model.reactions.get_by_id('MEANFA')
    r.name = "Mean fatty acid assembl reaction"
    r.build_reaction_from_string(rstring)
    r.bounds = (0, 1000)
    r.gene_reaction_rule = 'spontaneous'   
    r.update_genes_from_gpr()
    
    
    # determine 'L' formula and charge (charge should be -1 like every fatty acid)
    L_dict = dict()              # for 1 mol
    L_charge = Decimal('0.0')    # for 1 mol
    for puremid, coeff in LIPIDS_FA.items():
        m = model.metabolites.get_by_id(f"{puremid}_c")
        for key, value in m.elements.items():
            if key not in L_dict.keys():
                L_dict[key] = Decimal('0.0')
            L_dict[key] = L_dict[key] + (value * coeff)   # addition
        L_charge = L_charge + (m.charge * coeff)          # addition
    if model.metabolites.get_by_id(f"meanfa_c").charge != L_charge:
        logger.error("Charge of 'meanfa_c' should be -1. Please contact the developer.")
    
    
    # update formula of every metabolite having 'L' element
    for m in model.metabolites:
        m_dict = dict()
        to_update = False
        for key, value in m.elements.items():                
            if key != 'L':
                if key not in m_dict.keys():
                    m_dict[key] = Decimal('0.0')
                m_dict[key] = m_dict[key] + Decimal(value)
            else:
                to_update = True
                for key_L, value_L in L_dict.items():
                    if key_L not in m_dict.keys():
                        m_dict[key_L] = Decimal('0.0')
                    m_dict[key_L] = m_dict[key_L] + (value_L * Decimal(value))
        if to_update:
            m.formula = ''.join([f'{key}{float(value)}' for key, value in m_dict.items()])
            
            
    # define ATP costs for LIPIDS synthesis
    atp_cost_LIPIDS = Decimal('0.0')
    
    
    # define the rstring:
    reactant_to_coeffs = dict()
    for puremid, coeff in LIPIDS_PL.items():
        reactant_to_coeffs[f"{puremid}_c"] = coeff
    reactant_to_coeffs['atp_c'] = atp_cost_LIPIDS
    reactant_to_coeffs['h2o_c'] = atp_cost_LIPIDS
    product_to_coeffs = {
        #'LIPIDS_c': Decimal('1.0'),
        'adp_c': atp_cost_LIPIDS,
        'pi_c': atp_cost_LIPIDS,
        'h_c': atp_cost_LIPIDS,
    }
    
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # avoids warnings like "UserWarning: 9.823 is not an integer (in formula C9.823H5.5789999999999935N3.6769999999999996O3.628P1.0)"
    
        # define molecular formula and charge of LIPIDS
        LIPIDS_dict, LIPIDS_charge, LIPIDS_molweight = get_fraction_dict_charge_molweight(model, reactant_to_coeffs, product_to_coeffs)
     
        
    # adjust coefficients to match MWF
    product_to_coeffs['LIPIDS_c'] = Decimal('1.0')
    factor = MWF['LIPIDS'] / LIPIDS_molweight * 1000   # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
    for mid, coeff in reactant_to_coeffs.items():
        reactant_to_coeffs[mid] = reactant_to_coeffs[mid] * factor
    for mid, coeff in product_to_coeffs.items():
        product_to_coeffs[mid] = product_to_coeffs[mid] * factor
    
    
    return (reactant_to_coeffs, product_to_coeffs)
    


def compute_exp_WTA_coeffs(logger, model, biomass_dict, MWF, dbexp):
    product_to_coeffs = dict()  # empty dict (no product)
    
    
    # get WTA species in biomass: 
    available_WTA = set()
    for mid in biomass_dict['WTA']: 
        if mid in [m.id for m in model.reactions.get_by_id('Biomass').reactants]:
            available_WTA.add(mid)
            
            
    # if no pathway was completed for LTA, but a fraction was given in MWF:
    if available_WTA == set() and 'WTA' in MWF.keys():
        logger.error(f"Strain seems unable to synthetize WTA, but a fraction was indicated in 'MWF'.")
        return 1
            
    
    # if no grams were specified in MWF:
    if available_WTA != set() and 'WTA' not in MWF.keys():
        logger.info(f"This strain should be able to synthetize WTA ({available_WTA}), but no fraction was indicated in 'MWF': they will be treated as cofactors (coefficient {get_uni_biom_coeff()}).")
        reactant_to_coeffs = dict()
        for mid in available_WTA:
            reactant_to_coeffs[mid] = Decimal(get_uni_biom_coeff())
        return (reactant_to_coeffs, product_to_coeffs)
    
    
    # equal grams are assumed for every detected species of WTA
    reactant_to_coeffs = dict()
    for mid in available_WTA:
        m = model.metabolites.get_by_id(mid) 
        # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
        reactant_to_coeffs[mid] = MWF['WTA'] / len(available_WTA) / Decimal(m.formula_weight) * 1000

        
    return (reactant_to_coeffs, product_to_coeffs)



def compute_exp_LTA_coeffs(logger, model, biomass_dict, MWF, dbexp):
    product_to_coeffs = dict()  # empty dict (no product)
    
    
    # get LTA species in biomass: 
    available_LTA = set()
    for mid in biomass_dict['LTA']: 
        if mid in [m.id for m in model.reactions.get_by_id('Biomass').reactants]:
            available_LTA.add(mid)
            
            
    # if no pathway was completed for LTA, but a fraction was given in MWF:
    if available_LTA == set() and 'LTA' in MWF.keys():
        logger.error(f"Strain seems unable to synthetize LTA, but a fraction was indicated in 'MWF'.")
        return 1
            
    
    # if no grams were specified in MWF:
    if available_LTA != set() and 'LTA' not in MWF.keys():
        logger.info(f"This strain should be able to synthetize LTA ({available_LTA}), but no fraction was indicated in 'MWF': they will be treated as cofactors (coefficient {get_uni_biom_coeff()}).")
        reactant_to_coeffs = dict()
        for mid in available_LTA:
            reactant_to_coeffs[mid] = Decimal(get_uni_biom_coeff())
        return (reactant_to_coeffs, product_to_coeffs)
    
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # avoids warnings like "UserWarning: 9.823 is not an integer (in formula C9.823H5.5789999999999935N3.6769999999999996O3.628P1.0)"
    

        # equal grams are assumed for every detected species of LTA
        reactant_to_coeffs = dict()
        for mid in available_LTA:
            m = model.metabolites.get_by_id(mid)
            # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
            reactant_to_coeffs[mid] = MWF['LTA'] / len(available_LTA) / Decimal(m.formula_weight) * 1000

        
    return (reactant_to_coeffs, product_to_coeffs)



def compute_exp_PEPTIDO_coeffs(logger, model, biomass_dict, MWF, dbexp):
    product_to_coeffs = dict()  # empty dict (no product)
    
    
    # get WTA species in biomass: 
    available_PEPTIDO = set()
    for mid in biomass_dict['PEPTIDO']: 
        if mid in [m.id for m in model.reactions.get_by_id('Biomass').reactants]:
            available_PEPTIDO.add(mid)
            
            
    # if no pathway was completed for LTA, but a fraction was given in MWF:
    if available_PEPTIDO == set() and 'PEPTIDO' in MWF.keys():
        logger.error(f"Strain seems unable to synthetize PEPTIDO, but a fraction was indicated in 'MWF'.")
        return 1
            
    
    # if no grams were specified in MWF:
    if available_PEPTIDO != set() and 'PEPTIDO' not in MWF.keys():
        logger.info(f"This strain should be able to synthetize PEPTIDO ({available_PEPTIDO}), but no fraction was indicated in 'MWF': they will be treated as cofactors (coefficient {get_uni_biom_coeff()}).")
        reactant_to_coeffs = dict()
        for mid in available_PEPTIDO:
            reactant_to_coeffs[mid] = Decimal(get_uni_biom_coeff())
        return (reactant_to_coeffs, product_to_coeffs)
    
    
    # equal grams are assumed for every detected species of WTA
    reactant_to_coeffs = dict()
    for mid in available_PEPTIDO:
        m = model.metabolites.get_by_id(mid) 
        # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
        reactant_to_coeffs[mid] = MWF['PEPTIDO'] / len(available_PEPTIDO) / Decimal(m.formula_weight) * 1000

        
    return (reactant_to_coeffs, product_to_coeffs)



def compute_exp_EPS_coeffs(logger, model, biomass_dict, MWF, dbexp):
    product_to_coeffs = dict()  # empty dict (no product)
    
    
    # get WTA species in biomass: 
    available_EPS = set()
    for mid in biomass_dict['EPS']: 
        if mid in [m.id for m in model.reactions.get_by_id('Biomass').reactants]:
            available_EPS.add(mid)
            
            
    # if no pathway was completed for LTA, but a fraction was given in MWF:
    if available_EPS == set() and 'EPS' in MWF.keys():
        logger.error(f"Strain seems unable to synthetize EPS, but a fraction was indicated in 'MWF'.")
        return 1
            
    
    # if no grams were specified in MWF:
    if available_EPS != set() and 'EPS' not in MWF.keys():
        logger.info(f"This strain should be able to synthetize EPS ({available_EPS}), but no fraction was indicated in 'MWF': they will be treated as cofactors (coefficient {get_uni_biom_coeff()}).")
        reactant_to_coeffs = dict()
        for mid in available_EPS:
            reactant_to_coeffs[mid] = Decimal(get_uni_biom_coeff())
        return (reactant_to_coeffs, product_to_coeffs)
    
    
    # equal grams are assumed for every detected species of WTA
    reactant_to_coeffs = dict()
    for mid in available_EPS:
        m = model.metabolites.get_by_id(mid) 
        # [g/gDW] / [g/mol] * 1000 = [mmol/gDW]
        reactant_to_coeffs[mid] = MWF['EPS'] / len(available_EPS) / Decimal(m.formula_weight) * 1000

        
    return (reactant_to_coeffs, product_to_coeffs)

