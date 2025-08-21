"""
Modern Acquisition Function Core for PyMBO
==========================================

This module provides the modern acquisition function implementation that directly
replaces PyMBO's legacy EHVI and LogEI with qNEHVI and qLogEI.

This is integrated into PyMBO's core - no installation or setup required.
Your main.py works unchanged and automatically gets modern acquisition functions.

Author: Generated for PyMBO enhancement
Date: 2025-08-18
"""

import torch
import logging
from typing import Union, Optional, Dict, List, Any
import warnings

# Core BoTorch imports for modern acquisition
from botorch.models import SingleTaskGP, ModelListGP
from botorch.models.transforms import Normalize, Standardize
from gpytorch.kernels import ScaleKernel, MaternKernel
from gpytorch.mlls import ExactMarginalLogLikelihood, SumMarginalLogLikelihood
from botorch.fit import fit_gpytorch_mll

# Modern acquisition functions (2024 SOTA)
from botorch.acquisition.multi_objective import qLogNoisyExpectedHypervolumeImprovement
from botorch.acquisition.logei import qLogExpectedImprovement
from botorch.acquisition.analytic import LogExpectedImprovement  # Fallback

# Import unified kernel
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, parent_dir)
    from unified_kernel import UnifiedExponentialKernel, is_mixed_variable_problem
    UNIFIED_KERNEL_AVAILABLE = True
except ImportError:
    UNIFIED_KERNEL_AVAILABLE = False
    warnings.warn("UnifiedExponentialKernel not available - using MaternKernel fallback")

logger = logging.getLogger(__name__)

# Configuration
MIN_DATA_POINTS = 3
DEFAULT_ALPHA = 0.05
DEFAULT_PRUNE_BASELINE = True

def create_modern_kernel(params_config: Dict[str, Dict[str, Any]], input_dim: int) -> torch.nn.Module:
    """
    Create appropriate kernel based on parameter configuration.
    
    Args:
        params_config: PyMBO parameter configuration
        input_dim: Input dimension
        
    Returns:
        Configured kernel (UnifiedExponentialKernel or MaternKernel fallback)
    """
    if UNIFIED_KERNEL_AVAILABLE and params_config:
        try:
            logger.info(f"Creating UnifiedExponentialKernel for {len(params_config)} parameters")
            kernel = UnifiedExponentialKernel(params_config, ard_num_dims=input_dim)
            
            if is_mixed_variable_problem(params_config):
                logger.info("Mixed variable problem detected - using UnifiedExponentialKernel")
            else:
                logger.info("Continuous-only problem - using UnifiedExponentialKernel for consistency")
                
            return kernel
            
        except Exception as e:
            logger.warning(f"UnifiedExponentialKernel failed: {e}, using MaternKernel fallback")
    
    # Fallback to standard kernel
    logger.info("Using MaternKernel fallback")
    return MaternKernel(nu=2.5, ard_num_dims=input_dim)

