import torch
from .util import mps_to_standard_form
from .enhancements import preconditioning
from .primal_dual_hybrid_gradient import pdlp_algorithm


def solve(mps_file_path, tol=1e-4, device='auto', precondition=True, primal_weight_update = True, adaptive_stepsize = True, infeasibility_detect = False, verbose=False, support_sparse = False, max_kkt = 100000, time_limit=3600):
    '''
    Run LP solver with configuration options.
  
    Args:
      mps_file_path: Path to LP in MPS file format.
      tol: Error tolerance (default 1e-4)
      device: 'cpu', 'gpu', or 'auto' (default 'auto')
      precondition: Precondtion the LP before solving (default True)
      primal_weight_update: Update primal weights at every restart (default True)
      adaptive_stepsize: Adapt the step size every iteration (default True)
      infeasibility_detect: Check if iterates give infeasibility certificate (default False)
      verbose: Output information on the solver (default False)
      support_sparse: Use sparse tensors if they are beneficial (default False)
      max_kkt: Maximum KKT passes solver will use (default 100000)
      time_limit: Maximum time in seconds that solver will run (default 3600)
    Returns:
      minimizer solution to primal LP
      Primal objective value
      Status of solver (Solved, Unsolved)
    '''
    
    # --- Device Selection ---
    if device == 'auto' or device == 'gpu':
        if torch.cuda.is_available():
            device = torch.device('cuda')
            print(f"PyTorch is using ROCm/CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
            print("ROCm/CUDA not available. PyTorch is using CPU.")
    else:
        device = torch.device(device)
        print(f"PyTorch is using device: {device}")

    if verbose:
      print(f"\nConfiguration:")
      print(f"Instance path: {mps_file_path}")
      print(f"Tolerance: {tol}")
      print(f"Time limit: {time_limit} seconds")
      print(f"Max KKT passes: {max_kkt}")
      print(f"Preconditioning: {precondition}")
      print(f"Primal weight update: {primal_weight_update}")
      print(f"Adaptive stepsize: {adaptive_stepsize}")
      print(f"Infeasibility detection: {infeasibility_detect}")
    
    try:
        # --- Load problem ---
        c, K, q, m_ineq, l, u= mps_to_standard_form(mps_file_path, device=device, support_sparse=support_sparse, verbose=verbose)
    except Exception as e:
        print(f"Failed to load MPS file: {mps_file_path}. Error: {e}")

    
    try:
        # PRECONDITION
        if precondition:
            K, c, q, l, u, dt_precond, time_used= preconditioning(c, K, q, l, u, device = device)
        else:
            time_used = 0.0
            dt_precond = None
        
        x, prim_obj, k, n, j, status, total_time = pdlp_algorithm(
            K, m_ineq, c, q, l, u, device, 
            max_kkt=max_kkt, tol=tol, verbose=verbose, restart_period=40, 
            precondition=precondition, primal_update=primal_weight_update, 
            adaptive=adaptive_stepsize, data_precond=dt_precond, 
            infeasibility_detect=infeasibility_detect,
            time_limit=time_limit, time_used=time_used
        )
        
        if verbose:  
          print("Objective Value:", prim_obj)
          print("Iterations:", k)
          print("Restarts:", n)
          print("KKT Passes:", j)
          print("Total Time:", total_time, "seconds")
          print("\nMinimizer (first 10 variables):")
          print(x[:10].cpu().numpy())
        
        return x, prim_obj, status
        
    except Exception as e:
        print(f"Solver Error: {e}")
