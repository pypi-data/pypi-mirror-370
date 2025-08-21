import argparse
import sys
import traceback
import importlib.metadata
from datetime import datetime


import cobra


from .commons import get_logger
from .commons import set_usual_formatter
from .commons import set_header_trailer_formatter

from .getmaps import getmaps_command
from .parsedb import parsedb_command
from .mkmodel import mkmodel_command
from .runsims import runsims_command



cobra_config = cobra.Configuration()
solver_name = str(cobra_config.solver.log).split(' ')[1]
solver_name = solver_name.replace("optlang.", '')
solver_name = solver_name.replace("_interface", '')



def main():
    
    
    # define the header of main- and sub-commands. 
    header = f'gsrap v{importlib.metadata.metadata("gsrap")["Version"]},\ndeveloped by Gioele Lazzari (gioele.lazzari@univr.it).'
    
    
    # create the command line arguments:
    parser = argparse.ArgumentParser(description=header, add_help=False)
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('gsrap')['Version']}", help="Show version number and exit.")
    subparsers = parser.add_subparsers(title='gsrap subcommands', dest='subcommand', help='', required=True)
    
    
    # create the 3 subparsers:
    getmaps_parser = subparsers.add_parser('getmaps', description=header, help="Create 'gsrap.maps' by retrieving metabolic information from specialized resources.", formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    parsedb_parser = subparsers.add_parser('parsedb', description=header, help="Parse our online database to create the universe GSMM. Requires 'gsrap.maps'.", formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    mkmodel_parser = subparsers.add_parser('mkmodel', description=header, help='Reconstruct a strain-specific GSMM starting from the universe and a functional annotation.', formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    runsims_parser = subparsers.add_parser('runsims', description=header, help='Analyze a GSMM previously built.', formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)

    
    # add arguments for the 'getmaps' command
    getmaps_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    getmaps_parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('gsrap')['Version']}", help="Show version number and exit.")
    getmaps_parser.add_argument("--verbose", action='store_true', help="Make stdout messages more verbose, including debug messages.")
    getmaps_parser.add_argument("-o", "--outdir", metavar='', type=str, default='./', help="Main output directory (will be created if not existing).")
    getmaps_parser.add_argument("--keeptmp", action='store_true', help="Do not delete temporary raw files.")
    getmaps_parser.add_argument("--usecache", action='store_true', help="Do not update previously downloaded records (save time).")
    
    
    # add arguments for the 'parsedb' command
    parsedb_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    parsedb_parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('gsrap')['Version']}", help="Show version number and exit.")
    parsedb_parser.add_argument("--verbose", action='store_true', help="Make stdout messages more verbose, including debug messages.")
    parsedb_parser.add_argument("-o", "--outdir", metavar='', type=str, default='./', help="Main output directory (will be created if not existing).")
    parsedb_parser.add_argument("-i", "--inmaps", metavar='', type=str, default='./gsrap.maps', help="Input file 'gsrap.maps' previously produced using the 'getmaps' subcommand.")
    parsedb_parser.add_argument("-p", "--progress", action='store_true', help="Show progress for each map.")
    parsedb_parser.add_argument("--module", action='store_true', help="Show progress for each module of each map (use only with --progress).")
    parsedb_parser.add_argument("-f", "--focus", metavar='', type=str, default='-', help="Focus on a particular map/module (use only with --progress).")
    parsedb_parser.add_argument("-m", "--media", metavar='', type=str, default='M9,M9an,M9photo', help="Media to use during growth simulations (comma-separated IDs).")
    parsedb_parser.add_argument("--precursors", action='store_true', help="Verify biosynthesis of biomass precursors and show blocked ones.")
    parsedb_parser.add_argument("--biosynth", action='store_true', help="Check biosynthesis of all metabolites and detect dead-ends.")
    parsedb_parser.add_argument("-e", "--eggnog", nargs='+', metavar='', type=str, default='-', help="Path to the optional eggnog-mapper annotation table(s).")
    #parsedb_parser.add_argument("-z", "--zeroes", action='store_true', help="Show maps/modules with 0%% coverage, in addition to partials (use only with --progress).")
    parsedb_parser.add_argument("--goodbefore", metavar='', type=str, default='-', help="Syntax is {pure_mid}-{rid1}-{rid2}. From top to bottom, build the universe until reaction {rid1}, transport {rid2} and metabolite {pure_mid} are reached.")
    parsedb_parser.add_argument("--onlyauthor", metavar='', type=str, default='-', help="Build the universe by parsing contents of the specified author ID only. Contents affected by --goodbefore are parsed anyway.")
    
    
    # add arguments for the 'mkmodel' command
    mkmodel_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    mkmodel_parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('gsrap')['Version']}", help="Show version number and exit.")
    mkmodel_parser.add_argument("--verbose", action='store_true', help="Make stdout messages more verbose, including debug messages.")
    mkmodel_parser.add_argument("-c", "--cores", metavar='', type=int, default=0, help="Number of cores to use (if 0, use all available cores).")
    mkmodel_parser.add_argument("-o", "--outdir", metavar='', type=str, default='./', help="Main output directory (will be created if not existing).")
    mkmodel_parser.add_argument("-e", "--eggnog", nargs='+', metavar='', type=str, default='-', help="Path to the eggnog-mapper annotation table(s).")
    mkmodel_parser.add_argument("-u", "--universe", metavar='', type=str, default='-', help="Path to the universe model (SBML format).")
    mkmodel_parser.add_argument("-i", "--force_inclusion", metavar='', type=str, default='-', help="Force the inclusion of the specified reactions (comma-separated IDs).")
    mkmodel_parser.add_argument("-f", "--gap_fill", metavar='', type=str, default='-', help="Media to use during gap-filling (comma-separated IDs); if not provided, gap-filling will be skipped.")
    mkmodel_parser.add_argument("-x", "--exclude_orphans", action='store_true', help="Exclude orphan reactions from the gap-filling repository.")
    #mkmodel_parser.add_argument("-r", "--force_removal", metavar='', type=str, default='-', help="Force the removal of the specified reactions (comma-separated IDs) (it applies after gap-filling, before Biolog(R)-based curation).")
    mkmodel_parser.add_argument("-l", "--biolog", metavar='', type=str, default='-', help="Strain ID associated to binary Biolog(R) PM1, PM2A, PM3B and PM4A plates; if not provided, Biolog(R)-based model curation will be skipped (use with --cnps and --gap_fill).")
    mkmodel_parser.add_argument("-s", "--cnps", metavar='', type=str, default='glc__D,nh4,pi,so4', help="Starting C, N, P and S source metabolites (comma-separated IDs).")
    mkmodel_parser.add_argument("--conditional", metavar='', type=float, default=0.5, help="Expected minimum fraction of reactions in a biosynthetic pathway for an actually present conditional biomass precursor.")
    mkmodel_parser.add_argument("--biosynth", action='store_true', help="Check biosynthesis of all metabolites and detect dead-ends.")
    mkmodel_parser.add_argument("-b", "--biomass", metavar='', type=str, default='-', help="Strain ID associated to experimental biomass data.")
    
    
    # add arguments for the 'runsims' command
    runsims_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    runsims_parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('gsrap')['Version']}", help="Show version number and exit.")
    runsims_parser.add_argument("--verbose", action='store_true', help="Make stdout messages more verbose, including debug messages.")
    runsims_parser.add_argument("-o", "--outdir", metavar='', type=str, default='./', help="Main output directory (will be created if not existing).")
    runsims_parser.add_argument("-i", "--inmodel", metavar='', type=str, default='-', help="Input strain-specific GSMM.")
    runsims_parser.add_argument("-m", "--media", metavar='', type=str, default='-', help="Media to use during growth simulations (comma-separated IDs); if not provided, growth simulations will be skipped.")
    runsims_parser.add_argument("--fva", action='store_true', help="Perform FVA during growth simulations.")
    runsims_parser.add_argument("--biosynth", action='store_true', help="Check biosynthesis of all metabolites and detect dead-ends.")
    runsims_parser.add_argument("--cnps", metavar='', type=str, default='-', help="Starting C, N, P and S source metabolites (comma-separated IDs); if not provided, anternative substrate analysis will be skipped (use with --media).")
    runsims_parser.add_argument("--biolog", metavar='', type=str, default='-', help="Strain ID associated to binary Biolog(R) PM1, PM2A, PM3B and PM4A plates; if not provided, Biolog(R) simulations will be skipped (use with --cnps).")
    runsims_parser.add_argument("--omission", action='store_true', help="Perform single omission experiments to study auxotrophies.")
    runsims_parser.add_argument("--essential", action='store_true', help="Predict essential genes (single-gene knock-out simulations).")
    runsims_parser.add_argument("--factors", action='store_true', help="Predict putative growth factors.")

    
    # check the inputted subcommand, automatic sys.exit(1) if a bad subprogram was specied. 
    args = parser.parse_args()
    
    
    
    # set up the logger:
    logger = get_logger('gsrap', args.verbose)
    
    
    
    # show a welcome message:
    set_header_trailer_formatter(logger.handlers[0])
    logger.info(header + '\n')
    command_line = '' # print the full command line:
    for arg, value in vars(args).items():
        if arg == 'subcommand': command_line = command_line + f"gsrap {value} "
        else: command_line = command_line + f"--{arg} {value} "
    logger.info('Inputted command line: "' + command_line.rstrip() + '".\n')
    
    
    
    # run the program:
    set_usual_formatter(logger.handlers[0])
    current_date_time = datetime.now()
    formatted_date = current_date_time.strftime("%Y-%m-%d")
    logger.info(f"Welcome to 'gsrap {args.subcommand}', it's {formatted_date}!")
    logger.debug(f"COBRApy started with solver: '{solver_name}'.")
    try: 
        # choose which subcommand to lauch: 
        if args.subcommand == 'getmaps':
            response = getmaps_command(args, logger)
        if args.subcommand == 'parsedb':
            response = parsedb_command(args, logger)
        if args.subcommand == 'mkmodel':
            response = mkmodel_command(args, logger)
        if args.subcommand == 'runsims':
            response = runsims_command(args, logger)
            
        if response == 0:
            logger.info(f"'gsrap {args.subcommand}' terminated without errors!")
    except: 
        # show the error stack trace for this un-handled error: 
        response = 1
        logger.error('Traceback is reported below.\n\n' + traceback.format_exc())


    
    # terminate the program:
    set_header_trailer_formatter(logger.handlers[0])
    if response == 1: 
        print(file=sys.stderr)  # separate last error from fresh prompt
        sys.exit(1)
    else: 
        # show a bye message
        logger.info('\n' + header)
        sys.exit(0) # exit without errors
        
        
        
if __name__ == "__main__":
    main()