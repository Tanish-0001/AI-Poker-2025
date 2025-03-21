from player import Player, PlayerAction
from game import PokerGame, GamePhase
from card import Card
from typing import List, Tuple
import random
import treys as tr
from treys import Evaluator
from collections import deque
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from operator import itemgetter
import getpass
from langchain_mistralai import ChatMistralAI


os.environ["MISTRAL_API_KEY"] = "Ij1rT7TL8fpf5qOrlgAeqU13AjT3jmSY"


class FoldPlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        return PlayerAction.FOLD, 0


class RaisePlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        current_raise = game_state[8]
        if self.stack > current_raise:
            return PlayerAction.RAISE, current_raise + 40
        return PlayerAction.ALL_IN, self.stack


class InputPlayer(Player):
    def action(self, game_state: list[int], action_history: list):
        call_amount = game_state[8] - self.bet_amount

        # Display available actions
        print("Available actions:")
        if call_amount == 0:
            print("1. Check")
            print("2. Bet")
        else:
            print("1. Fold")
            print("2. Call", call_amount)
            print("3. Raise")

        action_input = input("Enter choice: ")

        try:
            if call_amount == 0:
                if action_input == "1":
                    return PlayerAction.CHECK, 0
                elif action_input == "2":
                    amount = int(input("Enter bet amount: "))
                    return PlayerAction.BET, amount
            else:
                if action_input == "1":
                    return PlayerAction.FOLD, 0
                elif action_input == "2":
                    return PlayerAction.CALL, call_amount
                elif action_input == "3":
                    amount = int(input(f"Enter total raise amount: "))
                    return PlayerAction.RAISE, amount
                else:
                    return PlayerAction.FOLD, 0
        except ValueError:
            print("Invalid input")
            return PlayerAction.FOLD, 0


rank_lookup = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "T", 11: "J", 12: "Q", 13: "K",
               14: "A"}
suit_lookup = {0: "s", 1: "h", 2: "d", 3: "c"}


