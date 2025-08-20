"""
Configuration file for ABC optimization
"""

# ABC Tool Configuration
ABC_PATH = "/home/qiang/Applications/abc/abc-master/abc"
DESIGN_FILE = "voter.v"
OUTPUT_FILE = "voter_optimized.blif"

# Optimization Parameters
N_TRIALS = 100
TIMEOUT_SECONDS = 3600  # 1 hour
ABC_TIMEOUT_SECONDS = 300  # 5 minutes per ABC run

# Parameter Ranges - Fixed for ABC compatibility
PARAM_RANGES = {
    'balance1_l': (1, 20),      # First balance level
    'resub1_K': (4, 8),         # First resub K (LUT size)
    'resub1_N': (1, 3),         # First resub N (max nodes) - ABC limit is 3
    'resub2_K': (4, 8),         # Second resub K
    'resub2_N': (1, 3),         # Second resub N (max nodes) - ABC limit is 3
    'balance2_l': (1, 20),      # Second balance level
    'if_K': (4, 6)              # Technology mapping K
}

# Validation Constraints
LOGICAL_CONSTRAINTS = {
    'resub1_K_max': 'if_K',     # resub1_K <= if_K
    'resub2_K_max': 'if_K',     # resub2_K <= if_K
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Output Files
FAILED_TRIALS_LOG = "failed_trials.log"
BEST_PARAMETERS_FILE = "best_parameters.json"
BEST_ABC_SCRIPT = "best_abc_script.abc"
OPTIMIZATION_LOG = "optimization.log"

# Optuna Configuration
OPTUNA_SAMPLER = "TPESampler"
OPTUNA_PRUNER = "MedianPruner"
OPTUNA_SEED = 42
