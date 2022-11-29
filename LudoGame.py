# Author: James Wollenburg
# GitHub username: jrwollenburg
# Date: 08/04/2022
# Description: A program that allows the user to play a simplified version of the  game of Ludo. To play, the program
#              takes a list of players in some combination of A, B, C, or D, and a list of turns. The list of turns is
#              a list of tuples which are the players position and their dice roll. Takes these two lists and uses them
#              to play an instance of Ludo. At the end, returns the final positions of all the tokens on the board.
#
#               Moves are applied based on a priority system as follows:
#               1. If the die roll is 6, try to let the token that still in the home yard get out of the home yard
#               2. If one token is already in the home square and the roll is exactly what is needed to reach the end
#               3. If one token can move and kick out an opponent token, then move that token
#               4. Move the token that is the furthest away from the finishing square

class LudoGame:
    """
    Represents an instance of the game of Ludo. This class will handle adding players to the game, taking turns, moving
    tokens, and all other gameplay features. Implements a priority based decision-making algorithm to determine which
    token should be moved during a turn.

    Uses the Board class, Player class, and Token class to check positions, if tokens are stacked, or if another player
    has a token that should be kicked back to home, game/player completion status, and other key information that may
    alter the gameplay.

    Methods: get_player_by_position, move_token, play_game, player_setup, token_determination, home_yard_check,
    can_token_finish, final_stretch_check, can_player_attack, furthest_token, kick_home, occupied_space_check, and
    get_game_state
    """

    def __init__(self):
        self._game_state = 'Still Playing'
        self._players = {}  # Position: Player Object
        self._board = Board()  # creates the board object

    # required methods
    def get_player_by_position(self, pos):
        """
        Takes a position and returns the player object associated with that position. Returns Player Not Found! if an
        invalid position is passed.
        """
        if pos in self._players:
            return self._players[pos]
        else:
            return "Player not found!"

    def move_token(self, player_obj, token, dice_roll):
        """
        For the passed player, move either token p or q, for the passed number of steps. Updates the total step count
        and also handles kicking other player's tokens home. Uses methods from Board, Player, Token, and LudoGame.

        If a token is already finished, moves on to the next turn without applying any moves to that token.
        """
        if token == 'p':
            if player_obj.get_token_p_step_count() == 57:  # token is done
                return  # also handles one done & one at home scenario where roll is not 6
            if self.home_yard_check(player_obj) == token or self.home_yard_check(player_obj) == 'both':
                player_obj.set_token_p_step_count(0)  # a 6 has been rolled so move to ready position
                player_obj.set_token_locs(token, 'ready to go')
            else:
                self.occupied_space_check(player_obj, player_obj.get_token_p(), dice_roll)  # if space is occupied
                new_steps = player_obj.get_token_p_step_count() + dice_roll
                if new_steps > 57:  # if token does not have exact roll and will exceed final square
                    adjustment = new_steps - 57
                    new_steps = 57 - adjustment
                    player_obj.set_token_p_step_count(new_steps)
                else:
                    player_obj.set_token_p_step_count(new_steps)
                if player_obj.get_token_p_step_count() != 57:  # update position
                    player_obj.set_token_locs(token, 'somewhere on the board')
                else:
                    player_obj.set_token_locs(token, 'has finished')
            if player_obj.get_token_p().get_stacked():  # when tokens are stacked,
                player_obj.set_token_q_step_count(player_obj.get_token_p_step_count())
                if player_obj.get_token_p_step_count() == 57:  # update other token if stacked token finishes
                    player_obj.set_token_locs('q', 'has finished')
        elif token == 'q':  # functions the same as above except q is the token being moved
            if player_obj.get_token_q_step_count() == 57:
                return
            if self.home_yard_check(player_obj) == token:
                player_obj.set_token_q_step_count(0)
                player_obj.set_token_locs(token, 'ready to go')
            else:
                self.occupied_space_check(player_obj, player_obj.get_token_q(), dice_roll)
                new_steps = player_obj.get_token_q_step_count() + dice_roll
                if new_steps > 57:
                    adjustment = new_steps - 57
                    new_steps = 57 - adjustment
                    player_obj.set_token_p_step_count(new_steps)
                else:
                    player_obj.set_token_q_step_count(new_steps)
                if player_obj.get_token_q_step_count() != 57:
                    player_obj.set_token_locs(token, 'somewhere on the board')
                else:
                    player_obj.set_token_locs(token, 'has finished')
            if player_obj.get_token_q().get_stacked():
                player_obj.set_token_p_step_count(player_obj.get_token_q_step_count())
                if player_obj.get_token_p_step_count() == 57:
                    player_obj.set_token_locs('p', 'has finished')
        if not player_obj.get_token_p().get_stacked() and player_obj.can_token_stack():
            player_obj.stack_tokens()

    def play_game(self, player_list, turn_list):
        """
        Takes a list of player positions, creates the player objects, and adds them to the player dictionary. Then uses
        the move_token function to move tokens according to the passed turn_list. Uses a decision-making algorithm
        based on a priority system to move the tokens.

        Updates the Board object with new token positions. Updates LudoGame object status with Game Complete if the game
        is over (but does not prevent the last player to keep playing).

        Returns a list of the spaces that are occupied after all turns are taken.
        """
        count_finished = 0  # number of players that have finished the game
        for pos in player_list:
            self.player_setup(pos)
            self._board.set_tokens_in_play(self._players.values())
        for turn in turn_list:
            turn_player = self.get_player_by_position(turn[0])  # player position is index 0 of tuple
            dice_roll = turn[1]  # dice roll is at index 1 of tuple
            token = self.token_determination(turn_player, dice_roll)  # call decision algorithm
            if token == turn_player.get_token_p():
                token = 'p'
            elif token == turn_player.get_token_q():
                token = 'q'
            if token is not None:  # none occurs when a token cannot be moved out of home space
                self.move_token(turn_player, token, dice_roll)
            self._board.set_tokens_in_play(self._players.values())

        for player in player_list:  # game is over when only 1 player is left still playing
            if self.get_player_by_position(player).get_completed():
                count_finished += 1
        if count_finished == len(player_list) - 1:  # only changes status, does not prevent further turns
            self._game_state = 'Game Complete'
        return self._board.occupied_spaces()

    # end required methods

    def player_setup(self, pos):
        """
        Takes a string position from A, B, C, or D and initializes the Player object. Adds them to the dictionary of
        players (a LudoGame attribute). Sets each player's start and end spaces depending on their position choice.
        """
        self._players[pos] = Player(pos)
        self._players[pos].set_start_end()

    def token_determination(self, player, roll):
        """
        Takes a player object as a parameter and determines which token should receive the moves, if any. Uses a
        priority system to determine which token, p or q, should be moved. Handles Priority 1 in this function.

        Priority 1: If the die roll is 6, try to let the token that still in the home yard get out of the
        home yard (if both tokens are in the home yard, choose the first one ‘p’).

        Returns the token that meets the criteria, or else returns a call to the next priority check.
        """
        if roll == 6:
            if self.home_yard_check(player) == 'both':  # default to move p first
                return player.get_token_p()
            elif self.home_yard_check(player) == 'p':
                return player.get_token_p()
            elif self.home_yard_check(player) == 'q':
                return player.get_token_q()
            else:  # home_yard_check returns none
                return self.can_token_finish(player, roll)
        elif roll != 6:
            if self.home_yard_check(player) == 'both':
                return None  # both in yard, but not a 6 means turn ends without move
            elif self.home_yard_check(player) == 'p':
                return player.get_token_q()  # only q is movable
            elif self.home_yard_check(player) == 'q':
                return player.get_token_p()  # only p is movable
            else:  # neither at home
                return self.can_token_finish(player, roll)

    def home_yard_check(self, player):
        """
        Takes the current turn player object and checks if they have a token in the home yard. Returns either both, p,
        or q. Returns None if there are no tokens in the home yard.

        Returns both, p, or q depending on which tokens are in the home yard. Or None if neither are.
        """
        if player.get_token_locs() == ['in the home yard', 'in the home yard']:
            return 'both'
        elif player.get_token_locs()[0] != 'in the home yard' and player.get_token_locs()[1] == 'in the home yard':
            return 'q'
        elif player.get_token_locs()[0] == 'in the home yard' and player.get_token_locs()[1] != 'in the home yard':
            return 'p'
        else:
            return None

    def can_token_finish(self, player, roll):
        """
        Takes the turn player and checks if they own a token that can finish the game. Implements priority 2. Returns
        the token that can finish (beware stacked implementation might be needed). Otherwise, checks the next priority.

        Priority 2: If one token is already in the home square and the step number is exactly what is needed to
        reach the end square, let that token move and finish.

        Returns the token that meets the criteria, or checks which priority to go to next. If both are in the last
        squares, returns a call to furthest_token. Else, returns a call to can_player_attack.
        """
        if self.final_stretch_check(player) == 'both':
            if player.get_token_p_step_count() + roll == 57:
                return player.get_token_p()
            elif player.get_token_q_step_count() + roll == 57:
                return player.get_token_q()
            else:  # both are in final stretch, but can't finish so apply priority 4
                return self.furthest_token(player)
        elif self.final_stretch_check(player) == 'p':
            if player.get_token_p_step_count() + roll == 57:
                return player.get_token_p()
            else:  # give the move to 'q' (neither token is home)
                return player.get_token_q()
        elif self.final_stretch_check(player) == 'q':
            if player.get_token_q_step_count() + roll == 57:
                return player.get_token_q()
            else:
                return player.get_token_p()
        else:  # neither is home, but neither is in the final stretch
            return self.can_player_attack(player, roll)  # pass to priority 3 scenario

    def final_stretch_check(self, player):
        """
        Determines if the current turn player has a token in the final stretch.

        Returns the token(s) that are in the last squares, else returns None if neither.
        """
        # both in the final stretch
        if player.get_token_p_step_count() in range(51, 57) and player.get_token_q_step_count() in range(51, 57):
            return 'both'
        elif player.get_token_p_step_count() in range(51, 57):
            return 'p'
        elif player.get_token_q_step_count() in range(51, 57):
            return 'q'
        else:
            return None

    def can_player_attack(self, player, roll):
        """
        Function only called if both player tokens are out of the home and not in the final stretch.
        Takes the current turn player and their roll. Determines if one of the player's tokens can land on another
        player's token to kick them back home. Returns which token this applies to. Otherwise, passes to priority 4.
        Implementation of Priority 3: If one token can move and kick out an opponent token, then move that token.

        Uses Board class to find occupied spaces. Uses Token and Player class to determine owner of the token.
        """
        potential_space_p = player.get_token_p_step_count() + roll  # looking ahead
        potential_space_q = player.get_token_q_step_count() + roll
        new_space_p = player.get_space_name(potential_space_p)
        new_space_q = player.get_space_name(potential_space_q)
        keys = list(self._board.get_tokens_in_play().keys())  # token object
        if new_space_p in self._board.occupied_spaces() \
                and new_space_q in self._board.occupied_spaces():
            return self.furthest_token(player)
        if new_space_p in self._board.occupied_spaces():  # if p can land on another player's token
            index = self._board.occupied_spaces().index(new_space_p)  # index of the occupied space
            if player != keys[index].get_owner():  # if token is owned by someone else
                return player.get_token_p()
        elif new_space_q in self._board.occupied_spaces():
            index = self._board.occupied_spaces().index(new_space_q)
            if player != keys[index].get_owner():
                return player.get_token_q()
        return self.furthest_token(player)

    def furthest_token(self, player):
        """
        Takes the player and determines which token is furthest from the end. Method only called when both tokens are
        in play. Returns the token to move.
        Implementation of Priority 4: Move the token that is further away from the finishing square.
        """
        if player.get_token_p_step_count() <= player.get_token_q_step_count():
            return player.get_token_p()
        elif player.get_token_p_step_count() > player.get_token_q_step_count():
            return player.get_token_q()

    def kick_home(self, player, index):
        """
        Takes the player and using the index from can_player_attack(), determines which token of that player (p or q)
        to kick and then updates its location. Capable of sending stacked tokens home.
        """
        if index % 2 == 0:  # token p is stored at an even index
            player.set_token_p_step_count(-1)
            player.set_token_locs('p', 'in the home yard')
        else:  # token q is stored at an odd index
            player.set_token_q_step_count(-1)
            player.set_token_locs('q', 'in the home yard')
        if player.get_token_p().get_stacked():  # when a stacked token is sent home, update both.
            player.get_token_p().set_stacked(False)
            player.get_token_q().set_stacked(False)
            player.set_token_p_step_count(-1)
            player.set_token_q_step_count(-1)
            player.set_token_locs('p', 'in the home yard')
            player.set_token_locs('q', 'in the home yard')
        self._board.set_tokens_in_play(self._players.values())  # updates the game board

    def occupied_space_check(self, player, token, roll):
        """Determines if the space that is being landed on is occupied. If there is another player's token in that
        space, kick it home. This catches the scenario where a player only has one token out on the board, and it
        happens to land on another player's token (in other words that single token is being moved by default).

        Returns nothing but calls kick_home."""
        keys = list(self._board.get_tokens_in_play().keys())
        if token == player.get_token_p():
            potential_space_p = player.get_token_p_step_count() + roll
            new_space = player.get_space_name(potential_space_p)
            if new_space in self._board.occupied_spaces():
                index = self._board.occupied_spaces().index(new_space)
                if player != keys[index].get_owner():
                    self.kick_home(keys[index].get_owner(), index)
        else:
            potential_space_q = player.get_token_q_step_count() + roll
            new_space = player.get_space_name(potential_space_q)
            if new_space in self._board.occupied_spaces():
                index = self._board.occupied_spaces().index(new_space)
                if player != keys[index].get_owner():
                    self.kick_home(keys[index].get_owner(), index)

    def get_game_state(self):
        """Returns the game state. Default is Still Playing. When only one player is left,
        is switched to Game Complete. Current implementation does not prevent last player to keep playing."""
        return self._game_state


