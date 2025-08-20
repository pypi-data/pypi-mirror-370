"""Interactive NLE test - step through the game manually."""

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper

def show_game_state(obs):
    """Display current game state."""
    print("\n" + "="*80)
    print(f"Message: {obs['message']}")
    print(f"Position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
    print(f"HP: {obs['player_stats']['hp']}/{obs['player_stats']['max_hp']}  "
          f"Level: {obs['player_stats']['experience_level']}  "
          f"Depth: {obs['player_stats']['depth']}  "
          f"Gold: {obs['player_stats']['gold']}  "
          f"AC: {obs['player_stats']['ac']}")
    
    # Show map with highlighted player position
    print("\n--- Map ---")
    lines = obs['ascii_map'].split('\n')
    px, py = obs['player_stats']['x'], obs['player_stats']['y']
    
    # Show area around player (11x11)
    for y in range(max(0, py-5), min(len(lines), py+6)):
        if 0 <= y < len(lines):
            line = lines[y]
            if y == py:
                # Highlight player row
                if 0 <= px < len(line):
                    # Add brackets around player
                    before = line[max(0, px-15):px]
                    player = line[px] if px < len(line) else ' '
                    after = line[px+1:min(len(line), px+16)]
                    print(f">>> {before}[{player}]{after} <<<")
                else:
                    print(f">>> {line[max(0, px-15):min(len(line), px+16)]} <<<")
            else:
                # Normal row
                print(f"    {line[max(0, px-15):min(len(line), px+16)]}")
    
    # Show inventory count
    if obs.get('inventory'):
        print(f"\nInventory items: {len(obs['inventory'])}")
    
    # Show if in menu
    if obs.get('in_menu'):
        print("\n!!! IN MENU !!!")
        if obs.get('menu_text'):
            for line in obs['menu_text']:
                print(f"  {line}")

def main():
    print("=== NetHack Interactive Test ===")
    print("Commands:")
    print("  Movement: n/north, s/south, e/east, w/west, ne, nw, se, sw")
    print("  Actions: wait, search, look, inventory/i, pickup/p, drop/d")
    print("  Items: eat, drink/quaff, read, wear, wield, takeoff")
    print("  Other: open, close, kick, pray, up, down")
    print("  Menu: a-z (select item), escape/esc (cancel)")
    print("  Special: quit (end test)")
    print("\nType 'help' to see this again\n")
    
    # Create wrapper
    wrapper = NLEWrapper(character_role="monk")  # Start as monk
    
    # Reset
    obs = wrapper.reset()
    show_game_state(obs)
    
    # Command shortcuts
    shortcuts = {
        'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
        'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest',
        'i': 'inventory', 'p': 'pickup', 'd': 'drop',
        'esc': 'escape', '?': 'help'
    }
    
    # Main game loop
    done = False
    turn = 0
    total_reward = 0.0
    
    while not done:
        # Get user input
        cmd = input(f"\nTurn {turn} > ").strip().lower()
        
        if cmd == 'quit':
            print("Ending test...")
            break
        elif cmd == 'help' or cmd == '?':
            print("\nCommands:")
            print("  Movement: n/north, s/south, e/east, w/west, ne, nw, se, sw")
            print("  Actions: wait, search, look, inventory/i, pickup/p, drop/d")
            print("  Items: eat, drink/quaff, read, wear, wield, takeoff")
            print("  Other: open, close, kick, pray, up, down")
            print("  Menu: a-z (select item), escape/esc (cancel)")
            print("  Info: stats (show detailed stats)")
            continue
        elif cmd == 'stats':
            print("\n--- Detailed Stats ---")
            stats = obs['player_stats']
            print(f"STR: {stats['strength']} ({stats['strength_pct']}%)")
            print(f"DEX: {stats['dexterity']}")
            print(f"CON: {stats['constitution']}")
            print(f"INT: {stats['intelligence']}")
            print(f"WIS: {stats['wisdom']}")
            print(f"CHA: {stats['charisma']}")
            print(f"Score: {stats['score']}")
            print(f"XP: {stats['experience_points']}")
            print(f"Time: {stats['time']}")
            print(f"Hunger: {stats['hunger_state']}")
            continue
        
        # Expand shortcuts
        action = shortcuts.get(cmd, cmd)
        
        # Check if valid action
        if action not in wrapper.get_valid_actions():
            print(f"Unknown action: '{action}'")
            print(f"Valid actions include: {', '.join(wrapper.get_valid_actions()[:15])}...")
            continue
        
        # Take action
        try:
            obs, reward, done, info = wrapper.step(action)
            turn += 1
            total_reward += reward
            
            # Show result
            show_game_state(obs)
            if reward != 0:
                print(f"\nReward: {reward:+.2f} (Total: {total_reward:+.2f})")
            
            # Handle special messages
            msg = obs['message'].lower()
            if '--more--' in msg:
                print("(Press space or enter to continue...)")
                obs, _, done, _ = wrapper.step('space')
                print(f"Continued: {obs['message']}")
            elif 'really quit' in msg:
                print("(Confirm quit with 'y' or cancel with 'n')")
            elif done:
                print("\n*** GAME OVER ***")
                if 'die' in msg:
                    print("You died!")
                print(f"Final score: {obs['player_stats']['score']}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup
    wrapper.close()
    print("\n=== Test Complete ===")
    print(f"Total turns: {turn}")
    print(f"Total reward: {total_reward:+.2f}")

if __name__ == "__main__":
    main()