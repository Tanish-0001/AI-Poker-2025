from game import PokerGame, GamePhase
from base_players import FoldPlayer, AllInPlayer


def run_demo_game():
    # Create players
    players = [
        FoldPlayer("Alice", 1000),
        AllInPlayer("Bob", 1000),
        FoldPlayer("Charlie", 1000),
        AllInPlayer("Dave", 1000),
        FoldPlayer("Eve", 1000),
    ]

    # players = [
    #     Player("Alice", 1000),
    #     Player("Bob", 1000),
    #     Player("Charlie", 1000),
    #     Player("Dave", 1000),
    #     Player("Eve", 1000),
    # ]
    
    # Create game
    game = PokerGame(players, big_blind=20)
    
    # Run a few hands
    for _ in range(3):
        game.start_new_hand()
        
        # Main game loop
        while game.phase != GamePhase.SHOWDOWN:
            if game.phase == GamePhase.FLOP:
                print("\nCurrent Game State:")
                state = game.get_current_state()
                print(f"Hand: {state['hand_number']}, Phase: {state['phase']}, " +
                      f"Pot: {state['pot']}, Community Cards: {state['community_cards']}")
                
                # Also show action history
                print("\nAction History:")
                for action in game.action_history.get_round_actions(game.phase.value):
                    print(f"{action['name']} {action['action']}ed {action['amount']}")
            
            # Get player input
            if not get_player_input(game):
                continue
        
        # After showdown, display full action history
        print("\nFull Action History for this hand:")
        for action in game.action_history.get_action_sequence():
            name, act, amt = action
            print(f"{name} {act}{'ed' if not act.endswith('e') else 'd'}" + 
                  (f" {amt}" if amt > 0 else ""))
        
        print("\nHand complete. Press Enter for next hand...")
        input()
        
    return game  # Return the game object



def export_game_history(game, filename="poker_history.txt"):
    with open(filename, "w") as f:
        f.write(f"Poker Game History - {game.hand_number} hands played\n\n")
        
        for action in game.action_history.actions:
            f.write(f"Hand {action.get('hand_number', 1)} - {action['round']}: " +
                   f"{action['name']} {action['action']}ed {action['amount']}\n")
        
        f.write("\nFinal Stacks:\n")
        for player in game.players:
            f.write(f"{player.name}: {player.stack}\n")


if __name__ == "__main__":
    game = run_demo_game()
    export_game_history(game)