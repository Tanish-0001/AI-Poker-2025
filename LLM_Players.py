from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from player import Player, PlayerAction
from json import loads


class LLMPlayer(Player):

    def __init__(self, name, stack, api_key):
        super().__init__(name, stack)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                                          temperature=0,
                                          response_format={"type": "json_object"},
                                          google_api_key=api_key)

        template = """You are a professional poker player. You must win both, a lot of games and a lot of money. You are allowed to take safe risks.
                \nYou will be given the action history and the current poker game state as a sequence of numbers
                structured as follows.
                [hole card 1, hole card 2, community card 1, community card 2, community card 3, community card 4, community card 5,
                pot, current raise amount, number of players, stack of player 1, stack of player 2, ... , stack of player n, blind amount,
                game number]\n
                The cards will be given as a string of two characters, with the rank followed by the suit. The string "XX" indicates that the card has not been revealed yet. The current raise amount includes the big blind.\n
                Given the game state, you have to make a move in the game. You have to decide the action and the amount you will put in the pot. You will either call, raise or fold. Consider check as call with amount 0. The amount will be 0 should you choose to fold.
                \nHere is the action history of the current game:
                {action_history}
                \n\nHere is the game state, as a list of numbers:
                {game_state}
                \nYou are {name} and you currently have {stack} dollars.
                \nYou must return the output in the following JSON format:\n
                [
                "ACTION": <FOLD/CALL/RAISE>,
                "AMOUNT": <integer>,
                "EXPLANATION": <a brief reasoning>
                ]
                """

        self.prompt = ChatPromptTemplate.from_template(template)
        self.chain = self.prompt | self.llm

    def action(self, game_state: list[int], action_history: list):
        game_state[:7] = [self.card_from_index(i) for i in game_state[:7]]
        call_amount = game_state[8] - self.bet_amount
        output = self.chain.invoke(
            {'action_history': action_history, 'game_state': game_state, 'name': self.name, 'stack': self.stack})
        parsed_output = output.content.strip("```")
        parsed_output = parsed_output.lstrip("json")

        try:
            json = loads(parsed_output)
            action, amount = json["ACTION"], json["AMOUNT"]
            amount = int(amount)
            if action.upper() == 'CALL':
                return PlayerAction.CALL, call_amount
            elif action.upper() == 'RAISE' and amount > max(game_state[-2], game_state[8]):
                return PlayerAction.RAISE, int(amount)
            return PlayerAction.FOLD, 0

        except Exception as e:
            print(f"Encountered error: {e}")
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
