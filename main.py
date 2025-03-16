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


if __name__ == "__main__":
    run_demo_game()