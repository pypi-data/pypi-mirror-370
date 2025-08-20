"""Test NetHack recording with actual NLE backend."""

import time
from pathlib import Path
import matplotlib.pyplot as plt
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper
from src.synth_env.examples.nethack.helpers.trajectory_recorder import TrajectoryRecorder
from src.synth_env.examples.nethack.helpers.visualization.visualizer import NetHackVisualizer


def test_nle_recording():
    """Test recording with real NLE environment."""
    print("=== Testing NLE Recording ===\n")
    
    # Create NLE wrapper
    wrapper = NLEWrapper(character_role="knight")
    
    # Create trajectory recorder
    recorder = TrajectoryRecorder("dev/nle_trajectories")
    trajectory_id = recorder.start_recording("knight", task_id="test_nle")
    
    print(f"Started recording: {trajectory_id}")
    
    # Reset environment
    obs = wrapper.reset()
    recorder.record_step("reset", obs, 0.0, False, {})
    
    # Show initial state
    print(f"Initial position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
    print(f"Message: {obs['message']}")
    print()
    
    # Play some moves
    action_sequence = [
        "wait",
        "north", "north", "east", "east",
        "search", "search",
        "west", "south",
        "inventory",
        "look",
        "northeast", "southeast", "southwest", "northwest",
        "pickup",
        "search",
        "east", "east", "north"
    ]
    
    total_reward = 0.0
    
    for i, action in enumerate(action_sequence):
        print(f"Step {i+1}: {action}")
        
        # Take action
        obs, reward, done, info = wrapper.step(action)
        
        # Record step
        recorder.record_step(action, obs, reward, done, info)
        
        total_reward += reward
        
        # Show state
        stats = obs['player_stats']
        print(f"  Position: ({stats['x']}, {stats['y']}) | HP: {stats['hp']}/{stats['max_hp']}")
        if obs['message'].strip():
            print(f"  Message: {obs['message'].strip()}")
        if reward != 0:
            print(f"  Reward: {reward:+.2f}")
        
        if done:
            print("\nGame ended!")
            break
        
        time.sleep(0.1)  # Small delay
    
    # Close environment
    wrapper.close()
    
    # Stop recording
    final_status = "completed"
    if 'done' in locals() and done:
        msg = obs['message'].lower()
        if 'die' in msg or 'killed' in msg:
            final_status = "died"
    
    recorder.stop_recording(final_status)
    
    # Save trajectory
    filepath = recorder.save_trajectory()
    print(f"\nTrajectory saved to: {filepath}")
    
    # Show summary
    summary = recorder.get_summary()
    print(f"\nRecording summary:")
    print(f"  Total steps: {summary['total_steps']}")
    print(f"  Total reward: {summary['total_reward']:.2f}")
    print(f"  Max depth: {summary['max_depth']}")
    print(f"  Unique actions: {summary['unique_actions']}")
    
    return filepath


def visualize_nle_recording(trajectory_path: str):
    """Visualize NLE recording."""
    print("\n=== Visualizing NLE Recording ===\n")
    
    # Load trajectory
    recorder, metadata, frames = TrajectoryRecorder.load_trajectory(trajectory_path)
    
    print(f"Loaded trajectory: {metadata.trajectory_id}")
    print(f"Total steps: {metadata.total_steps}")
    
    # Create visualizer
    viz = NetHackVisualizer(cell_size=8, font_size=10)
    
    # Create output directory
    output_dir = Path("dev/nle_trajectories/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create frame sequence showing player movement
    print("Creating movement visualization...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # Select 6 frames evenly spaced
    frame_indices = [0, len(frames)//5, 2*len(frames)//5, 
                    3*len(frames)//5, 4*len(frames)//5, len(frames)-1]
    
    for idx, frame_idx in enumerate(frame_indices):
        if frame_idx < len(frames):
            frame = frames[frame_idx]
            img = viz.create_frame_image(frame.observation, include_stats=False)
            
            axes[idx].imshow(img)
            axes[idx].set_title(f"Step {frame.step}: {frame.action}")
            axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / "movement_sequence.png", dpi=150)
    plt.close()
    
    print(f"  Saved movement sequence to {output_dir}")
    
    # 2. Create detailed statistics
    print("Creating detailed statistics...")
    
    # Convert frames
    vis_frames = []
    for frame in frames:
        vis_frames.append({
            'action': frame.action,
            'observation': frame.observation,
            'reward': frame.reward
        })
    
    # Stats plot
    viz.plot_trajectory_stats(vis_frames, str(output_dir / "trajectory_stats.png"))
    
    # Action distribution
    viz.plot_action_distribution(vis_frames, str(output_dir / "action_distribution.png"))
    
    print(f"  Saved statistics to {output_dir}")
    
    # 3. Create ASCII art frames
    print("Creating ASCII art frames...")
    
    # Save a few ASCII maps as text
    ascii_dir = output_dir / "ascii_frames"
    ascii_dir.mkdir(exist_ok=True)
    
    for i in [0, len(frames)//2, len(frames)-1]:
        if i < len(frames):
            frame = frames[i]
            ascii_map = frame.observation.get('ascii_map', '')
            
            with open(ascii_dir / f"frame_{i:04d}.txt", 'w') as f:
                f.write(f"Step {frame.step}: {frame.action}\n")
                f.write(f"Position: {frame.observation['player_stats']['x']}, "
                       f"{frame.observation['player_stats']['y']}\n")
                f.write(f"Message: {frame.observation.get('message', '')}\n")
                f.write("\n" + ascii_map)
    
    print(f"  Saved ASCII frames to {ascii_dir}")
    
    # 4. Try to create animation
    print("Creating animation...")
    try:
        # Use first 30 frames for demo
        demo_frames = vis_frames[:30]
        gif_path = output_dir / "gameplay_demo.gif"
        viz.create_trajectory_video(demo_frames, str(gif_path), fps=3, include_stats=True)
        print(f"  Saved animation to {gif_path}")
    except Exception as e:
        print(f"  Animation creation failed: {e}")
    
    print("\nVisualization complete!")


def main():
    """Run NLE recording test."""
    # Record a game
    trajectory_path = test_nle_recording()
    
    # Visualize the recording
    if trajectory_path:
        visualize_nle_recording(trajectory_path)
    
    print("\n=== Test complete! ===")
    print("\nTo replay interactively:")
    print(f"  python -m src.synth_env.examples.nethack.helpers.visualization.replay_viewer {trajectory_path}")


if __name__ == "__main__":
    main()