class NewPlayer(Player):

    def preflop_eval(self, cards: List[Card]):  # use this to evaluate hand when no community cards have been dealt
        ranks = [card.rank.name for card in cards]
        suits = [card.suit.name for card in cards]

        if len(set(suits)) == 1:  # Flush potential
            return 8
        elif ranks[0] == ranks[1]:  # Pair
            return 7
        elif ranks in [['ACE', 'KING'], ['ACE', 'QUEEN'], ['KING', 'QUEEN']]:  # Strong broadway hands
            return 6
        elif 'ACE' in ranks or 'KING' in ranks:  # Any ace or king
            return 5
        else:
            return random.randint(1, 4)  # Randomize weak hands for variety

    def bet_check(self, game_state: list[
            int]):  # returns true is bet and ccheck are only options false when call, raise and fold are options
        return (game_state[8] - self.bet_amount) == 0

    def make_preflop_dec(self, game_state: list[int]) -> Tuple[
            PlayerAction, int]:  # use this method to make decisions when community cards have not been dealt only
        current_player = self
        current_hole_cards = current_player.hole_cards
        big_blind = game_state[13]
        current_raise = game_state[8]
        eval = self.preflop_eval(current_hole_cards)
        if eval >= 7:
            if self.bet_check(game_state):
                print(f"{current_player.name} should bet\n")
                return PlayerAction.BET, big_blind
            else:
                print(f"{current_player.name} should raise\n")
                return PlayerAction.RAISE, current_raise
        elif eval >= 3:
            if not self.bet_check(game_state):
                print(f"{current_player.name} should call\n")
                return PlayerAction.CALL, current_raise - self.bet_amount
            else:
                print(f"{current_player.name} should check\n")
                return PlayerAction.CHECK, 0
        else:
            print(f"{current_player.name} should fold\n")
            return PlayerAction.FOLD, 0

    def index_to_rank(self, index: int) -> Tuple[int, int]:  # returns the rank of the card and takes its index as input
        rank_index = 14
        if index % 13 != 0:
            rank_index = (index % 13) + 1
        suit_index = (index - rank_index + 1) // 13

        return suit_index, rank_index

    def make_postflop_dec(self, game_state: list[int]) -> Tuple[
            PlayerAction, int]:  # execute this under the condition that game state is not pre-flop
        current_player = self
        current_hole_cards = current_player.hole_cards

        community_card_suits = deque()
        community_card_ranks = deque()

        for i in range(2, 7):
            if game_state[i] == 0:
                continue
            suit_index, rank_index = self.index_to_rank(game_state[i])
            community_card_suits.append(suit_lookup[suit_index])
            community_card_ranks.append(rank_lookup[rank_index])

        board = []
        hand = []

        for i in range(2, 7):
            if game_state[i] == 0:
                continue
            board.append(tr.Card.new(community_card_ranks.popleft() + community_card_suits.popleft()))
        for card in current_hole_cards:
            hand.append(tr.Card.new(rank_lookup[card.rank.value] + suit_lookup[card.suit.value]))
        # when do we bet ?
        evaluator = Evaluator()
        eval = evaluator.evaluate(board, hand)
        hand_rank = evaluator.get_rank_class(eval)
        current_raise = game_state[8]

        # when should you bet
        if self.bet_check(game_state):
            big_blind = game_state[13]
            if hand_rank <= 6:
                print(f"{current_player.name} should bet\n")
                return PlayerAction.BET, big_blind
            else:
                print(f"{current_player.name} should check\n")
                return PlayerAction.CHECK, 0
        else:
            if hand_rank <= 4:
                print(f"{current_player.name} should raise\n")
                return PlayerAction.RAISE, current_raise
            elif hand_rank <= 6:
                print(f"{current_player.name} should call\n")
                return PlayerAction.CALL, current_raise - self.bet_amount
            else:
                print(f"{current_player.name} should fold\n")
                return PlayerAction.FOLD, 0

    def action(self, game_state: list[int], action_history: list):
        if (game_state[2] == 0 and
                game_state[3] == 0 and
                game_state[4] == 0 and
                game_state[5] == 0 and
                game_state[6] == 0):
            return self.make_preflop_dec(game_state)
        return self.make_postflop_dec(game_state)


class LLMPlayer(Player):

    def __init__(self, name, stack, llm, template):
        super().__init__(name, stack)
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(template)
        self.chain = self.prompt | self.llm

    def action(self, game_state: list[int], action_history: list):
        game_state[:7] = [self.card_from_index(i) for i in game_state[:7]]
        call_amount = game_state[8] - self.bet_amount
        output = self.chain.invoke({'game_state': game_state, 'stack': self.stack})
        action, amount = output.content.split(',')

        try:
            amount = int(amount)
            if action.upper() == 'CALL':
                return PlayerAction.CALL, call_amount
            elif action.upper() == 'RAISE' and amount > max(game_state[-2], game_state[8]):
                return PlayerAction.RAISE, int(amount)
            return PlayerAction.FOLD, 0
        except:
            return PlayerAction.FOLD, 0

    @staticmethod
    def card_from_index(index) -> str:
        if index == 0:
            return "XX"
        index -= 1  # since it is 1-indexed
        suit = index // 13
        rank = index % 13
        res = ''
        if rank == 12:
            res += 'A'
        elif rank == 11:
            res += 'K'
        elif rank == 10:
            res += 'Q'
        elif rank == 9:
            res += 'J'
        else:
            res += str(rank + 2)

        if suit == 0:
            res += 'S'
        elif suit == 1:
            res += 'H'
        elif suit == 2:
            res += 'D'
        else:
            res += 'C'

        return res


class LLMWithRagPlayer(Player):

    def __init__(self):
        loader = PyPDFLoader(r'')
        pages = loader.load()

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=800, chunk_overlap=50)
        splits = text_splitter.split_documents(pages)

        vectorstore = Chroma.from_documents(documents=splits,
                                            embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"))
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)


