import os
from player import Player, PlayerStatus
from game import PokerGame, GamePhase
from baseplayers import InputPlayer, NewPlayer, LLMPlayer, LLMWithRagPlayer
from langchain_mistralai import ChatMistralAI


os.environ["MISTRAL_API_KEY"] = input("Enter Mistral API Key: ")
os.environ["HF_TOKEN"] = input("Enter HF Token: ")

llm = ChatMistralAI(model_name="mistral-large-latest", temperature=0)


def run_demo_game():

    players = [
        LLMWithRagPlayer("Alice", 1000, llm),
        InputPlayer("Bob", 1000),
        NewPlayer("Charlie", 1000),
        LLMPlayer("David", 1000, llm),
        LLMPlayer("Eve", 1000, llm)
    ]
    
    # Create game
    game = PokerGame(players, big_blind=20)

    # Run a few hands
    for _ in range(3):
        game.start_new_hand()
        
        # Main game loop
        num_tries = 0
        while game.phase != GamePhase.SHOWDOWN and num_tries < 5:
            print(game.action_history)
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
