import warnings
from decimal import Decimal


import numpy as np
import pandas as pnd
import cobra


from .coeffs import get_uni_biom_coeff
from .coeffs import check_exp_biomass_data
from .coeffs import compute_exp_DNA_coeffs
from .coeffs import compute_exp_RNA_coeffs
from .coeffs import compute_exp_PROTS_coeffs
from .coeffs import compute_exp_LIPIDS_coeffs
from .coeffs import compute_exp_WTA_coeffs
from .coeffs import compute_exp_LTA_coeffs
from .coeffs import compute_exp_PEPTIDO_coeffs
from .coeffs import compute_exp_EPS_coeffs



def get_biomass_dict(logger, universe, dbexp):
    
    
    # check if precursors are modeled in the universe:
    universal_mids = [m.id for m in universe.metabolites]
    fraction_to_precursors = dict()
    for fraction in ['DNA', 'RNA', 'PROTS', 'LIPIDS_PL', 'LIPIDS_FA']:
        fraction_db = dbexp[fraction]
        fraction_db = fraction_db.iloc[4:] # ignore ['description', 'doi', 'author', 'units']) 
        precursors = [f"{i}_c" for i in fraction_db.index.dropna()]
        for i in precursors: 
            if i not in universal_mids:
                logger.error(f"Metabolite '{i}', indicated in 'DNA', is not present in universe.")
                return 1
        fraction_to_precursors[fraction] = precursors
    
    
    biomass_dict = {
        
        
        # MWF: macromolecular weight fractions:
        'DNA': fraction_to_precursors['DNA'],
        'RNA': fraction_to_precursors['RNA'],
        'PROTS': fraction_to_precursors['PROTS'],
        'LIPIDS_PL': fraction_to_precursors['LIPIDS_PL'],
        'LIPIDS_FA': fraction_to_precursors['LIPIDS_FA'],
        'WTA': [
            'WTAgg40r_20n_20a_P_c', # teichoic acids
            'WTArg40r_20g_20a_P_c', # teichoic acids
            'WTAg40g_20g_20a_P_c', # teichoic acids
            'WTAt4_20a_P_c', # teoichoic acid
        ],
        'LTA': [
            'LTAgg40g_20n_20a_c', # lipoteichoic acids
            'LTAga40g_20t_20a_c', # lipoteichoic acids 
            'LTAt4_20a_c', # lipoteichoic acid
        ],
        'PEPTIDO': [
            'peptidoSTA_c', # peptidoglycan (dependant on 'udcpdp_c')
            'peptidoSTR_c',
            'peptidoDAP_c',
        ],
        'EPS': [
            'epsLAB_c', # LAB eps            
        ],
        # glycogen
        # starch
        'PHA': [
            'phb_c', # PHA / PHB
        ],
        
        
        # Cofactors:
        # Note: universal ('cofs_uni_Xavier2017') and conditional ('cofs_cond_Xavier2017') cofactors have been defined in Xavier2017 .
        # Here presented in the same order of Xavier2017.
        # Cofactors not mentioned in Xavier2017 ('cofactors_add') are reported below.
        # Xavier2017: 10.1016/j.ymben.2016.12.002.
        'cofs_uni_Xavier2017': [
            'nad_c',    # B3: Nicotinamide -adenine dinucleotide phosphate
            'nadp_c',   # B3: Nicotinamide -adenine dinucleotide phosphate
            'coa_c',    # B5: Coenzyme A  (dependant on 'pnto__R_c')
            'fad_c',    # B2: Flavin adenine dinucleotide
            'fmn_c',    # B2: Flavin mononucleotide
            'ribflv_c', # B2: ribovlavin. Non-active form acording to Xavier2017 but anyway included.
            #'f4200_c', # B2: included by Xavier2017 in 'universal' but the description seems conditional.
            'thf_c',    # B9: tetrahydrofolate 
            '10fthf_c', # B9: 10-Formyltetrahydrofolate
            '5mthf_c',  # B9: 5-Methyltetrahydrofolate
            'thmpp_c',  # B1: Thiamine diphosphate
            'pydx5p_c', # B6: pyridoxal 5-phosphate
            'amet_c',   # SAM: S-adenosyl-methionine
        ],
        'cofs_cond_Xavier2017': [
            #'f4200_c', # coenzyme f420 (electron transfer in methanogens, actinobacteria , and others)
            'ptrc_c',   # Putrescine
            'spmd_c',   # Sperimidine
            'pheme_c',  # protoheme
            'mql8_c',   # menaquinol / manaquinone (mqn8_c)
            'q8h2_c',   # ubiquinol / ubiquinone (q8_c)
            # Methionaquinone
            'btn_c',    # B7: biotin
            #'ACP_c',    # Acyl-carrier protein (removed as it contains the 'X' atom, causing error in Memote)
            'adocbl_c', # B12: Adenosylcobalamin
            # Lipoate
            'uacgam_c'  # uridine diphosphate N-Acetylglucosamine (UDP-GlcNAc)
        ],
        ##### ADDED ##### (conditionals not included or lumped in Xavier2017)
        'cofs_suppl': [
            'hemeO_c',  # heme-O
            'sheme_c',  # siroheme
            'moco_c',   # molybdenum cofactor
            'phllqol_c',# phylloquinol / phylloquinone (phllqne_c)
            'gthrd_c',  # glutathione (reduced)
            'br_c',     # bacterioruberin
            # kdo_lipid_A
        ],
    }
    
    
    return biomass_dict