def build_modern_gp_model(train_X: torch.Tensor, 
                         train_Y: torch.Tensor,
                         params_config: Optional[Dict[str, Dict[str, Any]]] = None) -> Optional[Union[SingleTaskGP, ModelListGP]]:
    """
    Build modern GP model compatible with qNEHVI/qLogEI.
    
    Args:
        train_X: Training inputs (n_samples, n_params)
        train_Y: Training outputs (n_samples, n_objectives)
        params_config: PyMBO parameter configuration
        
    Returns:
        Trained GP model or None if failed
    """
    try:
        if train_X.shape[0] < MIN_DATA_POINTS:
            logger.warning(f"Insufficient data points: {train_X.shape[0]} < {MIN_DATA_POINTS}")
            return None
            
        if train_X.shape[0] != train_Y.shape[0]:
            logger.error(f"Dimension mismatch: X={train_X.shape[0]}, Y={train_Y.shape[0]}")
            return None
        
        # Filter out non-finite values
        finite_mask = torch.isfinite(train_Y).all(dim=1) & torch.isfinite(train_X).all(dim=1)
        
        if finite_mask.sum() < MIN_DATA_POINTS:
            logger.warning(f"Insufficient finite data points: {finite_mask.sum()} < {MIN_DATA_POINTS}")
            return None
            
        X_filtered = train_X[finite_mask]
        Y_filtered = train_Y[finite_mask]
        
        logger.info(f"Building GP with {X_filtered.shape[0]} samples, {X_filtered.shape[1]} params, {Y_filtered.shape[1]} objectives")
        
        if Y_filtered.shape[-1] == 1:
            # Single output case
            base_kernel = create_modern_kernel(params_config, X_filtered.shape[-1])
            covar_module = ScaleKernel(base_kernel)
            
            model = SingleTaskGP(
                train_X=X_filtered,
                train_Y=Y_filtered,
                covar_module=covar_module,
                input_transform=Normalize(d=X_filtered.shape[-1]),
                outcome_transform=Standardize(m=1),
            )
            
            mll = ExactMarginalLogLikelihood(model.likelihood, model)
            
        else:
            # Multi-output case: use ModelListGP with individual SingleTaskGPs
            models = []
            for i in range(Y_filtered.shape[-1]):
                Y_single = Y_filtered[:, i:i+1]  # Keep 2D shape
                
                base_kernel_i = create_modern_kernel(params_config, X_filtered.shape[-1])
                covar_module_i = ScaleKernel(base_kernel_i)
                
                model_i = SingleTaskGP(
                    train_X=X_filtered,
                    train_Y=Y_single,
                    covar_module=covar_module_i,
                    input_transform=Normalize(d=X_filtered.shape[-1]),
                    outcome_transform=Standardize(m=1),
                )
                models.append(model_i)
            
            model = ModelListGP(*models)
            mll = SumMarginalLogLikelihood(model.likelihood, model)
        
        # Fit the model
        logger.info("Training GP model...")
        fit_gpytorch_mll(mll)
        
        logger.info(f"Successfully trained modern GP: {X_filtered.shape} -> {Y_filtered.shape}")
        return model
        
    except Exception as e:
        logger.error(f"Error building modern GP model: {e}")
        return None

def setup_qnehvi_acquisition(model: Union[SingleTaskGP, ModelListGP],
                            train_X: torch.Tensor,
                            train_Y: torch.Tensor) -> Optional[qLogNoisyExpectedHypervolumeImprovement]:
    """
    Set up qNEHVI acquisition function for multi-objective optimization.
    
    Args:
        model: Trained GP model
        train_X: Training inputs for baseline
        train_Y: Training outputs for reference point calculation
        
    Returns:
        qNEHVI acquisition function or None if failed
    """
    try:
        if train_Y.shape[-1] < 2:
            logger.error("qNEHVI requires at least 2 objectives")
            return None
            
        # Filter finite data for reference point calculation
        finite_mask = torch.isfinite(train_Y).all(dim=1)
        clean_Y = train_Y[finite_mask]
        clean_X = train_X[finite_mask]
        
        if clean_Y.shape[0] == 0:
            logger.warning("No finite data points for qNEHVI")
            return None
            
        # Calculate adaptive reference point
        margin = 0.1 * (clean_Y.max(dim=0)[0] - clean_Y.min(dim=0)[0])
        ref_point = clean_Y.min(dim=0)[0] - margin
        ref_point = torch.minimum(ref_point, clean_Y.min(dim=0)[0] - 1e-6)
        
        logger.info(f"qNEHVI setup: {clean_Y.shape[0]} points, ref_point={ref_point.tolist()}")
        
        # Limit baseline size for numerical stability
        baseline_limit = min(clean_X.shape[0], 10)
        limited_X_baseline = clean_X[:baseline_limit] if clean_X.shape[0] > baseline_limit else clean_X
        
        # Create qLogNEHVI acquisition function (2024 SOTA)
        qnehvi = qLogNoisyExpectedHypervolumeImprovement(
            model=model,
            ref_point=ref_point,
            X_baseline=limited_X_baseline,
            prune_baseline=DEFAULT_PRUNE_BASELINE,
            alpha=DEFAULT_ALPHA,
        )
        
        logger.info("qNEHVI acquisition function created successfully")
        return qnehvi
        
    except Exception as e:
        logger.error(f"Error setting up qNEHVI: {e}")
        return None

