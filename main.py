from player import Player, PlayerStatus
from game import PokerGame, GamePhase
from ui import get_player_input
from baseplayers import FoldPlayer, RaisePlayer


def run_demo_game():

    players = [
        FoldPlayer("Alice", 1000),
        RaisePlayer("Bob", 1000),
        FoldPlayer("Charlie", 1000),
        RaisePlayer("David", 1000),
    ]
    
    # Create game
    game = PokerGame(players, big_blind=20)
    
    # Run a few hands
    for _ in range(3):
        game.start_new_hand()
        
        # Main game loop
        num_tries = 0
        while game.phase != GamePhase.SHOWDOWN and num_tries < 5:
            if game.num_active_players() == 1:
                game.advance_game_phase()
            player = game.players[game.active_player_index]

            print(f"\n{player.name}'s turn")
            print(f"Your cards: {[str(c) for c in player.hole_cards]}")

            is_successful = game.get_player_input()

            if not is_successful:
                print("Invalid command received.")
                num_tries += 1
            else:
                num_tries = 0
        print("\nHand complete. Press Enter for next hand...")
        input()


if __name__ == "__main__":
    run_demo_game()