def get_precursors_to_pathway():
    
    
    precursors_to_pathway = {  # listing alternative biosynthetic pathways
        
        'pheme_c': ['M00868', 'M00121', 'M00926'],   # protoheme (heme)
        'mql8_c': ['M00116', 'M00930', 'M00931'],  # menaquinol
        'q8h2_c': ['M00117', 'M00989', 'M00128'],  # ubiquinol
        'adocbl_c': ['M00122'],   # vitamin B12 (cobolamin)
        'hemeO_c': ['gr_HemeO'],  # heme-O
        'sheme_c': ['M00846'],   # siroheme
        'moco_c': ['M00880'],  # molybdenum cofactor
        'phllqol_c': ['M00932'],  # phylloquinol
        'gthrd_c': ['M00118'],  # Reduced glutathione
        'br_c': ['gr_br'],  # bacterioruberin
        'WTAg40g_20g_20a_P_c':  ['gr_WTA1'], # teichoic acids
        'WTArg40r_20g_20a_P_c': ['gr_WTA2'], # teichoic acids
        'WTAgg40r_20n_20a_P_c': ['gr_WTA3'], # teichoic acids
        'WTAt4_20a_P_c': ['gr_WTA4'], # teoichoic acid
        'LTAgg40g_20n_20a_c':  ['gr_LTA1'], # lipoteichoic acids
        'LTAga40g_20t_20a_c':  ['gr_LTA2'], # lipoteichoic acids 
        'LTAt4_20a_c': ['gr_LTA3'],  # lipoteichoic acids 
        'peptidoSTA_c': ['gr_ptdSTA'], # peptidoglycan (dependant on 'udcpdp_c')
        'peptidoSTR_c': ['gr_ptdSTR'],
        'peptidoDAP_c': ['gr_ptdDAP'],
        'epsLAB_c': ['gr_epsLAB'],  # EPS of lactic acid bacteria
        'phb_c': ['gr_PHA1'],  # PHA / PHB    
    }
    
    
    return precursors_to_pathway



