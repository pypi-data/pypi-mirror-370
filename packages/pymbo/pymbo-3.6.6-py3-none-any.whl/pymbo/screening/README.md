# SGLBO Screening Module

A sophisticated parameter space screening module implementing Stochastic Gradient Line Bayesian Optimization (SGLBO) for efficient exploration before detailed Bayesian optimization.

## Overview

This module performs fast, low-resolution parameter space screening to identify promising regions for subsequent detailed optimization using the main Bayesian optimization software. It combines gradient-based exploration with Bayesian optimization principles for efficient screening.

## Features

- **SGLBO Algorithm**: Advanced screening combining gradient information with Bayesian optimization
- **Parameter Handling**: Compatible with main software parameter configurations (continuous, categorical, discrete)
- **Multiple Response Support**: Handles Maximize, Minimize, and Target optimization goals
- **Design Space Generation**: Creates Central Composite Design (CCD) and other DOE designs around optimal points
- **Convergence Detection**: Automatic detection of local optima during screening
- **Comprehensive Analysis**: Parameter importance analysis, response trend analysis, and optimization recommendations
- **Export Capabilities**: Results export to JSON, Excel, and Pickle formats

## Module Structure

```
screening/
├── __init__.py                 # Module initialization and exports
├── parameter_handler.py        # Parameter validation and transformation
├── screening_optimizer.py      # Main SGLBO implementation
├── design_space_generator.py   # Design space generation around optima
├── screening_results.py        # Results storage and analysis
├── example_usage.py           # Complete usage example
└── README.md                  # This documentation
```

## Quick Start

### 1. Basic Setup

```python
from pymbo.screening import ScreeningOptimizer, ScreeningResults, DesignSpaceGenerator

# Define parameters (matching main software format)
params_config = {
    "Temperature": {
        "type": "continuous",
        "bounds": [25, 200],
        "precision": 1
    },
    "Pressure": {
        "type": "continuous", 
        "bounds": [1, 10],
        "precision": 2
    },
    "Catalyst": {
        "type": "categorical",
        "bounds": ["A", "B", "C", "D"]
    }
}

# Define responses
responses_config = {
    "Yield": {"goal": "Maximize"},
    "Purity": {"goal": "Maximize"},
    "Cost": {"goal": "Minimize"}
}
```

### 2. Initialize Screening

```python
# Create screening optimizer
screening_optimizer = ScreeningOptimizer(
    params_config=params_config,
    responses_config=responses_config,
    gradient_step_size=0.1,
    exploration_factor=0.15,
    max_iterations=20,
    convergence_threshold=0.02,
    n_initial_samples=8
)

# Create results manager
results_manager = ScreeningResults(params_config, responses_config)
```

### 3. Run Screening Process

```python
# Step 1: Generate initial experiments
initial_experiments = screening_optimizer.suggest_initial_experiments()

# Step 2: Conduct experiments and add data
# (In real usage, replace simulation with actual experiments)
for params in initial_experiments:
    responses = conduct_experiment(params)  # Your experimental function
    experiment_data = {**params, **responses}
    data_df = pd.DataFrame([experiment_data])
    screening_optimizer.add_experimental_data(data_df)
    results_manager.add_experimental_data(data_df)

# Step 3: Iterative screening
while not screening_optimizer.converged:
    # Suggest next experiment
    next_experiment = screening_optimizer.suggest_next_experiment()
    
    # Conduct experiment
    responses = conduct_experiment(next_experiment)
    experiment_data = {**next_experiment, **responses}
    
    # Add data and analyze
    new_data_df = pd.DataFrame([experiment_data])
    screening_optimizer.add_experimental_data(new_data_df)
    
    iteration_info = screening_optimizer.run_screening_iteration()
    results_manager.add_experimental_data(new_data_df, iteration_info)
    
    # Check convergence
    convergence_info = screening_optimizer.check_convergence()
    if convergence_info["converged"]:
        break
```

### 4. Generate Design Space

```python
# Get best parameters from screening
best_params, best_responses = results_manager.get_best_parameters()

# Generate design space for detailed optimization
from pymbo.screening import ParameterHandler, DesignSpaceGenerator

param_handler = ParameterHandler(params_config)
design_generator = DesignSpaceGenerator(param_handler)

# Create Central Composite Design around best point
design_points = design_generator.generate_central_composite_design(
    center_point=best_params,
    design_radius=0.15,
    include_center=True,
    include_axial=True,
    include_factorial=True
)

print(f"Generated {len(design_points)} points for detailed optimization")
```

### 5. Analysis and Export

```python
# Analyze results
param_effects = results_manager.analyze_parameter_effects()
response_trends = results_manager.analyze_response_trends()
recommendations = results_manager.generate_optimization_recommendations()

# Export results
results_manager.export_results("screening_results.json", format="json")
results_manager.export_results("screening_results.xlsx", format="excel")

# Get comprehensive summary
summary = results_manager.get_results_summary()
```

## Configuration Options

### Parameter Types

- **Continuous**: Numeric parameters with min/max bounds
- **Discrete**: Integer parameters with min/max bounds  
- **Categorical**: Choice parameters with list of allowed values

### Response Goals

- **Maximize**: Optimize for highest values
- **Minimize**: Optimize for lowest values
- **Target**: Optimize toward specific target value

### SGLBO Parameters