def setup_qlogei_acquisition(model: Union[SingleTaskGP, ModelListGP],
                            train_Y: torch.Tensor) -> Optional[qLogExpectedImprovement]:
    """
    Set up qLogEI acquisition function for single-objective optimization.
    
    Args:
        model: Trained GP model
        train_Y: Training outputs to find best value
        
    Returns:
        qLogEI acquisition function or None if failed
    """
    try:
        if train_Y.shape[-1] != 1:
            logger.error("qLogEI requires exactly 1 objective")
            return None
            
        # Find best observed value
        finite_mask = torch.isfinite(train_Y)
        if not finite_mask.any():
            logger.warning("No finite values for qLogEI")
            return None
            
        finite_Y = train_Y[finite_mask]
        best_f = finite_Y.max()
        
        logger.info(f"qLogEI setup: best_f={best_f.item()}")
        
        # Create qLogEI acquisition function
        qlogei = qLogExpectedImprovement(
            model=model,
            best_f=best_f,
        )
        
        logger.info("qLogEI acquisition function created successfully")
        return qlogei
        
    except Exception as e:
        logger.error(f"Error setting up qLogEI: {e}")
        return None

def setup_fallback_acquisition(model: Union[SingleTaskGP, ModelListGP],
                              train_Y: torch.Tensor) -> Optional[LogExpectedImprovement]:
    """
    Set up fallback acquisition function (analytic LogEI).
    
    Args:
        model: Trained GP model
        train_Y: Training outputs
        
    Returns:
        LogEI acquisition function or None if failed
    """
    try:
        # Use first objective for fallback
        if train_Y.shape[-1] > 1:
            Y_single = train_Y[:, 0]
            logger.info("Using first objective for fallback LogEI")
        else:
            Y_single = train_Y.squeeze(-1)
            
        finite_mask = torch.isfinite(Y_single)
        if not finite_mask.any():
            logger.warning("No finite values for fallback LogEI")
            return None
            
        finite_Y = Y_single[finite_mask]
        best_f = finite_Y.max()
        
        logger.info(f"Fallback LogEI setup: best_f={best_f.item()}")
        
        # For ModelListGP, use first model
        if isinstance(model, ModelListGP):
            model_for_logei = model.models[0]
        else:
            model_for_logei = model
        
        # Create fallback acquisition function
        logei = LogExpectedImprovement(
            model=model_for_logei,
            best_f=best_f,
        )
        
        logger.info("Fallback LogEI acquisition function created successfully")
        return logei
        
    except Exception as e:
        logger.error(f"Error setting up fallback acquisition: {e}")
        return None

def create_modern_acquisition_function(train_X: torch.Tensor,
                                     train_Y: torch.Tensor,
                                     objective_names: List[str],
                                     params_config: Optional[Dict[str, Dict[str, Any]]] = None) -> Optional[torch.nn.Module]:
    """
    Create modern acquisition function - this is the main entry point that replaces PyMBO's legacy functions.
    
    Args:
        train_X: Training inputs (n_samples, n_params)
        train_Y: Training outputs (n_samples, n_objectives)
        objective_names: List of objective names
        params_config: PyMBO parameter configuration
        
    Returns:
        Modern acquisition function or None if failed
    """
    try:
        logger.info(f"Creating modern acquisition function for {len(objective_names)} objectives")
        
        # Build modern GP model
        model = build_modern_gp_model(train_X, train_Y, params_config)
        if model is None:
            logger.error("Failed to build GP model")
            return None
        
        # Choose acquisition function based on number of objectives
        if len(objective_names) == 1:
            # Single-objective: use qLogEI
            logger.info("Setting up qLogEI for single-objective optimization")
            acq_func = setup_qlogei_acquisition(model, train_Y)
            
        elif len(objective_names) > 1:
            # Multi-objective: use qNEHVI
            logger.info("Setting up qNEHVI for multi-objective optimization")
            acq_func = setup_qnehvi_acquisition(model, train_X, train_Y)
            
        else:
            logger.error("No objectives specified")
            return None
        
        # Fallback if primary acquisition function failed
        if acq_func is None:
            logger.warning("Primary acquisition function failed, using fallback")
            acq_func = setup_fallback_acquisition(model, train_Y)
            
        if acq_func is None:
            logger.error("All acquisition function setups failed")
            return None
            
        logger.info(f"Successfully created {type(acq_func).__name__} acquisition function")
        return acq_func
        
    except Exception as e:
        logger.error(f"Error creating modern acquisition function: {e}")
        return None