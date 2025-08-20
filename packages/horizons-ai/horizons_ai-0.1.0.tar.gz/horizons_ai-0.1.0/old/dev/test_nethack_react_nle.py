"""Test NetHack ReAct agent with real NLE backend using GPT-4o-mini."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from synth_ai.zyk import LM
from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper
from src.synth_env.examples.nethack.helpers.trajectory_recorder import TrajectoryRecorder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetHackReActAgentNLE:
    """ReAct agent for playing NetHack with NLE backend."""
    
    def __init__(self, llm: LM, max_turns: int = 500):
        self.llm = llm
        self.max_turns = max_turns
        self.history = []
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "nethack_action",
                    "description": (
                        "Perform an action in NetHack. Available actions:\n"
                        "Movement: north, south, east, west, northeast, northwest, southeast, southwest\n"
                        "Basic: wait, search (use multiple times to find secrets), look, inventory\n"
                        "Items: pickup, drop, eat, drink/quaff, read, wear, wield, apply\n"
                        "Stairs: up (go up <), down (go down >)\n"
                        "Combat: Just move into monsters to attack\n"
                        "Other: kick, open, close, pray\n"
                        "Menu navigation: a-z to select items, escape to cancel"
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The NetHack action to perform"
                            },
                            "reasoning": {
                                "type": "string", 
                                "description": "Brief explanation of why this action"
                            }
                        },
                        "required": ["action", "reasoning"]
                    }
                }
            }
        ]
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the agent."""
        return """You are an expert NetHack player. Your goal is to explore the dungeon, collect gold, and survive as long as possible to maximize your score.

Key strategies:
1. SEARCH thoroughly - Use 'search' action 5-10 times in rooms to find secret doors/passages
2. EXPLORE systematically - Visit all rooms on a level before going down
3. COLLECT gold ($) and items - These give points
4. MANAGE health - Rest with 'wait' when hurt, pray if desperate
5. BE CAUTIOUS - Unknown items might be cursed

Scoring system:
- Gold pieces = 1 point each
- Killing monsters = varies by type
- Going deeper = bonus points
- Death = game over

Think step-by-step:
1. Observe the map and your status
2. Identify threats, items, or unexplored areas  
3. Choose the best action
4. Explain your reasoning

Focus on maximizing score through exploration and gold collection."""

    def _format_observation(self, obs: Dict[str, Any]) -> str:
        """Format NLE observation for the LLM."""
        stats = obs.get('player_stats', {})
        
        # Extract key information
        hp = stats.get('hp', 0)
        max_hp = stats.get('max_hp', 0)
        gold = stats.get('gold', 0)
        score = stats.get('score', 0)
        depth = stats.get('depth', 1)
        x, y = stats.get('x', 0), stats.get('y', 0)
        
        # Get message
        message = obs.get('message', '').strip()
        
        # Get nearby map (focused view)
        ascii_map = obs.get('ascii_map', '')
        map_lines = ascii_map.split('\n')
        
        # Show 11x11 area around player
        nearby_map = []
        for dy in range(-5, 6):
            if 0 <= y + dy < len(map_lines):
                line = map_lines[y + dy]
                start = max(0, x - 5)
                end = min(len(line), x + 6)
                if start < len(line):
                    map_segment = line[start:end].ljust(11)
                    if dy == 0:  # Player's line
                        nearby_map.append(f">{map_segment}<")
                    else:
                        nearby_map.append(f" {map_segment} ")
        
        # Build formatted observation
        formatted = f"""=== NetHack Status ===
Position: ({x}, {y}) on Dungeon Level {depth}
HP: {hp}/{max_hp} | Gold: {gold} | Score: {score}

Map (11x11 area, @ is you):
{chr(10).join(nearby_map)}

Legend: @ = you, . = floor, # = wall, + = door, < = up, > = down, $ = gold, % = food

Last message: {message if message else '(none)'}"""

        # Add warnings
        if hp < max_hp * 0.3:
            formatted += "\n⚠️ WARNING: Low health! Consider resting or praying."
        
        if "hungry" in message.lower():
            formatted += "\n🍖 WARNING: You are hungry! Eat food soon."
            
        # Check inventory
        inv = obs.get('inventory', [])
        if inv:
            formatted += f"\nInventory ({len(inv)} items): "
            formatted += ", ".join([f"{item['letter']}: {item['description']}" for item in inv[:3]])
            if len(inv) > 3:
                formatted += f", ... ({len(inv)-3} more)"
        
        return formatted

    async def get_action(self, obs_text: str) -> tuple[str, str]:
        """Get next action from LLM."""
        try:
            # Keep recent history
            self.history.append({"role": "user", "content": obs_text})
            if len(self.history) > 6:  # Keep last 3 exchanges
                self.history = self.history[-6:]
            
            # Combine history into a single message
            full_message = "\n\n".join([msg["content"] for msg in self.history[-3:]])
            
            response = await self.llm.respond_async(
                system_message=self._create_system_prompt(),
                user_message=full_message,
                tools=self.tools
            )
            
            # Extract tool call
            if hasattr(response, 'role_response') and response.role_response:
                tool_calls = response.role_response.get('tool_calls', [])
                if tool_calls:
                    args = tool_calls[0]['function']['arguments']
                    action = args.get('action', 'wait')
                    reasoning = args.get('reasoning', 'No reasoning provided')
                    
                    # Add assistant response to history
                    self.history.append({
                        "role": "assistant",
                        "content": f"Action: {action}\nReasoning: {reasoning}"
                    })
                    
                    return action, reasoning
            
            return 'wait', 'No valid action returned'
            
        except Exception as e:
            logger.error(f"Error getting action: {e}")
            return 'wait', f'Error: {e}'

    async def play_game(self, character_role: str = "valkyrie", record: bool = True) -> Dict[str, Any]:
        """Play one game of NetHack."""
        wrapper = NLEWrapper(character_role=character_role)
        recorder = None
        
        if record:
            recorder = TrajectoryRecorder("dev/nethack_react_trajectories")
            recorder.start_recording(character_role, task_id="react_gpt4_mini")
        
        # Game statistics
        stats = {
            'character_role': character_role,
            'max_depth': 1,
            'max_score': 0,
            'total_reward': 0,
            'turns': 0,
            'gold_collected': 0,
            'final_message': '',
            'death_reason': None,
            'actions_taken': {}
        }
        
        try:
            # Reset game
            obs = wrapper.reset()
            if recorder:
                recorder.record_step("reset", obs, 0.0, False, {})
            
            # Initial status
            logger.info(f"Starting as {character_role}")
            logger.info(f"Initial position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
            
            # Clear history for new game
            self.history = []
            
            # Game loop
            for turn in range(self.max_turns):
                stats['turns'] = turn + 1
                
                # Format observation
                obs_text = self._format_observation(obs)
                
                # Get action from LLM
                action, reasoning = await self.get_action(obs_text)
                
                # Log decision
                if turn % 10 == 0:  # Log every 10 turns
                    logger.info(f"Turn {turn+1}: {action} - {reasoning[:50]}...")
                
                # Track actions
                stats['actions_taken'][action] = stats['actions_taken'].get(action, 0) + 1
                
                # Execute action
                obs, reward, done, info = wrapper.step(action)
                
                if recorder:
                    recorder.record_step(action, obs, reward, done, info)
                
                # Update stats
                current_stats = obs['player_stats']
                stats['max_depth'] = max(stats['max_depth'], current_stats.get('depth', 1))
                stats['max_score'] = max(stats['max_score'], current_stats.get('score', 0))
                stats['total_reward'] += reward
                stats['gold_collected'] = current_stats.get('gold', 0)
                
                # Check for death
                if done:
                    stats['final_message'] = obs.get('message', '')
                    if 'die' in stats['final_message'].lower():
                        stats['death_reason'] = 'died'
                    logger.info(f"Game ended at turn {turn+1}: {stats['final_message']}")
                    break
                
                # Periodic status
                if turn % 50 == 0:
                    logger.info(f"Status - Depth: {current_stats.get('depth', 1)}, "
                              f"Score: {current_stats.get('score', 0)}, "
                              f"HP: {current_stats.get('hp', 0)}/{current_stats.get('max_hp', 0)}")
            
            # Timeout
            if stats['turns'] >= self.max_turns:
                stats['death_reason'] = 'timeout'
                logger.info("Game ended due to turn limit")
        
        except Exception as e:
            logger.error(f"Error during game: {e}")
            stats['error'] = str(e)
        
        finally:
            wrapper.close()
            
            if recorder:
                recorder.stop_recording(stats.get('death_reason', 'completed'))
                trajectory_file = recorder.save_trajectory()
                stats['trajectory_file'] = trajectory_file
                logger.info(f"Saved trajectory to {trajectory_file}")
        
        return stats


async def main():
    """Run GPT-4o-mini on NetHack."""
    logger.info("=== NetHack ReAct Agent with GPT-4o-mini ===")
    
    # Initialize LLM
    llm = LM(model_name="gpt-4o-mini", formatting_model_name="gpt-4o-mini", temperature=0.7)
    agent = NetHackReActAgentNLE(llm, max_turns=300)
    
    # Run multiple games
    num_games = 3
    all_results = []
    
    characters = ["valkyrie", "wizard", "tourist"]  # Different starting conditions
    
    for i in range(num_games):
        character = characters[i % len(characters)]
        logger.info(f"\n=== Game {i+1}/{num_games}: {character} ===")
        
        result = await agent.play_game(character_role=character, record=True)
        all_results.append(result)
        
        # Report game result
        logger.info(f"Game {i+1} completed:")
        logger.info(f"  Character: {character}")
        logger.info(f"  Final Score: {result['max_score']}")
        logger.info(f"  Max Depth: {result['max_depth']}")
        logger.info(f"  Turns: {result['turns']}")
        logger.info(f"  Gold: {result['gold_collected']}")
        logger.info(f"  Total Reward: {result['total_reward']:.1f}")
        logger.info(f"  Death: {result.get('death_reason', 'survived')}")
        
        # Short break between games
        await asyncio.sleep(2)
    
    # Summary statistics
    print("\n" + "="*60)
    print("FINAL RESULTS - GPT-4o-mini on NetHack")
    print("="*60)
    
    scores = [r['max_score'] for r in all_results]
    depths = [r['max_depth'] for r in all_results]
    turns = [r['turns'] for r in all_results]
    rewards = [r['total_reward'] for r in all_results]
    
    print(f"Games played: {num_games}")
    print(f"Average score: {sum(scores)/len(scores):.1f} (max: {max(scores)}, min: {min(scores)})")
    print(f"Average depth: {sum(depths)/len(depths):.1f} (max: {max(depths)})")
    print(f"Average turns: {sum(turns)/len(turns):.1f}")
    print(f"Average reward: {sum(rewards)/len(rewards):.1f}")
    print(f"Death rate: {sum(1 for r in all_results if r.get('death_reason') == 'died')}/{num_games}")
    
    # Action distribution
    all_actions = {}
    for result in all_results:
        for action, count in result['actions_taken'].items():
            all_actions[action] = all_actions.get(action, 0) + count
    
    print("\nTop 10 actions taken:")
    for action, count in sorted(all_actions.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {action}: {count}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"dev/nethack_gpt4_mini_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'model': 'gpt-4o-mini',
            'num_games': num_games,
            'games': all_results,
            'summary': {
                'avg_score': sum(scores)/len(scores),
                'max_score': max(scores),
                'avg_depth': sum(depths)/len(depths),
                'avg_turns': sum(turns)/len(turns),
                'avg_reward': sum(rewards)/len(rewards),
                'action_distribution': all_actions
            }
        }, f, indent=2)
    
    print(f"\nDetailed results saved to {results_file}")


if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    asyncio.run(main())