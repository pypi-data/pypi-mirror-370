# MiniGrid Development Scripts Archive

This directory contains development and testing scripts that were moved from the main MiniGrid agent demos directory during cleanup.

## 📁 Archived Files

### Testing and Development Scripts
- **`demo_results_table.py`** (7.2KB) - Mock results demonstration showing expected evaluation output format
- **`simple_test.py`** (3.3KB) - Component testing for evaluation framework functions
- **`test_eval_framework.py`** (719B) - Quick test for the evaluation framework
- **`standalone_test.py`** (4.2KB) - Standalone testing without dependencies
- **`success_rate_demo.py`** (2.0KB) - Success rate calculation demonstration

## 🎯 Purpose

These scripts were primarily used for:
- **Development testing**: Verifying framework components work correctly
- **Mock data generation**: Creating example outputs for documentation
- **Isolated testing**: Testing specific functionality without full evaluations
- **Debugging**: Understanding framework behavior during development

## 🚀 Usage

If you need to reference these scripts:

```bash
# Run component tests
python simple_test.py

# Test evaluation framework
python test_eval_framework.py

# Generate mock results table
python demo_results_table.py
```

## 📝 Notes

- These scripts were moved to reduce clutter in the main agent demos directory
- They contain useful patterns for testing and development
- Some import paths may need updating if you want to use them again
- The main production scripts are in `src/synth_env/examples/minigrid/agent_demos/`

## 🔄 Restoration

To restore any of these scripts to the main directory:

```bash
# From the main agent_demos directory
cp ../../../../../old/minigrid_development_scripts/SCRIPT_NAME.py .
```

Remember to update import paths if needed! 