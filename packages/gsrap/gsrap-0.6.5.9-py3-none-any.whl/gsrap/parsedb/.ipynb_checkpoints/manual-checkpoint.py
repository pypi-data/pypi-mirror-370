


def get_deprecated_kos():
    deprecated_kos = [
        'K11189',  # should be K02784
        'K07011',  # linked to lp_1215(cps3A) and lp_1216(cps3B) during 2018 and not replaced
    ]
    return deprecated_kos



def get_rids_with_mancheck_gpr():
    rids_mancheck_gpr = [  # reactions with manually checked GPRs
        'SUCD1', 'ALKP', 'PFK_3', 'TCMPTS', 'PPA', 'APSR',
        'NADHPO', 'ACOD', '5DOAN', '5DRBK', '5DRBPI', '5DRBUPD',
        'FNPOR', 'THZPSN', 'PPTGP', 'ALATA_D2', 'XYLUR1'
    ]
    return rids_mancheck_gpr



def get_manual_sinks():
    
    return ['apoACP', 'aponit', 'apocarb', 'thioca', 'THI5p_b', 'cyE', 'meanfa']



def get_manual_demands():
    
    return ['scp', 'amob', 'dialurate', 'THI5p_a', 'partmass' ]



def get_custom_groups():
    
    
    return {
        'gr_ptdSTA': ['UAMAGLL', 'UMNS', 'UPPNAPT', 'UAGPT2', 'UAGPGAL', 'UAGPN6GT', 'UAAGGTLGAGT', 'UAAGGTLG3AGT', 'PPTGP'],
        'gr_ptdSTR': ['UAMAGLL', 'UMNS', 'UPPNAPT', 'UAGPT2', 'PPGAAE1', 'PPGAAE2', 'PPTGP2'],
        'gr_ptdDAP': ['UGMDL', 'UGMDDS', 'UGMDDPT', 'UAGPT3', 'PPTGP3'],
        'gr_HemeO': ['HEMEOS'],
        'gr_WTA1': ['ACGAMT', 'UNDBD', 'WTAGPT', 'WTAGPP', 'WTAUGLCT2', 'WTAALAT3', 'WTAPL3'],
        'gr_WTA2': ['ACGAMT', 'UNDBD', 'WTAGPT', 'WTARBT2', 'WTARPP2', 'WTAUGLCT', 'WTAALAT2', 'WTAPL2'],
        'gr_WTA3': ['ACGAMT', 'UNDBD', 'WTAGPT', 'WTAGPT2', 'WTARPP', 'WTAGLCNACT', 'WTAALAT', 'WTAPL'],
        'gr_WTA4': ['UNACGYL', 'UADDTRS', 'AATGALT', 'TAA13GLT', 'TAARPTR', 'TAANGTR', 'TAANGTR2', 'LPSCHPT', 'TACCHPT', 'T4WTAPOL', 'WTAPL4', 'WTAT4ALAT'], # type-IV WTA
        'gr_LTA1': ['UGDIAT', 'UGLDIAT', 'GGGDAGF2', 'LIPOPO2', 'LTANACT', 'LTAALAT2'],
        'gr_LTA2': ['UGDIAT', 'UGADIAT', 'GGGDAGF', 'LIPOPO', 'LTAGAT', 'LTAALAT'],
        'gr_LTA3': ['UNACGYL', 'UADDTRS', 'AATGALT', 'TAA13GLT', 'TAARPTR', 'TAANGTR', 'TAANGTR2', 'LPSCHPT', 'TACCHPT', 'T4WTAPOL', 'T4LTAL', 'LTAT4ALAT'], # type-IV LTA
        'gr_br': ['LYEH1', 'HIPCD1', 'LYEH2', 'HIPCD2', 'BHBRH1', 'BHBRH2'],
        'gr_PHA1': ['ACACT1r', 'AACOAR_syn', 'PHBS_syn_1', 'PHBDEP_1'],    # PHA from glycolyis
        'gr_epsLAB': ['PGTLAB', 'GTSTLAB', 'EPSPOLAB'],
    }