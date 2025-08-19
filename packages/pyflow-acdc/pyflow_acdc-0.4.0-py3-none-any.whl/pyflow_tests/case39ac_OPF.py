import pyflow_acdc as pyf

def case39ac_OPF():

    grid,res = pyf.case39()

    pyf.Optimal_PF(grid)

    res.All()


def run_test():
    """Test case39 AC optimal power flow."""
    try:
        import pyomo
    except ImportError:
        print("pyomo is not installed...")
        return  
    
    case39ac_OPF()
if __name__ == "__main__":
    run_test()

