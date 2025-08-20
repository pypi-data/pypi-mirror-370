"""Show NetHack ASCII display without interaction."""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper


def format_nethack_display(obs):
    """Format observation as full NetHack terminal display."""
    # Get components
    ascii_map = obs.get('ascii_map', '')
    stats = obs.get('player_stats', {})
    message = obs.get('message', '').strip()
    
    # Split map into lines
    map_lines = ascii_map.split('\n')
    
    # Build the display
    display_lines = []
    
    # Add message if present
    if message:
        display_lines.append(message)
    
    # Add map (first 21 lines)
    for i in range(min(21, len(map_lines))):
        display_lines.append(map_lines[i])
    
    # Add separator
    display_lines.append("-" * 80)
    
    # Add status lines
    status1 = f"Agent the Adventurer    St:{stats.get('strength', 10)} Dx:{stats.get('dexterity', 10)} Co:{stats.get('constitution', 10)} In:{stats.get('intelligence', 10)} Wi:{stats.get('wisdom', 10)} Ch:{stats.get('charisma', 10)} Neutral"
    display_lines.append(status1)
    
    dlvl = stats.get('depth', 1)
    gold = stats.get('gold', 0)
    hp = stats.get('hp', 10)
    max_hp = stats.get('max_hp', 10)
    pw = stats.get('energy', 0)
    max_pw = stats.get('max_energy', 0)
    ac = stats.get('ac', 10)
    xp = stats.get('experience_level', 1)
    
    status2 = f"Dlvl:{dlvl}  $:{gold}  HP:{hp}({max_hp})  Pw:{pw}({max_pw})  AC:{ac}  Xp:{xp}/1"
    display_lines.append(status2)
    
    return '\n'.join(display_lines)


def main():
    """Show NetHack ASCII displays."""
    print("=== NetHack ASCII Terminal Display ===\n")
    
    # Create wrapper
    wrapper = NLEWrapper(character_role="wizard")
    
    # Show initial state
    obs = wrapper.reset()
    print("INITIAL STATE:")
    print("=" * 80)
    print(format_nethack_display(obs))
    print("=" * 80)
    
    # Play a few moves to show different states
    print("\n\nAFTER MOVING NORTH 3 TIMES:")
    print("=" * 80)
    for _ in range(3):
        obs, _, _, _ = wrapper.step("north")
    print(format_nethack_display(obs))
    print("=" * 80)
    
    # More exploration
    print("\n\nAFTER EXPLORING EAST:")
    print("=" * 80)
    for _ in range(5):
        obs, _, _, _ = wrapper.step("east")
    print(format_nethack_display(obs))
    print("=" * 80)
    
    # Show with a message
    print("\n\nAFTER SEARCHING (with message):")
    print("=" * 80)
    obs, _, _, _ = wrapper.step("search")
    obs, _, _, _ = wrapper.step("search")
    obs, _, _, _ = wrapper.step("look")
    print(format_nethack_display(obs))
    print("=" * 80)
    
    # Save examples to file
    with open("dev/nethack_ascii_examples.txt", "w") as f:
        f.write("NetHack ASCII Terminal Examples\n")
        f.write("==============================\n\n")
        
        # Reset for clean examples
        obs = wrapper.reset()
        f.write("Example 1: Starting Position\n")
        f.write("-" * 80 + "\n")
        f.write(format_nethack_display(obs))
        f.write("\n\n")
        
        # Move around
        for _ in range(3):
            obs, _, _, _ = wrapper.step("north")
        for _ in range(3):
            obs, _, _, _ = wrapper.step("east")
        
        f.write("Example 2: After Movement\n")
        f.write("-" * 80 + "\n")
        f.write(format_nethack_display(obs))
        f.write("\n\n")
        
        f.write("ASCII Character Reference:\n")
        f.write("-" * 80 + "\n")
        f.write("@     - You (the player)\n")
        f.write(".     - Floor/ground\n")
        f.write("#     - Wall or corridor\n")
        f.write("-|    - Wall sections\n")
        f.write("+     - Closed door\n")
        f.write("<     - Stairs up\n")
        f.write(">     - Stairs down\n")
        f.write("d     - Dog (pet)\n")
        f.write("f     - Cat (pet)\n")
        f.write("u     - Pony (pet)\n")
        f.write("$     - Gold pieces\n")
        f.write("%     - Food/comestible\n")
        f.write("!     - Potion\n")
        f.write("?     - Scroll\n")
        f.write("/     - Wand\n")
        f.write("=     - Ring\n")
        f.write("\"     - Amulet\n")
        f.write(")     - Weapon\n")
        f.write("[     - Armor\n")
        f.write("(     - Tool\n")
        f.write("*     - Gem or rock\n")
        f.write("`     - Boulder or statue\n")
        f.write("^     - Trap\n")
        f.write("{     - Fountain\n")
        f.write("}     - Pool/moat\n")
        f.write("\\     - Throne\n")
        f.write("_     - Altar\n")
    
    print("\nSaved examples to dev/nethack_ascii_examples.txt")
    
    wrapper.close()


if __name__ == "__main__":
    main()