"""Automated NLE test - demonstrate various actions."""

from src.synth_env.examples.nethack.helpers.nle_wrapper import NLEWrapper
import time

def show_state(obs, action_taken=None):
    """Display game state."""
    print("\n" + "="*60)
    if action_taken:
        print(f"Action taken: {action_taken}")
    print(f"Message: {obs['message']}")
    print(f"Position: ({obs['player_stats']['x']}, {obs['player_stats']['y']})")
    print(f"HP: {obs['player_stats']['hp']}/{obs['player_stats']['max_hp']}  "
          f"Level: {obs['player_stats']['experience_level']}  "
          f"Gold: {obs['player_stats']['gold']}")
    
    # Show small map section
    lines = obs['ascii_map'].split('\n')
    px, py = obs['player_stats']['x'], obs['player_stats']['y']
    print("\nMap around player:")
    for y in range(max(0, py-2), min(len(lines), py+3)):
        if 0 <= y < len(lines):
            line = lines[y]
            start = max(0, px-5)
            end = min(len(line), px+6)
            if y == py:
                print(f"  >> {line[start:end]} <<")
            else:
                print(f"     {line[start:end]}")

def main():
    print("=== Automated NetHack Test ===")
    
    # Test 1: Basic movement
    print("\n\n### TEST 1: Basic Movement ###")
    wrapper = NLEWrapper(character_role="knight")
    obs = wrapper.reset()
    show_state(obs, "RESET")
    
    # Try each direction
    movements = ["wait", "north", "east", "south", "west", "northeast", "southeast", "southwest", "northwest"]
    for move in movements:
        obs, reward, done, _ = wrapper.step(move)
        show_state(obs, move)
        if done:
            print("Game ended!")
            break
        time.sleep(0.5)  # Small delay to see output
    
    wrapper.close()
    
    # Test 2: Inventory and items
    print("\n\n### TEST 2: Inventory Management ###")
    wrapper = NLEWrapper(character_role="tourist")  # Tourist has more items
    obs = wrapper.reset()
    show_state(obs, "RESET as tourist")
    
    # Check inventory
    obs, _, _, _ = wrapper.step("inventory")
    show_state(obs, "inventory")
    
    if obs['inventory']:
        print("\nInventory contents:")
        for i, item in enumerate(obs['inventory'][:5]):  # Show first 5
            print(f"  {item['letter']}: {item['description']}")
    
    # Drop an item (if we have any)
    if obs['inventory'] and len(obs['inventory']) > 2:
        obs, _, _, _ = wrapper.step("drop")
        show_state(obs, "drop")
        
        # If menu appears, select first droppable item
        if obs.get('in_menu'):
            print("Drop menu appeared!")
            # Drop the first item (usually 'a')
            obs, _, _, _ = wrapper.step("a")
            show_state(obs, "selected 'a' to drop")
    
    wrapper.close()
    
    # Test 3: Searching and interacting
    print("\n\n### TEST 3: Search and Interact ###")
    wrapper = NLEWrapper(character_role="monk")
    obs = wrapper.reset()
    show_state(obs, "RESET as monk")
    
    # Search multiple times
    for i in range(3):
        obs, _, _, _ = wrapper.step("search")
        show_state(obs, f"search #{i+1}")
        time.sleep(0.3)
    
    # Try to pick up if something is here
    obs, _, _, _ = wrapper.step("pickup")
    show_state(obs, "pickup")
    
    # Look around
    obs, _, _, _ = wrapper.step("look")
    show_state(obs, "look")
    
    wrapper.close()
    
    # Test 4: Menu navigation
    print("\n\n### TEST 4: Menu Navigation ###")
    wrapper = NLEWrapper(character_role="wizard")
    obs = wrapper.reset()
    show_state(obs, "RESET as wizard")
    
    # Open inventory
    obs, _, _, _ = wrapper.step("inventory")
    show_state(obs, "inventory")
    
    # Try to read something (wizards start with spellbooks)
    obs, _, _, _ = wrapper.step("read")
    show_state(obs, "read")
    
    if obs.get('in_menu'):
        print("\nRead menu appeared! Canceling with escape...")
        obs, _, _, _ = wrapper.step("escape")
        show_state(obs, "escape from menu")
    
    wrapper.close()
    
    # Test 5: Combat test
    print("\n\n### TEST 5: Finding Combat ###")
    wrapper = NLEWrapper(character_role="barbarian")  # Good fighter
    obs = wrapper.reset()
    show_state(obs, "RESET as barbarian")
    
    # Move around to find monsters
    search_pattern = ["north", "north", "east", "east", "south", "south", "west", "west"]
    for move in search_pattern:
        obs, reward, done, _ = wrapper.step(move)
        show_state(obs, move)
        
        # Check for combat messages
        if any(word in obs['message'].lower() for word in ['hit', 'miss', 'attack', 'killed', 'dies']):
            print("\n*** COMBAT DETECTED! ***")
        
        if done:
            print("Game ended!")
            break
    
    wrapper.close()
    
    print("\n\n=== All Tests Complete ===")

if __name__ == "__main__":
    main()