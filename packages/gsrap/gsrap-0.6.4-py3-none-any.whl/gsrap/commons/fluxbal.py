import warnings
import logging



def get_optthr():
    
    return 0.001   # optimization threshold



def fba_no_warnings(model): 
    
    # Ignore eventual "UserWarning: Solver status is 'infeasible'."
    with warnings.catch_warnings():  # temporarily suppress warnings for this block
        warnings.simplefilter("ignore")  # ignore all warnings
        
        # disable warnings
        cobra_logger = logging.getLogger("cobra.util.solver")
        old_level = cobra_logger.level
        cobra_logger.setLevel(logging.ERROR)   

        # perform FBA: 
        res = model.optimize()
        obj_value = res.objective_value
        status = res.status

        # restore original behaviour: 
        cobra_logger.setLevel(old_level)   

        return res, obj_value, status
    
    
    
def verify_growth(model, boolean=True):
            
    
    res, obj_value, status = fba_no_warnings(model)
    if boolean:
        if obj_value < get_optthr() or status=='infeasible':
            return False
        else: return True
    else:
        if status =='infeasible':
            return 'infeasible'
        elif obj_value < get_optthr():
            return 0
        else:
            return round(obj_value, 3)
        
        
        