def introduce_universal_biomass(logger, dbexp, universe): 
    
    
    biomass_dict = get_biomass_dict(logger, universe, dbexp)
    
    
    # MWF: macromolecular weight fractions:
    rstring =              f'{get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["RNA"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["DNA"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["PROTS"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["LIPIDS_PL"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["LIPIDS_FA"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["WTA"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["LTA"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["PEPTIDO"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["EPS"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["PHA"])}'
    
    
    # Cofactors:
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["cofs_uni_Xavier2017"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["cofs_cond_Xavier2017"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} {(" + " + str(get_uni_biom_coeff()) + " ").join(biomass_dict["cofs_suppl"])}'
    rstring = rstring + f' + {get_uni_biom_coeff()} atp_c + {get_uni_biom_coeff()} h2o_c --> {get_uni_biom_coeff()} adp_c + {get_uni_biom_coeff()} h_c + {get_uni_biom_coeff()} pi_c'
    
    
    r = cobra.Reaction('Biomass')
    universe.add_reactions([r])
    r = universe.reactions.get_by_id('Biomass')
    r.name = 'Biomass assembly reaction'
    r.build_reaction_from_string(rstring)
    
    
    # set as objective:
    universe.objective = 'Biomass'
    
    
    return universe



def adjust_biomass_precursors(logger, model, universe, conditional_threshold):
    

    precursor_to_pathway = get_precursors_to_pathway()
    modeled_rids = [r.id for r in model.reactions]
    
    
    cnt_removed = 0
    cond_col_dict = {}  # dictionary of variable biomass precursors
    for precursor, pathways in precursor_to_pathway.items(): 
        
        pathway_to_absence = {}
        pathway_to_compstring = {}   # completeness string
        for pathway in pathways:   # more pathways might lead to the same precursor
            # initialize counters:
            cnt_members_tot = 0
            cnt_members_present = 0

            
            if pathway not in [gr.id for gr in universe.groups]:
                continue   # still missing from the universe
                
            for member in universe.groups.get_by_id(pathway).members:
                cnt_members_tot += 1    
                if member.id in modeled_rids:
                    cnt_members_present += 1
            # populate dicts:
            pathway_to_absence[pathway] = (cnt_members_present / cnt_members_tot) < conditional_threshold
            pathway_to_compstring[pathway] = f'{pathway}: {cnt_members_present}/{cnt_members_tot}'
            

        cond_col_dict[precursor] = '; '.join(list(pathway_to_compstring.values()))
        if all(list(pathway_to_absence.values())):
            cnt_removed += 1
            logger.debug(f"Biomass precursor '{precursor}' seems not required ({cond_col_dict[precursor]}).")
            # add metabolites to the right side (they will disappear if the balance if 0)
            model.reactions.Biomass.add_metabolites({precursor: get_uni_biom_coeff()})

       
    if model.id != universe.id:   # avoid logging when testing blocked biomass precusors of the universe.
        logger.info(f"Removed {cnt_removed} conditional biomass precursors.")
        
        
    return cond_col_dict



def compute_biomass_norm(logger, model, biomass): 
    
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # avoids warnings like "UserWarning: 9.823 is not an integer (in formula C9.823H5.5789999999999935N3.6769999999999996O3.628P1.0)"
    
    
        norm = Decimal(0.0)
        for m, coeff in model.reactions.get_by_id('Biomass').metabolites.items():
            if coeff < 0.0:   # reactant
                if m.id not in ["atp_c", "h2o_c"]:
                    # '/1000' as they are milli-model coefficients:
                    norm = norm + Decimal(abs(coeff)) / 1000 * Decimal(m.formula_weight) 
        logger.info(f"Biomass adjusted using '{biomass}' data: {str(round(norm, 16))} gDW.")



def adjust_biomass_coefficients(logger, model, universe, dbexp, biomass):
    # Strategy: the default coefficients are equal to 'get_uni_biom_coeff()', which is  a really samm number, negligible.
    # Coefficients are adjusted only for precursors comprised by MWF, all the others are left with default coefficients.
    # Therefore, if the final biomass is not sufficiently close to 1.0, just lower the 'get_uni_biom_coeff()', 
    # or lower the number of precursors left with default coefficient. 
    
    
    if biomass == '-':
        logger.info(f"No biomass data provided: using minimal coefficients ({get_uni_biom_coeff()}).")
        return 0
    
    
    # check biomass data
    response = check_exp_biomass_data(logger, dbexp, biomass)
    if type(response)==int: return 1
    else: MWF, DNA, RNA, PROTS, LIPIDS_PL, LIPIDS_FA = response
    
    
    # compute coefficient for 'Biomass' reaction:
    biomass_dict = get_biomass_dict(logger, universe, dbexp)
    reacs_prods_coeffs = dict()
    
    
    # the reaction 'MEANFA' will replace 'sn_meanfa_c' to produce 'meanfa_c'.
    model.remove_reactions([model.reactions.get_by_id("sn_meanfa_c")])
    logger.debug(f"Removed 'sn_meanfa_c': will be replaced by 'MEANFA'.")
    
    
    # DNA
    response = compute_exp_DNA_coeffs(logger, model, MWF, DNA)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['DNA'] = response
    # RNA
    response = compute_exp_RNA_coeffs(logger, model, MWF, RNA)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['RNA'] = response
    # PROTS
    response = compute_exp_PROTS_coeffs(logger, model, MWF, PROTS)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['PROTS'] = response
    # LIPIDS
    response = compute_exp_LIPIDS_coeffs(logger, model, MWF, LIPIDS_PL, LIPIDS_FA)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['LIPIDS'] = response 
    # WTA
    response = compute_exp_WTA_coeffs(logger, model, biomass_dict, MWF, dbexp)    
    if type(response)==int: return 1
    else: reacs_prods_coeffs['WTA'] = response
    # LTA
    response = compute_exp_LTA_coeffs(logger, model, biomass_dict, MWF, dbexp)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['LTA'] = response
    # PEPTIDO
    response = compute_exp_PEPTIDO_coeffs(logger, model, biomass_dict, MWF, dbexp)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['PEPTIDO'] = response
    # EPS
    response = compute_exp_EPS_coeffs(logger, model, biomass_dict, MWF, dbexp)
    if type(response)==int: return 1
    else: reacs_prods_coeffs['EPS'] = response  
    
    
    # merge dicts of reactants and products: 
    reactant_to_coeffs = dict()
    product_to_coeffs = dict()
    for i in reacs_prods_coeffs.values():
        reacs, prods = i[0], i[1]
        for key, coeff in reacs.items():
            if key not in reactant_to_coeffs.keys():
                reactant_to_coeffs[key] = Decimal('0.0')
            reactant_to_coeffs[key] = reactant_to_coeffs[key] + coeff
        for key, coeff in prods.items():
            if key in ['DNA_c', 'RNA_c', 'PROTS_c', 'LIPIDS_c']:
                continue
            if key not in product_to_coeffs.keys():
                product_to_coeffs[key] = Decimal('0.0')
            product_to_coeffs[key] = product_to_coeffs[key] + coeff
    
    
    # update biomass coefficients
    for mid in [m.id for m in model.reactions.get_by_id('Biomass').reactants]:
        if mid in reactant_to_coeffs.keys(): 
            model.reactions.Biomass.add_metabolites({mid: get_uni_biom_coeff()})
            model.reactions.Biomass.add_metabolites({mid: -float(reactant_to_coeffs[mid])})
    for mid in [m.id for m in model.reactions.get_by_id('Biomass').products]:
        if mid in product_to_coeffs.keys(): 
            model.reactions.Biomass.add_metabolites({mid: -get_uni_biom_coeff()})
            model.reactions.Biomass.add_metabolites({mid: float(product_to_coeffs[mid])})
            
            
    # remove unsed biomass precursors:
    biomass_dict = get_biomass_dict(logger, universe, dbexp)
    # remove all fatty acids:
    for mid in biomass_dict["LIPIDS_FA"]:
        model.reactions.Biomass.add_metabolites({mid: get_uni_biom_coeff()})
    # remove unused phospholipids:
    for mid in biomass_dict["LIPIDS_PL"]:
        if mid not in reacs_prods_coeffs['LIPIDS'][0].keys():
            model.reactions.Biomass.add_metabolites({mid: get_uni_biom_coeff()})
            
            
    # check normalization to 1.0 gDW
    compute_biomass_norm(logger, model, biomass)
            
    
    return 0



def get_biomass_df_structure(logger, df, model, universe, dbexp, cond_col_dict):
    
    
    # get strain-specific biomass precursors / coeffs to gap-fill: 
    biomass_mids_to_coeff = dict()
    for m, coeff in model.reactions.Biomass.metabolites.items():
        if coeff < 0:   # reactants
            biomass_mids_to_coeff[m.id] = abs(coeff)
            
            
    # get all universal biomass precursors: 
    biomass_dict = get_biomass_dict(logger, universe, dbexp)
    biomass_mids = []
    for key, values in biomass_dict.items():
        for i in values:
            biomass_mids.append(i)
            
    
    # preload ctegory of each precursor
    precursor_to_catg = dict()
    for catg, mids in biomass_dict.items(): 
        for mid in mids: 
            precursor_to_catg[mid] = catg
    precursor_to_catg['atp_c'] = '/'
    
    
    
    # prepare sheet for excel output
    df['name'] = None
    df['category'] = None
    df['cond'] = None
    df['coeff'] = None
    universal_precs = ['atp_c'] + [m.id for m in universe.reactions.Biomass.reactants if m.id not in ['atp_c', 'h2o_c']]
    for mid in universal_precs:
        
        if mid in biomass_mids and not mid in biomass_mids_to_coeff.keys():
            if mid in biomass_dict['LIPIDS_PL'] or mid in biomass_dict['LIPIDS_FA']:
                continue   # unobserved experimentally, not true conditional 
        
        df.loc[mid, 'name'] = universe.metabolites.get_by_id(mid).name
        
        df.loc[mid, 'category'] = precursor_to_catg[mid]
        
        # set 'cond' column:
        if mid in cond_col_dict.keys():
            df.loc[mid, 'cond'] = f'{cond_col_dict[mid]}'
        else:
            df.loc[mid, 'cond'] = '/'
            
        # set 'coeff' column:
        if mid not in [m.id for m in model.reactions.Biomass.reactants]:  
                df.loc[mid, 'coeff'] = 'removed'
        else:
            df.loc[mid, 'coeff'] = biomass_mids_to_coeff[mid]
            
            
    return df


