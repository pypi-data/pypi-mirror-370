"""Test what rewards NLE provides by default."""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper
import nle
from nle import nethack


def test_nle_rewards():
    """Test NLE reward signals."""
    print("=== Testing NLE Reward Signals ===\n")
    
    # Create wrapper
    wrapper = NLEWrapper(character_role="valkyrie")
    
    # Track rewards
    total_reward = 0.0
    reward_events = []
    
    # Reset
    obs = wrapper.reset()
    print(f"Starting position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
    print(f"Starting gold: {obs['player_stats']['gold']}")
    print(f"Starting score: {obs['player_stats']['score']}")
    print("\n")
    
    # Test various actions that might give rewards
    test_sequences = [
        # Basic movement
        ("Basic movement", ["north", "south", "east", "west"]),
        
        # Exploration
        ("Exploration", ["north", "north", "north", "east", "east"]),
        
        # Searching (might find things)
        ("Searching", ["search", "search", "search", "search", "search"]),
        
        # More exploration
        ("Deep exploration", ["north", "north", "east", "east", "south", "south"]),
        
        # Waiting
        ("Waiting", ["wait", "wait", "wait", "wait", "wait"]),
    ]
    
    step_count = 0
    
    for sequence_name, actions in test_sequences:
        print(f"\n{sequence_name}:")
        print("-" * 40)
        
        for action in actions:
            obs, reward, done, info = wrapper.step(action)
            step_count += 1
            total_reward += reward
            
            # Track non-zero rewards
            if reward != 0:
                stats = obs['player_stats']
                reward_events.append({
                    'step': step_count,
                    'action': action,
                    'reward': reward,
                    'position': (stats['x'], stats['y']),
                    'gold': stats['gold'],
                    'score': stats['score'],
                    'message': obs.get('message', '').strip()
                })
                
                print(f"  Step {step_count}: {action} -> REWARD: {reward:+.2f}")
                print(f"    Position: ({stats['x']}, {stats['y']})")
                print(f"    Gold: {stats['gold']}, Score: {stats['score']}")
                if obs.get('message', '').strip():
                    print(f"    Message: {obs['message'].strip()}")
            
            if done:
                print("\nGame ended!")
                break
        
        if done:
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("REWARD SUMMARY")
    print("=" * 60)
    print(f"Total steps: {step_count}")
    print(f"Total reward: {total_reward:+.2f}")
    print(f"Average reward per step: {total_reward/step_count if step_count > 0 else 0:.4f}")
    print(f"Number of reward events: {len(reward_events)}")
    
    if reward_events:
        print("\nReward events:")
        for event in reward_events:
            print(f"  Step {event['step']}: {event['action']} -> {event['reward']:+.2f}")
            if event['message']:
                print(f"    '{event['message']}'")
    
    # Test specific reward scenarios
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC REWARD SCENARIOS")
    print("=" * 60)
    
    # Reset for new tests
    wrapper.close()
    wrapper = NLEWrapper(character_role="rogue")
    obs = wrapper.reset()
    
    print("\n1. Testing gold pickup:")
    # Rogues often start near gold
    for _ in range(10):
        obs, reward, done, _ = wrapper.step("north")
        if reward > 0:
            print(f"  Got reward: {reward:+.2f}")
            print(f"  Gold: {obs['player_stats']['gold']}")
            break
    
    # Check NLE's default reward function
    print("\n2. Checking NLE's scoring system:")
    print(f"  Current score: {obs['player_stats']['score']}")
    print(f"  Current gold: {obs['player_stats']['gold']}")
    print(f"  Experience points: {obs['player_stats']['experience_points']}")
    
    wrapper.close()
    
    # Create raw NLE environment to check reward function
    print("\n3. Checking raw NLE environment:")
    env = nle.env.NLE()
    obs = env.reset()
    
    # The default NLE uses score-based rewards
    print("  NLE default configuration:")
    print(f"    Reward type: Score-based (delta in game score)")
    print(f"    Initial score: {obs['blstats'][nethack.NLE_BL_SCORE]}")
    
    # Take a few steps
    for _ in range(5):
        obs, reward, done, _ = env.step(0)  # Move north
        if reward != 0:
            print(f"    Got reward: {reward}, Score: {obs['blstats'][nethack.NLE_BL_SCORE]}")
    
    env.close()
    
    print("\n=== Summary ===")
    print("NLE provides rewards based on:")
    print("1. Score changes (default) - picking up gold, killing monsters, etc.")
    print("2. The reward is the delta in score between steps")
    print("3. Score increases from:")
    print("   - Picking up gold (1 point per gold piece)")
    print("   - Killing monsters (varies by monster)")
    print("   - Descending dungeon levels")
    print("   - Finding items")
    print("   - Other achievements")


if __name__ == "__main__":
    test_nle_rewards()