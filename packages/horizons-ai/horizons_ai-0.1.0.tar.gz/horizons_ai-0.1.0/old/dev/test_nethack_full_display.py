"""Test full NetHack display visualization."""

import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper
from src.synth_env.examples.nethack.helpers.trajectory_recorder import TrajectoryRecorder
from src.synth_env.examples.nethack.helpers.visualization.visualizer import NetHackVisualizer


def test_full_display():
    """Test creating full NetHack terminal display."""
    print("=== Testing Full NetHack Display ===\n")
    
    # Create larger visualizer for better display
    viz = NetHackVisualizer(cell_size=10, font_size=12)
    
    # Create NLE wrapper
    wrapper = NLEWrapper(character_role="valkyrie")
    
    # Reset and get initial observation
    obs = wrapper.reset()
    
    # Add some extra info for display
    obs['character_name'] = "Agent"
    obs['character_role'] = "Valkyrie"
    obs['turn_count'] = 0
    
    print(f"Initial position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
    print(f"Message: {obs['message']}")
    
    # Create initial frame
    img = viz.create_frame_image(obs, include_stats=True)
    
    # Save initial state
    output_dir = Path("dev/nethack_display_test")
    output_dir.mkdir(exist_ok=True)
    
    plt.figure(figsize=(16, 12))
    plt.imshow(img)
    plt.title("NetHack - Initial State")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_dir / "nethack_initial.png", dpi=150, bbox_inches='tight', facecolor='black')
    plt.close()
    
    print(f"\nSaved initial display to {output_dir}/nethack_initial.png")
    
    # Play a few moves and capture states
    actions = ["north", "north", "east", "search", "west", "south"]
    
    for i, action in enumerate(actions):
        obs, reward, done, _ = wrapper.step(action)
        obs['character_name'] = "Agent"
        obs['character_role'] = "Valkyrie"
        obs['turn_count'] = i + 1
        
        print(f"\nStep {i+1}: {action}")
        print(f"Position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
        if obs['message'].strip():
            print(f"Message: {obs['message'].strip()}")
        
        # Create frame
        img = viz.create_frame_image(obs, include_stats=True)
        
        # Save frame
        plt.figure(figsize=(16, 12))
        plt.imshow(img)
        plt.title(f"NetHack - Step {i+1}: {action}")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_dir / f"nethack_step_{i+1:02d}.png", dpi=150, bbox_inches='tight', facecolor='black')
        plt.close()
        
        if done:
            break
    
    # Create a comparison figure
    print("\nCreating comparison figure...")
    
    # Reset for fresh game
    obs = wrapper.reset()
    obs['character_name'] = "Agent"
    obs['character_role'] = "Valkyrie"
    obs['turn_count'] = 0
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 15))
    fig.patch.set_facecolor('black')
    
    # Show different game states
    states = []
    
    # State 1: Initial
    img1 = viz.create_frame_image(obs, include_stats=True)
    states.append((img1, "Initial State"))
    
    # State 2: After exploration
    for _ in range(5):
        obs, _, _, _ = wrapper.step("north")
    for _ in range(5):
        obs, _, _, _ = wrapper.step("east")
    obs['turn_count'] = 10
    img2 = viz.create_frame_image(obs, include_stats=True)
    states.append((img2, "After Exploration"))
    
    # State 3: After searching
    for _ in range(3):
        obs, _, _, _ = wrapper.step("search")
    obs['turn_count'] = 13
    img3 = viz.create_frame_image(obs, include_stats=True)
    states.append((img3, "After Searching"))
    
    # State 4: Return journey
    for _ in range(3):
        obs, _, _, _ = wrapper.step("west")
    for _ in range(3):
        obs, _, _, _ = wrapper.step("south")
    obs['turn_count'] = 19
    img4 = viz.create_frame_image(obs, include_stats=True)
    states.append((img4, "Return Journey"))
    
    # Plot all states
    for idx, (ax, (img, title)) in enumerate(zip(axes.flat, states)):
        ax.imshow(img)
        ax.set_title(title, color='white', fontsize=14, pad=10)
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / "nethack_states_comparison.png", dpi=150, bbox_inches='tight', facecolor='black')
    plt.close()
    
    print(f"Saved comparison figure to {output_dir}/nethack_states_comparison.png")
    
    # Close wrapper
    wrapper.close()
    
    print("\n=== Test Complete ===")
    print(f"All images saved to {output_dir}/")


if __name__ == "__main__":
    test_full_display()