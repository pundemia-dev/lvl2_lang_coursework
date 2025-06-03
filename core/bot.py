import random
from core.ship_container import ShipType
import customtkinter as ctk

class Bot(ctk.CTkFrame):
    def __init__(self, master, self_ship_set, self_ship_unset, self_check_alive, self_bombs_enable, user_bomb_action):
        super().__init__(master)
        self.ship_set = self_ship_set
        self.ship_unset_func = self_ship_unset 
        self.check_alive = self_check_alive 
        self.bombs_enable = self_bombs_enable 
        self.user_bomb_action = user_bomb_action
        
        self.create_map()

    def create_map(self):
        trash_poss = []
        for ship in ShipType:
            for sh in range(ship.count):
                while True:
                    rotation = random.randint(0, 1)
                    pos = (random.randint(0, 9), random.randint(0, 9))
                    center = ship.cells_count // 2 
                    begin_pos = pos[rotation] - center
                    end_pos = begin_pos + ship.cells_count
                    positions = [(pos[0], p) if rotation else (p, pos[1]) for p in range(begin_pos, end_pos)]
                    filtered_positions = [pos for pos in positions if all(0 <= unit < 10 for unit in pos)]
                    flag_frame = len(positions) is len(filtered_positions)
                    if flag_frame:
                        flag_combine = not any(x in trash_poss for x in filtered_positions)
                        if flag_combine:
                            for poss in filtered_positions:
                                for x in range(poss[0]-1, poss[0]+2):
                                    for y in range(poss[1]-1, poss[1]+2):
                                        trash_poss.append((x, y))

                            trash_poss.extend(filtered_positions)
                            self.master.botgrid.active_shiptype_selector = ship
                            self.master.botgrid.selector_rotation = rotation 
                            self.ship_set(pos)
                            print(ship.type, filtered_positions, list([x in trash_poss for x in filtered_positions]))
                            break

    def callback(self):
        pass

        
