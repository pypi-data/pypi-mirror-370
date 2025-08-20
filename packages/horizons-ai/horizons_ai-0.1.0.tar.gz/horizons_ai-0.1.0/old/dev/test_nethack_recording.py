"""Test script for NetHack trajectory recording and visualization."""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.synth_env.examples.nethack.helpers.recording_wrapper import RecordingNetHackEnvironment
from src.synth_env.examples.nethack.taskset import NetHackTaskSet
from src.synth_env.examples.nethack.helpers.visualization.visualizer import NetHackVisualizer
from src.synth_env.examples.nethack.helpers.trajectory_recorder import TrajectoryRecorder
from src.synth_env.environment.tools import EnvToolCall
import matplotlib.pyplot as plt


async def test_recording_environment():
    """Test trajectory recording with a simple game."""
    print("=== Testing NetHack Recording Environment ===\n")
    
    # Create task
    taskset = NetHackTaskSet(seed=42)
    task_instance = await taskset.sample_task_instance(
        task_id="explore_dungeon",
        config={
            "character_role": "knight",
            "difficulty": "novice",
            "time_limit": 100
        }
    )
    
    # Create recording environment
    env = RecordingNetHackEnvironment(
        save_dir="dev/test_trajectories",
        auto_record=True
    )
    
    # Start environment
    public_state, private_state = await env.start(task_instance=task_instance)
    
    print(f"Started recording: {env.trajectory_id}")
    print(f"Character: {task_instance.metadata.character_role}")
    print(f"Initial position: {public_state.position}")
    print(f"Message: {public_state.message}\n")
    
    # Play some moves
    actions = [
        "wait", "north", "north", "east", "search", 
        "west", "south", "inventory", "look", "east",
        "north", "northeast", "search", "southwest", "wait"
    ]
    
    for i, action in enumerate(actions):
        print(f"Step {i+1}: {action}")
        
        # Create tool call
        tool_call = EnvToolCall(
            tool="interact",
            args={"action": action}
        )
        
        # Process action
        obs, reward, done, info = await env.process_action([tool_call])
        
        print(f"  Position: {obs.position}")
        print(f"  Message: {obs.message}")
        if reward != 0:
            print(f"  Reward: {reward:+.2f}")
        
        if done:
            print("\nGame ended!")
            break
    
    # Ensure recording is finalized
    if env.is_recording:
        filepath = env.stop_recording()
        print(f"\nRecording saved to: {filepath}")
    
    # Get recording summary
    summary = env.recorder.get_summary()
    print(f"\nRecording summary:")
    print(f"  Total steps: {summary['total_steps']}")
    print(f"  Total reward: {summary['total_reward']:.2f}")
    print(f"  Unique actions: {summary['unique_actions']}")
    print(f"  Actions distribution: {dict(list(summary['actions_distribution'].items())[:5])}...")
    
    return env.trajectory_id


def test_trajectory_loading():
    """Test loading and analyzing a saved trajectory."""
    print("\n=== Testing Trajectory Loading ===\n")
    
    # Find the most recent trajectory
    trajectory_dir = Path("dev/test_trajectories")
    if not trajectory_dir.exists():
        print("No trajectories found. Run recording test first.")
        return None
    
    trajectory_files = list(trajectory_dir.glob("*.trajectory.gz"))
    if not trajectory_files:
        print("No trajectory files found.")
        return None
    
    # Load most recent
    latest_trajectory = max(trajectory_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading trajectory: {latest_trajectory}")
    
    # Load trajectory
    recorder, metadata, frames = TrajectoryRecorder.load_trajectory(str(latest_trajectory))
    
    print(f"\nTrajectory metadata:")
    print(f"  ID: {metadata.trajectory_id}")
    print(f"  Character: {metadata.character_role}")
    print(f"  Total steps: {metadata.total_steps}")
    print(f"  Total reward: {metadata.total_reward:.2f}")
    print(f"  Final status: {metadata.final_status}")
    print(f"  Max depth: {metadata.max_depth_reached}")
    
    # Show first few frames
    print(f"\nFirst 5 frames:")
    for i, frame in enumerate(frames[:5]):
        print(f"  Frame {i}: {frame.action} (reward: {frame.reward:+.2f})")
    
    return str(latest_trajectory)


def test_visualization(trajectory_path: str = None):
    """Test visualization of trajectory."""
    print("\n=== Testing Visualization ===\n")
    
    if trajectory_path is None:
        # Find most recent trajectory
        trajectory_dir = Path("dev/test_trajectories")
        if not trajectory_dir.exists():
            print("No trajectories found.")
            return
        
        trajectory_files = list(trajectory_dir.glob("*.trajectory.gz"))
        if not trajectory_files:
            print("No trajectory files found.")
            return
        
        trajectory_path = str(max(trajectory_files, key=lambda p: p.stat().st_mtime))
    
    # Load trajectory
    recorder, metadata, frames = TrajectoryRecorder.load_trajectory(trajectory_path)
    
    # Create visualizer
    viz = NetHackVisualizer()
    
    # Create output directory
    output_dir = Path("dev/test_trajectories/visualizations")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Create sample frame images
    print("Creating sample frame images...")
    for i in [0, len(frames)//2, len(frames)-1]:
        if i < len(frames):
            frame = frames[i]
            img = viz.create_frame_image(frame.observation, include_stats=True)
            
            plt.figure(figsize=(8, 10))
            plt.imshow(img)
            plt.title(f"Frame {i}: {frame.action}")
            plt.axis('off')
            plt.savefig(output_dir / f"frame_{i}.png", dpi=150, bbox_inches='tight')
            plt.close()
    
    print(f"  Saved frame images to {output_dir}")
    
    # 2. Create trajectory statistics plot
    print("Creating statistics plots...")
    
    # Convert frames for visualizer
    vis_frames = []
    for frame in frames:
        vis_frames.append({
            'action': frame.action,
            'observation': frame.observation,
            'reward': frame.reward
        })
    
    stats_path = output_dir / f"{metadata.trajectory_id}_stats.png"
    viz.plot_trajectory_stats(vis_frames, str(stats_path))
    print(f"  Saved stats to {stats_path}")
    
    # 3. Create action distribution plot
    actions_path = output_dir / f"{metadata.trajectory_id}_actions.png"
    viz.plot_action_distribution(vis_frames, str(actions_path))
    print(f"  Saved action distribution to {actions_path}")
    
    # 4. Create short video/GIF (first 20 frames)
    print("Creating animation (first 20 frames)...")
    try:
        video_frames = vis_frames[:20]  # Limit to 20 frames for quick demo
        video_path = output_dir / f"{metadata.trajectory_id}_demo.gif"
        viz.create_trajectory_video(video_frames, str(video_path), fps=2, include_stats=True)
        print(f"  Saved animation to {video_path}")
    except Exception as e:
        print(f"  Animation creation failed: {e}")
        print("  (This is normal if ffmpeg/pillow is not installed)")
    
    print("\nVisualization complete!")


async def main():
    """Run all tests."""
    # Test 1: Recording
    trajectory_id = await test_recording_environment()
    
    # Test 2: Loading
    trajectory_path = test_trajectory_loading()
    
    # Test 3: Visualization
    if trajectory_path:
        test_visualization(trajectory_path)
    
    print("\n=== All tests complete! ===")
    print("\nTo view a replay interactively, run:")
    print(f"  python -m src.synth_env.examples.nethack.helpers.visualization.replay_viewer dev/test_trajectories/*.trajectory.gz")


if __name__ == "__main__":
    asyncio.run(main())