- `gradient_step_size`: Step size for gradient-based moves (default: 0.1)
- `exploration_factor`: Balance between exploitation and exploration (default: 0.1)
- `max_iterations`: Maximum screening iterations (default: 50)
- `convergence_threshold`: Convergence criterion (default: 0.01)
- `n_initial_samples`: Initial Latin Hypercube samples (default: 5)

### Design Space Options

- **Central Composite Design (CCD)**: Standard response surface design
- **Full Factorial**: Complete factorial design with multiple levels
- **Box-Behnken**: Efficient design for 3+ parameters
- **Adaptive Design**: Importance-weighted design space

## Advanced Features

### Multi-Center Design Spaces

```python
# Generate design around multiple optima
center_points = [best_params_1, best_params_2, best_params_3]
multi_design = design_generator.generate_multi_center_design(
    center_points=center_points,
    design_radius=0.15,
    points_per_center=15,
    design_type="ccd"
)
```

### Parameter Importance Analysis

```python
# Analyze which parameters most affect responses
param_effects = results_manager.analyze_parameter_effects()

# Get parameter rankings
rankings = param_effects["overall_parameter_importance"]
for rank in rankings:
    print(f"{rank['parameter']}: {rank['importance_score']:.3f}")
```

### Custom Convergence Criteria

```python
# Check convergence with custom parameters
convergence_info = screening_optimizer.check_convergence()
print(f"Converged: {convergence_info['converged']}")
print(f"Improvement: {convergence_info['improvement']:.4f}")
print(f"Recommendation: {convergence_info['recommendation']}")
```

## Integration with PyMBO

The screening module is designed for seamless integration with PyMBO:

### 1. Parameter Compatibility
- Uses identical parameter configuration format
- Supports same parameter types and constraints
- Compatible validation and transformation functions

### 2. Workflow Integration
```python
# Screening phase
screening_results = run_screening_optimization()
best_params = screening_results.get_best_parameters()[0]
design_points = generate_design_space_around(best_params)

# Main optimization phase
main_optimizer = EnhancedMultiObjectiveOptimizer(
    params_config=params_config,
    responses_config=responses_config
)

# Initialize with design points from screening
for point in design_points:
    # Conduct detailed experiments at design points
    # Add to main optimizer for precise optimization
```

### 3. Data Transfer
- Export screening results to formats compatible with main software
- Transfer parameter importance insights
- Use screening convergence information for main optimization strategy

## Performance Characteristics

### Efficiency
- **Fast Exploration**: ~10-50 experiments for initial screening
- **Low Resolution**: Optimized for broad exploration, not precise optimization
- **Gradient Guidance**: Uses gradient information for directed search
- **Adaptive Sampling**: Balances exploitation and exploration

### Scalability
- **Parameter Dimensions**: Efficient for 2-10 parameters
- **Response Variables**: Handles multiple objectives simultaneously
- **Computational**: Lightweight GP models for fast iteration

### Robustness
- **Noise Handling**: Robust to experimental noise and outliers
- **Convergence**: Multiple convergence criteria prevent premature stopping
- **Fallback**: Graceful fallback to random sampling when needed

## Example Results

After running the screening module:

```
Screening Summary:
  Total experiments: 23
  Iterations completed: 15
  Converged: True
  Best parameters: {'Temperature': 118, 'Pressure': 5.8, 'Catalyst': 'B', 'pH': 7.9}

Parameter Importance Ranking:
  Temperature: 0.847
  Catalyst: 0.623
  Pressure: 0.401
  pH: 0.234

Generated 25 design points for detailed optimization
Next Steps:
  1. Generate design space around best parameters
  2. Configure main Bayesian optimization software
  3. Set up multi-objective optimization if applicable
  4. Plan experimental validation campaign
```

## Error Handling

The module includes comprehensive error handling:

- Parameter validation with detailed error messages
- Graceful fallback to simpler methods when advanced methods fail
- Extensive logging for debugging and monitoring
- Data validation and consistency checks

## Dependencies

- **numpy**: Numerical computations
- **pandas**: Data handling and analysis
- **scipy**: Statistical functions and optimization
- **scikit-learn**: Gaussian Process models
- **json/pickle**: Data serialization

## Best Practices

1. **Start with Sufficient Initial Samples**: Use at least 2×(number of parameters) initial samples
2. **Choose Appropriate Convergence Threshold**: 0.01-0.05 works well for most applications
3. **Balance Exploration**: Adjust `exploration_factor` based on problem characteristics
4. **Validate Results**: Always inspect screening results before proceeding to detailed optimization
5. **Export Results**: Save screening results for reproducibility and analysis

## Troubleshooting

### Common Issues

1. **Slow Convergence**: Increase `gradient_step_size` or `exploration_factor`
2. **Premature Convergence**: Decrease `convergence_threshold` or increase `max_iterations`
3. **Poor Parameter Coverage**: Increase `n_initial_samples` or check parameter bounds
4. **GP Model Failures**: Usually resolved automatically with fallback to random sampling

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check convergence history:
```python
for iteration in screening_optimizer.iteration_history:
    print(f"Iteration {iteration['iteration']}: {iteration['convergence']}")
```

## License

This module is part of PyMBO (Python Multi-objective Bayesian Optimization) and follows the same licensing terms as the main software (Creative Commons BY-NC-ND 4.0).