class Board:
    """
    Represents the game board. Takes no parameters and is initialized as an empty board. Tracks the tokens in play and
    can display the game board. Used by LudoGame class.

    Methods: set_tokens_in_play, get_tokens_in_play, occupied_spaces
    """

    def __init__(self):
        self._tokens_in_play = {}  # Token: Board Space Name

    def set_tokens_in_play(self, player_list):
        """Adds the players to the Board's dictionary as Token: Board Space Name"""
        for player in player_list:
            p_steps = player.get_token_p_step_count()
            q_steps = player.get_token_q_step_count()
            p_space = player.get_space_name(p_steps)
            q_space = player.get_space_name(q_steps)
            self._tokens_in_play[player.get_token_p()] = p_space
            self._tokens_in_play[player.get_token_q()] = q_space

    def get_tokens_in_play(self):
        """Returns the tokens in play dictionary."""
        return self._tokens_in_play

    def occupied_spaces(self):
        """Returns a list containing the dictionary values. These values are the occupied spaces on the board."""
        return list(self._tokens_in_play.values())


class Player:
    """
    Represents the Player Class. Used by LudoGame, Board, and Token classes. Takes the player's position choice as the
    only parameter, but contains additional data regarding token locations, steps, player status, starting/end spaces.

    Each Player is automatically initialized with two Token objects. One for P and one for Q.
    """

    def __init__(self, position):
        self._position = position
        self._start = None
        self._end = None
        self._token_locs = ['in the home yard', 'in the home yard']  # ready to go/somewhere on the board/has finished
        self._p_steps = -1  # -1 = home, 0 = ready to go, 1-56 in play, 57 done
        self._q_steps = -1
        self._completed = False  # False if still playing, True if player has finished
        self._token_p = Token(self, position + 'p')  # designed with future GUI implementation in mind.
        self._token_q = Token(self, position + 'q')  # Token will be displayed as position + token, ex. Ap and Aq.

    # required methods

    def get_completed(self):
        """
        Returns False if the player is still playing or True if they have completed the game. Used by LudoGame to
        determine if the game is over yet.
        """
        if self._token_locs[0] == self._token_locs[1] == 'has finished':
            return True
        return False

    def get_token_p_step_count(self):
        """
        Return the current step count for token 'p'. Used by LudoGame to determine a token's location.
        """
        return self._p_steps

    def get_token_q_step_count(self):
        """
        Return the current step count for token 'q'. Used by LudoGame to determine a token's location.
        """
        return self._q_steps

    def get_space_name(self, steps):
        """
        Takes a number of steps and then returns the name of the space as a string. Used by Board to update occupied
        spaces.
        """
        if steps == -1:
            return 'H'
        elif steps == 0:
            return 'R'
        elif 1 <= steps <= 50:
            space_name = int(self._start) + steps - 1  # cast to int to do the math
            if space_name > 56:
                space_name -= 56
            return str(space_name)  # cast to string
        elif 51 <= steps <= 56:
            return self._position + str(steps)[-1]  # final spaces are in the format position letter + space number(1-6)
        elif steps == 57:
            return 'E'

    # end required methods

    def set_start_end(self):
        """
        Sets the start and end spaces depending on the position the player has chosen. Used by LudoGame class to setup
        players.
        """
        if self._position == 'A':
            self._start = '1'
            self._end = '50'
        elif self._position == 'B':
            self._start = '15'
            self._end = '8'
        elif self._position == 'C':
            self._start = '29'
            self._end = '22'
        elif self._position == 'D':
            self._start = '43'
            self._end = '36'

    def set_token_p_step_count(self, step):
        """Update token P step count. Used by LudoGame to move token."""
        self._p_steps = step

    def set_token_q_step_count(self, step):
        """Update token Q step count. Used by LudoGame to move token."""
        self._q_steps = step

    def get_token_locs(self):
        """Returns token locations. Used by LudoGame as part of decision-making algorithm and to keep track of where
        the tokens are."""
        return self._token_locs

    def set_token_locs(self, token, location):
        """Updates token locations. Used by LudoGame class after moves are made."""
        if token == 'p':
            self._token_locs[0] = location
        elif token == 'q':
            self._token_locs[1] = location

    def get_token_p(self):
        """Returns the Token object representing token P. Used by Board to update its dictionary. Used by LudoGame
        as part of token movement algorithm."""
        return self._token_p

    def get_token_q(self):
        """Returns the Token object representing token Q. Used by Board to update its dictionary. Used by LudoGame
        as part of token movement algorithm."""
        return self._token_q

    def can_token_stack(self):
        """Returns True if a token can be stacked on another token. False if not. Called by LudoGame after moves have
        been made. Does not stack two different player's tokens."""
        if 0 < self.get_token_p_step_count() == self.get_token_q_step_count() < 57:
            if self.get_token_p_step_count() == self.get_token_q_step_count():
                return True
        return False

    def stack_tokens(self):
        """Set's a token's stacked attribute to True. Used by LudoGame to stack tokens."""
        self._token_p.set_stacked(True)
        self._token_q.set_stacked(True)


