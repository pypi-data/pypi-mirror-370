# NetHack Development Scripts Archive

This directory contains development files, debug scripts, evaluation results, and documentation that were moved from the NetHack implementation during cleanup.

## 📁 Archived Files

### Development Documentation
- **`plan.txt`** (20KB) - Original integration plan for NetHack into synth-env framework
- **`IMPLEMENTATION_SUMMARY.md`** (2.9KB) - Summary of implementation changes and design decisions
- **`NETHACK_EVAL_UPGRADE_PLAN.md`** (10KB) - Evaluation framework upgrade planning document
- **`balrg_scoring.txt`** (9.3KB) - Detailed BALROG scoring system documentation

### Debug and Development Scripts
- **`debug_single_rollout.py`** (14KB) - Comprehensive debug script for single NetHack episodes
- **`simple_debug.py`** (3.5KB) - Simple debugging utilities

### Evaluation Results
- **`nethack_eval_results_*.json`** (6 files, ~38KB total) - Historical evaluation results with timestamps
- **`nethack_react_results.json`** (180KB) - Large comprehensive evaluation results file

### Debug Prompt Dumps
- **`nethack_prompt_turn_*.txt`** (11 files, ~90KB total) - LLM prompt debugging files
  - Turn-by-turn prompt dumps for debugging agent behavior
  - System prompts and user messages for each game turn

## 🎯 Purpose

These files were primarily used for:
- **Research and Development**: Planning and implementing the NetHack integration
- **Debugging**: Understanding agent behavior and prompt engineering
- **Evaluation History**: Tracking performance across different model versions
- **Documentation**: Detailed technical specifications and scoring systems

## 📊 Key Insights from Archived Data

### BALROG Scoring System
The `balrg_scoring.txt` file contains comprehensive documentation of the BALROG benchmark scoring system:
- **BALROG Rewards**: Per-step shaped rewards for training (score deltas, gold collection, depth progression)
- **BALROG Score**: Official leaderboard metric (0-100%) based on milestone achievements
- **Current SOTA**: ~1-2% on the official metric (NetHack is extremely challenging!)

### Evaluation Results
Historical evaluation data shows:
- Success rates typically very low (0-5%) - NetHack is notoriously difficult
- Most runs end in timeout rather than death or completion
- Depth progression and experience gains are key metrics
- Agent behavior debugging through prompt analysis

### Debug Insights
The prompt dumps reveal:
- Detailed system prompts with 80+ action specifications
- Turn-by-turn decision making process
- Common failure patterns and error handling

## 🚀 Usage

If you need to reference these files:

```bash
# View BALROG scoring documentation
cat balrg_scoring.txt

# Analyze historical evaluation results
jq '.evaluation_summary' nethack_eval_results_*.json

# Review debug prompts
head -50 nethack_prompt_turn_1.txt

# Run debug script (may need path updates)
python debug_single_rollout.py
```

## 📝 Notes

- These files were moved to reduce clutter in the main NetHack directory
- They contain valuable historical context and debugging information
- Some import paths may need updating if you want to use scripts again
- The main production files are in `src/synth_env/examples/nethack/`
- Large JSON files contain detailed trajectory data for analysis

## 🔄 Restoration

To restore any of these files to the main directory:

```bash
# From the main nethack directory
cp ../../../../old/nethack_development_scripts/FILENAME .
```

## 🧠 Learning from the Archive

Key lessons from the development process:
1. **NetHack Complexity**: The game's difficulty is reflected in low success rates
2. **Prompt Engineering**: Extensive system prompts needed for action space clarity
3. **BALROG Integration**: Proper scoring requires understanding milestone-based evaluation
4. **Debug Importance**: Turn-by-turn analysis crucial for understanding agent failures
5. **State Management**: Complex game state requires careful serialization handling

These archived files represent the iterative development process and valuable debugging insights for future NetHack agent development! 