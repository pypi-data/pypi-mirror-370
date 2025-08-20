# Moved Files - Legacy/Redundant Scripts

This directory contains files that were moved from the main `agent_demos` directory during cleanup. These files are kept for reference but are no longer part of the core functionality.

## Moved Files

### Evaluation Scripts (Redundant/Outdated)
- **`crafter_quick_evaluation.py`** (1.4KB) - Simple wrapper that just calls the evaluation framework. Functionality is covered by the main evaluation scripts.

- **`crafter_comprehensive_evaluation.py`** (1.7KB) - Alternative evaluation script that duplicates functionality in `crafter_trace_evaluation.py`. The trace evaluation version is more comprehensive.

### Large/Experimental Files
- **`crafter_trace_evaluation.py`** (47KB) - Comprehensive evaluation with trace capture and visualization. While feature-rich, this is a very large file (1473 lines) that extends the framework with trace capture. This functionality could be integrated into the main framework or kept as a separate module.

- **`crafter_evaluation_browser.py`** (4.8KB) - Utility for browsing evaluations and launching the viewer. This is a nice-to-have feature but not core functionality.

### Test Files (To be converted to proper pytest structure)
- **`test_crafter_react_agent.py`** (45KB) - Large test file (1042 lines) that should be converted to proper pytest format. Contains:
  - Agent testing logic
  - Configuration classes  
  - Evaluation functions
  - Should be split into multiple focused test files

## Recommended Next Steps

1. **Convert test file to pytest structure:**
   ```
   tests/
   ├── test_crafter_agent.py          # Core agent functionality tests
   ├── test_crafter_evaluation.py     # Evaluation framework tests  
   ├── test_crafter_config.py         # Configuration tests
   └── conftest.py                    # Shared fixtures
   ```

2. **Consider integrating trace evaluation functionality** into the main framework if needed.

3. **Archive these files** if they're no longer needed after proper test conversion.

## Current Core Files (Kept in main directory)

- `crafter_react_agent.py` - Main agent implementation
- `crafter_evaluation_framework.py` - Core evaluation framework  
- `crafter_evaluation_config.toml` - Configuration
- `README.md` - Documentation

## Migration Date
July 29, 2025 - Cleanup to focus on core functionality and proper test organization. 