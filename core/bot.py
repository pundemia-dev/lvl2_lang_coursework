class Bot:
    def __init__(self, self_ship_set, self_ship_unset, self_check_alive, self_bombs_enable, user_bomb_action):
        self.ship_set = self_ship_set
        self.ship_unset_func = self_ship_unset 
        self.check_alive = self_check_alive 
        self.bombs_enable = self_bombs_enable 
        self.user_bomb_action = user_bomb_action

    def callback(self):
        pass

        
