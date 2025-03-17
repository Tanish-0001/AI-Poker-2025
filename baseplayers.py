from player import Player, PlayerAction


class FoldPlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        return PlayerAction.FOLD, 0


class RaisePlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        current_raise = game_state[8]
        if self.stack > current_raise:
            return PlayerAction.RAISE, current_raise + 40
        return PlayerAction.ALL_IN, self.stack
