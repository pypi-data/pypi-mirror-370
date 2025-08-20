"""Test NetHack ASCII text display - like the real terminal game."""

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper


def format_nethack_display(obs):
    """Format observation as full NetHack terminal display."""
    # Get components
    ascii_map = obs.get('ascii_map', '')
    stats = obs.get('player_stats', {})
    message = obs.get('message', '').strip()
    
    # Split map into lines
    map_lines = ascii_map.split('\n')
    
    # Ensure we have at least 21 lines for the map area
    while len(map_lines) < 21:
        map_lines.append(' ' * 80)
    
    # Format each line to be exactly 80 characters
    for i in range(len(map_lines)):
        if len(map_lines[i]) < 80:
            map_lines[i] = map_lines[i].ljust(80)
        elif len(map_lines[i]) > 80:
            map_lines[i] = map_lines[i][:80]
    
    # Build the display
    display_lines = []
    
    # Line 0: Message (if any)
    if message:
        display_lines.append(message[:79].ljust(80))
    else:
        display_lines.append(' ' * 80)
    
    # Lines 1-21: Map
    for i in range(21):
        if i < len(map_lines):
            display_lines.append(map_lines[i])
        else:
            display_lines.append(' ' * 80)
    
    # Line 22: Status line 1
    status1 = f"Agent the Adventurer    St:{stats.get('strength', 10)} Dx:{stats.get('dexterity', 10)} Co:{stats.get('constitution', 10)} In:{stats.get('intelligence', 10)} Wi:{stats.get('wisdom', 10)} Ch:{stats.get('charisma', 10)} Neutral"
    display_lines.append(status1[:80].ljust(80))
    
    # Line 23: Status line 2
    dlvl = stats.get('depth', 1)
    gold = stats.get('gold', 0)
    hp = stats.get('hp', 10)
    max_hp = stats.get('max_hp', 10)
    pw = stats.get('energy', 0)
    max_pw = stats.get('max_energy', 0)
    ac = stats.get('ac', 10)
    xp = stats.get('experience_level', 1)
    
    status2 = f"Dlvl:{dlvl} ${gold} HP:{hp}({max_hp}) Pw:{pw}({max_pw}) AC:{ac} Xp:{xp}"
    display_lines.append(status2[:80].ljust(80))
    
    # Join all lines
    return '\n'.join(display_lines)


def print_display_with_border(display_text):
    """Print display with a border."""
    print("┌" + "─" * 80 + "┐")
    for line in display_text.split('\n'):
        print(f"│{line}│")
    print("└" + "─" * 80 + "┘")


def main():
    """Show NetHack in ASCII text mode."""
    print("=== NetHack ASCII Terminal Display ===\n")
    
    # Create wrapper
    wrapper = NLEWrapper(character_role="rogue")
    
    # Reset and show initial state
    obs = wrapper.reset()
    
    print("Initial state:")
    display = format_nethack_display(obs)
    print_display_with_border(display)
    
    print("\nPlayer position:", obs['player_stats']['x'], obs['player_stats']['y'])
    print("\nPress Enter to continue...")
    input()
    
    # Play some moves
    actions = [
        ("north", "Moving north"),
        ("north", "Moving north again"),
        ("east", "Moving east"),
        ("search", "Searching for secret doors"),
        ("inventory", "Checking inventory"),
        ("west", "Moving west"),
        ("south", "Moving south"),
        ("look", "Looking around")
    ]
    
    for action, description in actions:
        print(f"\n{description} (action: {action})...")
        obs, reward, done, _ = wrapper.step(action)
        
        display = format_nethack_display(obs)
        print_display_with_border(display)
        
        if reward != 0:
            print(f"\nReward: {reward:+.2f}")
        
        if done:
            print("\nGame Over!")
            break
        
        print("\nPress Enter to continue...")
        input()
    
    # Save final state as text file
    with open("nethack_ascii_example.txt", "w") as f:
        f.write("NetHack ASCII Terminal Display Example\n")
        f.write("=" * 80 + "\n\n")
        f.write("This is how NetHack looks in a terminal:\n\n")
        f.write(display)
        f.write("\n\nLegend:\n")
        f.write("@ - You (the player)\n")
        f.write(". - Floor\n")
        f.write("# - Wall or corridor\n")
        f.write("+ - Closed door\n")
        f.write("< - Stairs up\n")
        f.write("> - Stairs down\n")
        f.write("d - Dog (pet)\n")
        f.write("$ - Gold\n")
        f.write("% - Food\n")
        f.write("! - Potion\n")
        f.write("? - Scroll\n")
        f.write(") - Weapon\n")
        f.write("[ - Armor\n")
    
    print("\nSaved example to nethack_ascii_example.txt")
    
    wrapper.close()


if __name__ == "__main__":
    main()