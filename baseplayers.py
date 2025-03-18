from player import Player, PlayerAction
from player import Player
from game import PokerGame
from game import GamePhase
from card import Card
from typing import List, Tuple
import random
from player import PlayerAction
import treys as tr
from treys import Evaluator
from collections import deque

class FoldPlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        return PlayerAction.FOLD, 0


class RaisePlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        current_raise = game_state[8]
        if self.stack > current_raise:
            return PlayerAction.RAISE, current_raise + 40
        return PlayerAction.ALL_IN, self.stack

rank_lookup = {2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",10:"T",11:"J",12:"Q",13:"K",14:"A"}
suit_lookup = {0:"s",1:"h",2:"d",3:"c"}

class newplayer(Player):
    
 def preflop_eval(self,cards: List[Card]): # use this to eavluate hand when no community cards have been dealt
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

 def bet_check(self,game_state: list[int]): # returns true is bet and ccheck are only options false when call, raise and fold are options
    return (game_state[8] - self.bet_amount)  == 0
        
 def make_preflop_dec(self,game_state: list[int]) -> Tuple[PlayerAction,int]:  # use this method to make decisions when community cards have not been dealt only
        current_player = self
        current_hole_cards = current_player.hole_cards
        big_blind = game_state[13]
        current_raise = game_state[8]
        eval = self.preflop_eval(current_hole_cards)
        if eval >= 7:
            if(self.bet_check(game_state)):
                print(f"{current_player.name} should bet\n")
                return PlayerAction.BET, big_blind
            else:
             print(f"{current_player.name} should raise\n")
             return PlayerAction.RAISE, current_raise
        elif eval >= 3:
            if(not self.bet_check(game_state)):
             print(f"{current_player.name} should call\n")
             return PlayerAction.CALL, current_raise - self.bet_amount
            else:
             print(f"{current_player.name} should check\n")
             return PlayerAction.CHECK, 0
        else:
            print(f"{current_player.name} should fold\n")
            return PlayerAction.FOLD, 0

 def index_to_rank(self,index: int) -> Tuple[int,int]: # returns the rank of the card and takes its index as input 
    rank_index = 14
    if(index % 13 != 0):
        rank_index = (index % 13) + 1
    suit_index = (index - rank_index + 1)/13

    return suit_index,rank_index

 def make_postflop_dec(self,game_state: list[int]) -> Tuple[PlayerAction,int]: # execute this under the condition that game state is not pre-flop 
     current_player = self
     current_hole_cards = current_player.hole_cards
     
     community_card_suits = deque()
     community_card_ranks = deque()
     
     for i in range(2,7):
        if(game_state[i] == 0):
            continue
        suit_index,rank_index = self.index_to_rank(game_state[i])
        community_card_suits.append(suit_lookup[suit_index])
        community_card_ranks.append(rank_lookup[rank_index])

     board = []
     hand = []

     for i in range(2,7):
         if(game_state[i] == 0):
             continue
         board.append(tr.Card.new(community_card_ranks.popleft() + community_card_suits.popleft()))
     for card in current_hole_cards:
         hand.append(tr.Card.new(rank_lookup[card.rank.value]+suit_lookup[card.suit.value]))
     # when do we bet ?
     evaluator = Evaluator()
     eval = evaluator.evaluate(board,hand)
     hand_rank = evaluator.get_rank_class(eval)
     
     # when should you bet
     if self.bet_check(game_state):
         current_raise = game_state[8]
         big_blind = game_state[13]
         if(hand_rank <= 6):
             print(f"{current_player.name} should bet\n")
             return PlayerAction.BET, big_blind
         else:
             print(f"{current_player.name} should check\n")
             return PlayerAction.CHECK, 0
     else:
         if(hand_rank <= 4):
             print(f"{current_player.name} should raise\n")
             return PlayerAction.RAISE, current_raise
         elif(hand_rank <= 6):
             print(f"{current_player.name} should call\n")
             return PlayerAction.CALL, current_raise - self.bet_amount
         else:
             print(f"{current_player.name} should fold\n")
             return PlayerAction.FOLD, 0     

 def action(self, game_state: list[int], action_history: list):
    if(game_state[2] == 0 and game_state[3] == 0 and game_state[4] == 0 and game_state[5] == 0 and game_state[6] == 0):
     return self.make_preflop_dec(game_state)
    return self.make_postflop_dec(game_state)
