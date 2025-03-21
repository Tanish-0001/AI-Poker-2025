from player import Player, PlayerStatus
from game import PokerGame, GamePhase
from ui import get_player_input
from baseplayers import *

os.environ["MISTRAL_API_KEY"] = 'Ij1rT7TL8fpf5qOrlgAeqU13AjT3jmSY'
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
template = """You are a professional poker player. You will be given the current poker game state as a sequence of numbers
        structured as follows.
        [hole card 1, hole card 2, community card 1, community card 2, community card 3, community card 4, community card 5,
        pot, current raise amount, number of players, stack of player 1, stack of player 2, ... , stack of player n, blind amount,
        game number]\n
        The cards will be given as a string of two characters, with the rank followed by the suit. The string "XX" indicates that the card has not been revealed yet. The current raise amount includes the big blind.\n
        Given the game state, you have to make a move in the game. You have to decide the action and the amount you will put in the pot. You will either call, raise or fold. Consider check as call with amount 0. The amount will be 0 should you choose to fold.
        \nYou must provide only the action and the amount, and nothing else.
        \n\nHere is the game state, as a list of numbers:
        {game_state}
        \nYou currently have {stack} dollars.
        \n\nYour output must be in the format:\nACTION, AMOUNT
        """


def run_demo_game():

    players = [
        NewPlayer("Alice", 1000),
        InputPlayer("Bob", 1000),
        NewPlayer("Charlie", 1000),
        LLMPlayer("David", 1000, llm, template),
        LLMPlayer("Eve", 1000, llm, template)
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
