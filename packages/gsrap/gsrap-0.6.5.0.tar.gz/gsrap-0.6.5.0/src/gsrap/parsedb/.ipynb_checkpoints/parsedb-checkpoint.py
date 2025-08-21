import os
import pickle


import cobra
import gempipe


from ..commons import force_id_on_sbml
from ..commons import log_metrics
from ..commons import log_unbalances
from ..commons import get_databases
from ..commons import introduce_universal_biomass
from ..commons import write_excel_model
from ..commons import show_contributions
from ..commons import adjust_biomass_precursors
from ..commons import count_undrawn_rids
from ..commons import format_expansion

from .introduce import introduce_metabolites
from .introduce import introduce_reactions
from .introduce import introduce_transporters
from .introduce import introduce_sinks_demands

from .annotation import translate_annotate_genes
from .annotation import set_up_groups

from .completeness import check_completeness

from ..runsims.simplegrowth import grow_on_media
from ..runsims.precursors import precursors_on_media
from ..runsims.biosynth import biosynthesis_on_media




def main(args, logger):
    
    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # check compatibility of input parameters
    if args.progress==False and args.module==True: 
        logger.error(f"You cannot ask --module without --progress (see --help).")
        return 1
    if args.progress==False and args.focus!='-':
        logger.error(f"You cannot ask --focus without --progress (see --help).")
        return 1
    
    
    # check 'goodbefore' and 'onlyauthor' params
    if args.goodbefore == '-' and args.onlyauthor != '-':
        logger.error(f"--onlyauthor must be used in conjunction with --goodbefore.")
        return 1
    if   args.goodbefore == '-': args.goodbefore = [None, None, None]
    elif len(args.goodbefore.split('-')) != 3: 
        logger.error(f"Invalid syntax detected for --goodbefore.")
        return 1
    else:
        args.goodbefore = args.goodbefore.split('-')
        if args.goodbefore[0] == 'None': args.goodbefore[0] = None
        if args.goodbefore[1] == 'None': args.goodbefore[1] = None
        if args.goodbefore[2] == 'None': args.goodbefore[2] = None
    if args.onlyauthor == '-': args.onlyauthor = None
    
    
    # format the --eggnog param
    args.eggnog = format_expansion(logger, args.eggnog)
    
    
    # check and extract the required 'gsrap.maps' file
    if os.path.exists(f'{args.inmaps}') == False:
        logger.error(f"File 'gsrap.maps' not found at {args.inmaps}.")
        return 1
    try: 
        with open(f'{args.inmaps}', 'rb') as f:
            inmaps = pickle.load(f)  
    except: 
        logger.error(f"Provided file {args.inmaps} has an incorrect format.")
        return 1
    idcollection_dict = inmaps['idcollection_dict']
    summary_dict = inmaps['summary_dict']
    keggc_to_bigg = inmaps['keggc_to_bigg']
    keggr_to_bigg = inmaps['keggr_to_bigg']
    
    
    # get dbuni and dbexp:
    logger.info("Downloading gsrap database...")
    response = get_databases(logger)
    if type(response)==int: return 1
    else: dbuni, dbexp, lastmap = response
    

    # show simple statistics of contributions
    show_contributions(logger, dbuni)
                                    
        
    
    ###### RECONSTRUCTION
    # create the model
    universe = cobra.Model('newuni')   
    logger.info("Parsing gsrap database...")
    
    # introduce M / R / T
    universe = introduce_metabolites(logger, dbuni, universe, idcollection_dict, keggc_to_bigg, args.goodbefore[0], args.onlyauthor)
    if type(universe)==int: return 1
    universe = introduce_reactions(logger, dbuni, universe, idcollection_dict, keggr_to_bigg, args.goodbefore[1], args.onlyauthor)
    if type(universe)==int: return 1
    universe = introduce_transporters(logger, dbuni, universe, idcollection_dict, keggr_to_bigg, args.goodbefore[2], args.onlyauthor)
    if type(universe)==int: return 1

    # introduce sinks / demands (exchanges where included during T)
    universe = introduce_sinks_demands(logger, universe)
    if type(universe)==int: return 1

    # introducce biomass
    universe = introduce_universal_biomass(logger, dbexp, universe)
    if type(universe)==int: return 1



    ###### ANNOTATION
    # translate Gs to symbols and annotate them (EC, COG, GO, ...)
    universe = translate_annotate_genes(logger, universe, idcollection_dict)
    if type(universe)==int: return 1

    # introduce collectionas (groups of Rs as maps/modules)
    universe = set_up_groups(logger, universe, idcollection_dict)
    if type(universe)==int: return 1


    
    # # # # #   PARSING ENDS HERE   # # # # #
    log_metrics(logger, universe)
    log_unbalances(logger, universe)

    
    
    ###### CHECKS
    # check universe completness
    setattr(args, 'zeroes', True)  # old parameter, forced to True from v0.6.1
    response = check_completeness(logger, universe, args.progress, args.module, args.focus, args.eggnog, args.zeroes, idcollection_dict, summary_dict)
    if response==1: return 1

    # check growth on minmal media
    df_G = grow_on_media(logger, universe, dbexp, args.media, '-', True)
    if type(df_G)==int: return 1
    
    # check blocked biomass precursors
    cond_col_dict = adjust_biomass_precursors(logger, universe, universe, 1.0)
    df_E = precursors_on_media(logger, universe, universe, dbexp, args.media, cond_col_dict, args.precursors)
    if type(df_E)==int: return 1

    # check blocked metabolites / dead-ends
    df_S = biosynthesis_on_media(logger, universe, dbexp, args.media, args.biosynth)
    if type(df_S)==int: return 1


    
    ###### POLISHING
    # reset growth environment befor saving the model
    gempipe.reset_growth_env(universe)



    # output the universe
    logger.info("Writing universal model...")
    cobra.io.save_json_model(universe, f'{args.outdir}/universe.json')
    logger.info(f"'{args.outdir}/universe.json' created!")
    cobra.io.write_sbml_model(universe, f'{args.outdir}/universe.xml')   # groups are saved only to SBML 
    logger.info(f"'{args.outdir}/universe.xml' created!")
    force_id_on_sbml(f'{args.outdir}/universe.xml', 'universe')   # force introduction of the 'id=""' field
    sheets_dict = write_excel_model(universe, f'{args.outdir}/universe.parsedb.xlsx', df_E, None, None, df_S)  
    logger.info(f"'{args.outdir}/universe.parsedb.xlsx' created!")


    
    # check if universal escher map os updated:
    count_undrawn_rids(logger, universe, lastmap)
    
    
    return 0