class Token:
    """
    Represents a token. Each player is initialized with two. One for P and one for Q. When a player is initialized,
    both tokens are assigned as owned by that player and their identity becomes the player position plus p or q. For
    example player A will own tokens Ap and Aq. This functionality will be used for the GUI. Used by Player, Board, and
    LudoGame.

    Methods: get_owner, get_token_identity, get_stacked, set_stacked
    """

    def __init__(self, owner, token_identity):
        self._owner = owner  # Initialized with a Player object as the owner.
        self._token_identity = token_identity  # can be either 'p' or 'q'
        self._stacked = False

    def get_owner(self):
        """Returns the player object which owns the token. Used by LudoGame when determining if tokens should be stacked
        or kicked back home."""
        return self._owner

    def get_token_identity(self):
        """Returns token identity. Not used - To be used in board GUI, if that gets implemented."""
        return self._token_identity

    def get_stacked(self):
        """Returns true if tokens are stacked, false if they are not. Used by LudoGame to decide whether tokens are
        stacked and therefore must move in unison."""
        return self._stacked

    def set_stacked(self, status):
        """Updates stacked status. Used by LudoGame to set Stacked status after a stacked token has been kicked.
        Primarily used to set status to False."""
        self._stacked = status

players = ['C']
turns = [('C',6), ('C',51)]
game = LudoGame()
current_tokens_space = game.play_game(players, turns)
print(current_tokens_space)