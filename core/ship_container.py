from enum import Enum
from random import randint
from icecream import ic
import customtkinter as ctk
import threading

from core.colors import Color

def start_timer(func, seconds, *args):
    timer = threading.Timer(seconds, func, args=args)
    timer.start()

class ShipType(Enum):
    PATROL_BOAT = (
        "Patrol boat",
        1,
        (

        ),
        4
    )
    DESTROYER = (
        "Destroyer",
        2,
        (

        ),
        3
    )
    CRUISER = (
        "Cruiser",
        3,
        (

        ),
        2
    )
    BATTLESHIP = (
        "Battleship",
        4,
        (
        
        ),
        1
    )
    def __init__(self, type: str, cells_count: int, cell_imgs: set, count: int):
        self.type = type
        self.cells_count = cells_count
        self.cell_imgs = cell_imgs
        self.count = count

class CellState(Enum):
    alive = 1
    cell = 0
    dead = -1

class Cell(ctk.CTkButton):
    def __init__(self, master, position, ship_mapping_func, ship_set_func, bomb_action_func, hidden=False):
        args = {
            "width": 30,
            "height": 30,
            "text": "",
            "fg_color": Color.gray,
            "hover_color": Color.gray_dark,
            # "text_color_disabled": Color.white_dark,
            "command": self.button_command
        }
        super().__init__(master, **args)
        self.state = None
        self.position = position
        self.ship_set_func = ship_set_func
        self.ship_unset_func = None
        self.ship_mapping_func = ship_mapping_func
        self.last_text = ""
        self.default_color = Color.gray
        self.bomb_action_func = bomb_action_func
        self.hidden = hidden
        self.toggle_hidden(hidden)
        self.bind("<Button-3>", self.mark) 
    
    def mark(self, _):
        ic.enable()
        text, text_color = "×", Color.white_dark
        if ic(self.cget("text")) == text:
            text, text_color = " ", Color.gray
        if ic(self.cget("state")) == "normal":
            ic()
            self.configure(text=text, text_color=text_color)

    def always_dead(self):
        if self.state is CellState.dead:
            self.configure(fg_color=Color.red)
            self.default_color = Color.red

    def toggle_hidden(self, enable):
        self.hidden = enable
        if enable:
            self.configure(text_color=self.default_color, hover_color=Color.yellow)
            if self.cget("text") not in (" ", "󱥸 ", "×"):
                self.configure(text=" ")


    def bombs_enable(self, enable):
        if enable:
            self.bind("<Enter>", lambda _: self.configure(text_color=Color.white, fg_color=Color.yellow) if self.cget("state") == "normal" else None)
            self.bind("<Leave>", lambda _: self.configure(text_color=Color.gray if self.cget("text") != "×" else Color.white_dark, fg_color=self.default_color) if self.cget("state") == "normal" else None)
            self.configure(state="disabled" if self.cget("text") in (" ", "󱥸 ") else "normal")
        else:
            self.unbind("<Enter>")
            self.unbind("<Leave>")
            self.configure(state="disabled")

    def check_alive(self) -> bool:
        match self.state:
            case CellState.alive:
                return True
            case _:
                return False

    def is_me(self, position):
        return position is self.position

    def set_ship_unset_func(self, func):
        self.ship_unset_func = func

    def button_command(self):
        match (self.state, self.hidden): 
            case (None, False):
                self.ship_set_func(self.position)
            case (CellState.alive, False):
                self.ship_unset_func()
            case (_, True):
                self.bomb_action_func(self.position, True)

    def set_state(self, state):#state: CellState):
        self.state = state
        match (state, self.hidden):
            case (CellState.alive, 0):
                self.configure(fg_color=Color.green, state="normal")
                self.default_color = Color.green
            case (CellState.cell, 0):
                self.configure(fg_color=Color.gray, state="disabled")
                self.default_color = Color.gray
            case (CellState.dead, 0):
                self.configure(fg_color=Color.yellow_dark if self.hidden else Color.yellow, state="disabled", text_color_disabled=Color.white)
                self.default_color = Color.yellow_dark if self.hidden else Color.yellow
            case (CellState.dead, 1):
                self.configure(fg_color=Color.yellow_dark if self.hidden else Color.yellow, state="disabled", text_color_disabled=Color.white_dark)
                self.default_color = Color.yellow_dark if self.hidden else Color.yellow
            case (None, _):
                self.configure(fg_color=Color.gray, state="normal", text="")
                self.default_color = Color.gray

    def ship_mapping(self, enable: bool):
        if enable:
            self.bind("<Enter>", lambda event: self.ship_mapping_func(self.position, True))
            self.bind("<Leave>", lambda event: self.ship_mapping_func(self.position, False))
            self.configure(state="normal")
        else:
            self.unbind("<Enter>")
            self.unbind("<Leave>")
            self.configure(state="disabled")

    def ship_on_hover(self, enable: bool, flag=True):
        if enable:
            self.configure(fg_color=Color.green if flag and self.state is None else Color.red)
        else:
            self.configure(fg_color=self.default_color)

    def bomb_on_hover(self, enable: bool):
        if enable:
            self.last_text = self.cget("text")
            self.configure(text=" ")
        else:
            self.configure(text=self.last_text)

    def bomb_action(self)->bool:
        if self.state is CellState.alive:
            self.configure(text="󱥸 ", state="disabled")
            self.set_state(CellState.dead)
            return CellState.alive
        else:
            self.configure(text=" ", state="disabled", fg_color=self.default_color)
            return CellState.cell


class ShipsSelector(ctk.CTkFrame):
    def __init__(self, master, select_ship_func, load_random_map):
        super().__init__(master)
        self.grid_rowconfigure(9, weight=1) 
        self.buttons = []

        for row, ship in enumerate(ShipType):
            button = ctk.CTkButton(self, text=f"{ship.type} {"*"*ship.cells_count}", fg_color=Color.blue, hover_color=Color.blue_dark, command=lambda shiptype=ship: select_ship_func(shiptype))
            button.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            self.buttons.append(button)

        button = ctk.CTkButton(self, text="Load random map", fg_color=Color.purple, hover_color=Color.purple_dark, command=load_random_map)
        button.grid(row=len(ShipType), column=0, padx=10,pady=10,sticky="nsew")
        self.buttons.append(button)

    def enable_selector(self, enable:bool):
        list(map(lambda button:button.configure(state="normal" if enable else "disabled"), self.buttons))

class Ship:
    def __init__(self, ship_type, ship_unset_func):
        self.ship_type = ship_type
        self.cells_list = list()
        self.positions = list()
        self.alive = True
        self.ship_unset_func = ship_unset_func

    def add_cell(self, cell, position):
        if len(self.cells_list) < self.ship_type.cells_count:
            self.cells_list.append(cell)
            self.positions.append(position)
            cell.set_state(CellState.alive)
            cell.set_ship_unset_func(self.unset)
        else:
            pass # logs

    def always_dead(self):
        [cell.always_dead() for cell in self.cells_list]

    def unset(self):
        self.ship_unset_func(self.positions, self.ship_type)

    def is_me(self, position):
        return (position[0], position[1]) in self.positions

    def check_alive(self, not_include_pos=None) -> bool:
        ic.enable()
        if not_include_pos is not None:
            ic(not_include_pos, self.cells_list[0].position)
            ic.disable()
            return sum(ic([cell.check_alive() for cell in self.cells_list if cell.position not in not_include_pos]))
        else:
            ic.disable()
            return sum(ic([cell.check_alive() for cell in self.cells_list]))


class Reload(ctk.CTkToplevel):
    def __init__(self, text, reload_callback):
        super().__init__()
        self.reload_callback = reload_callback
        self.title("Морской бой: уведомление")
        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=10)
        self.button = ctk.CTkButton(self, text="Reload", fg_color=Color.aqua, hover_color=Color.aqua_dark, command=self.button_callback)
        self.button.pack(padx=20, pady=20)

    def button_callback(self):
        self.reload_callback()
        self.destroy()

class ShipContainer(ctk.CTkFrame):
    def __init__(self, master, reload_callback, iter_callback = None, hidden=False):
        super().__init__(master)
        self.reload_callback = reload_callback
        self.hidden = hidden
        self.iter_callback = iter_callback
        self.cells_frame = ctk.CTkFrame(self)
        self.cells_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.ship_selector = ShipsSelector(self, self.set_active_shiptype_selector, self.load_random_map)
        if not self.hidden:
            self.ship_selector.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.cell_list = []
        self.play_button = ctk.CTkButton(self.ship_selector, text="Play", fg_color=Color.aqua, hover_color=Color.aqua_dark, command=self.play_game)

        for y in range(10):
            if y >= len(self.cell_list):
                self.cell_list.append([])
            for x in range(10):
                cell = Cell(self.cells_frame, (x, y), self.ship_on_hover, self.ship_set, self.bomb_action, self.hidden)
                cell.grid(row=y, column=x, padx=5, pady=5, sticky="nsew")
                self.cell_list[y].append(cell)
        
        self.bomb_rain_time = [(9.8*i)/100 for i in range(9, -1, -1)]
        self.last_bombed = []
        self.ships_counts = {ship.name: ship.count for ship in ShipType}
        self.ships = {ship.name: [] for ship in ShipType}
        self.active_shiptype_selector = None
        self.selector_rotation = True
        self.selector_position = ()
        self.enable_ship_selector(True)

    def toggle_hidden(self):
        self.hidden = not self.hidden
        for row in self.cell_list:
            for cell in row:
                cell.toggle_hidden(self.hidden)

        if self.hidden:
            self.ship_selector.grid_forget()
        else:
            self.ship_selector.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

    def toggle_selector_rotation_callback(self, _):
        self.ship_on_hover(self.selector_position, False)
        self.selector_rotation = not self.selector_rotation
        self.ship_on_hover(self.selector_position, True)

    def set_active_shiptype_selector(self, shiptype):
        self.active_shiptype_selector = shiptype

    def enable_ship_selector(self, enable: bool):
        for row in self.cell_list:
            for cell in row:
                cell.ship_mapping(enable)
        # list(map(lambda row: map(lambda cell: cell.ship_mapping(enable), row), self.cell_list))
        self.ship_selector.enable_selector(enable)
        if enable:
            self.master.master.bind("<BackSpace>", self.toggle_selector_rotation_callback)
        else:
            self.master.master.unbind("<BackSpace>")

    def ship_on_hover(self, position, enable:bool):
        if self.active_shiptype_selector is not None:
            self.selector_position = position
            center = self.active_shiptype_selector.cells_count // 2 
            begin_pos = position[self.selector_rotation] - center
            end_pos = begin_pos + self.active_shiptype_selector.cells_count
            positions = [(position[0], p) if self.selector_rotation else (p, position[1]) for p in range(begin_pos, end_pos)]
            filtered_positions = [pos for pos in positions if all(0 <= unit < 10 for unit in pos)]
            flag = len(positions) is len(filtered_positions) and self.ships_counts[self.active_shiptype_selector.name]
            list(map(lambda pos: self.cell_list[pos[1]][pos[0]].ship_on_hover(enable, flag), filtered_positions))

    def ship_set(self, position):
        if self.active_shiptype_selector is not None:
            center = self.active_shiptype_selector.cells_count // 2 
            begin_pos = position[self.selector_rotation] - center
            end_pos = begin_pos + self.active_shiptype_selector.cells_count
            positions = [(position[0], p) if self.selector_rotation else (p, position[1]) for p in range(begin_pos, end_pos)]
            filtered_positions = [pos for pos in positions if all(0 <= unit < 10 for unit in pos)]
            flag = len(positions) is len(filtered_positions)
            if flag and self.ships_counts[self.active_shiptype_selector.name]:
                ship = Ship(self.active_shiptype_selector, self.ship_unset_func)
                self.ships[self.active_shiptype_selector.name].append(ship)
                self.ships_counts[self.active_shiptype_selector.name] -= 1
                for pos in positions:
                    for x in range(pos[0]-1, pos[0]+2):
                        for y in range(pos[1]-1, pos[1]+2):
                            if x in range(10) and y in range(10):
                                self.cell_list[y][x].set_state(CellState.cell)
                for pos in positions:
                    self.ships[self.active_shiptype_selector.name][-1].add_cell(self.cell_list[pos[1]][pos[0]], pos)

                if not sum(self.ships_counts.values()):
                    self.play_button.grid(row=10, column=0, padx=5, pady=5, sticky="sew")
    
    def load_random_map(self):
        self.reload_map() 
        trash_positions = []
        for shiptype in ShipType:
            self.set_active_shiptype_selector(shiptype)
            for ship in range(shiptype.count):
                while True:
                    if randint(0, 1):
                        self.selector_rotation = not self.selector_rotation
                    position = (randint(0, 9), randint(0, 9))
                    center = shiptype.cells_count // 2 
                    begin_pos = position[self.selector_rotation] - center
                    end_pos = begin_pos + shiptype.cells_count
                    positions = [(position[0], p) if self.selector_rotation else (p, position[1]) for p in range(begin_pos, end_pos)]
                    filtered_positions = [pos for pos in positions if all([0 <= unit < 10 for unit in pos])]
                    flag_frame = len(positions) is len(filtered_positions)
                    if flag_frame:
                        flag_combine = not any([x in trash_positions for x in filtered_positions])
                        if flag_combine:
                            for poss in filtered_positions:
                                for x in range(poss[0]-1, poss[0]+2):
                                    for y in range(poss[1]-1, poss[1]+2):
                                        trash_positions.append((x, y))

                            trash_positions.extend(filtered_positions)
                            self.ship_set(position)
                            print(shiptype.type, filtered_positions, list([x in trash_positions for x in filtered_positions]))
                            break

        

    def ship_unset_func(self, positions, shiptype):
        for pos in positions:
            for x in range(pos[0]-1, pos[0]+2):
                for y in range(pos[1]-1, pos[1]+2):
                    if x in range(10) and y in range(10):
                        self.cell_list[y][x].set_state(None)
        self.ships[shiptype.name] = [ship for ship in self.ships[shiptype.name] if not ship.is_me(positions[0])]
        self.ships_counts[shiptype.name] += 1
        if sum(self.ships_counts.values()):
            self.play_button.grid_forget()

    def bombs_enable(self, enable):
        for row in self.cell_list:
            for cell in row:
                cell.bombs_enable(enable)

    def win_window(self):
        Reload(text = "You win :D" if self.check_alive() else "You lost(", reload_callback=self.reload_callback)
        
    def bomb_rain(self, position, target_position):
        if position[1] != 0:
            self.cell_list[position[1]-1][position[0]].bomb_on_hover(False)
        else:
            self.last_bombed.append(target_position)
        self.cell_list[position[1]][position[0]].bomb_on_hover(True)
        if position[1] == target_position[1]:
            # self.bomb_explode(target_position)
            self.cell_list[position[1]][position[0]].bomb_action()
            for ships in self.ships.values():
                for ship in ships:
                    if ship.is_me(position):
                        if not ship.check_alive(self.last_bombed):
                            ship.always_dead()
        else:
            start_timer(self.bomb_rain, self.bomb_rain_time[position[1]] if not self.hidden else 0, (position[0], position[1]+1), target_position)

    def bomb_action(self, position, button_callback = False):
        ic.disable()
        position = (position[0], position[1])
        self.bomb_rain((position[0], 0), position)

        # for y in range(position[1]):
        #     self.cell_list[y][position[0]].bomb_on_hover(True)
        #     [x for x in range(10000)] 
        #     self.cell_list[y][position[0]].bomb_on_hover(False)
        
        # self.cell_list[position[1]][position[0]].bomb_action()
        ic(self.ships)
        ic.enable()
        for ships in self.ships.values():
            for ship in ships:
                if ship.is_me(position):
                    # if not ship.check_alive(position):
                    #     ship.always_dead()
                    if button_callback:
                        self.iter_callback(not ship.check_alive(self.last_bombed))
                        return
                    else:
                        return not ship.check_alive(self.last_bombed)
        if button_callback:
            self.iter_callback(-1)
        else:
            return -1

    def check_alive(self) -> bool:
        ic.disable()
        ic(self.hidden)
        res = []
        [res.extend(list(map(lambda ship: ship.check_alive(), ships))) for ships in self.ships.values()]
        res = sum(ic(res))
        return res

    def play_game(self):
        self.enable_ship_selector(False)
        self.master.play_game()
       
    def reload_map(self):
        for ships in self.ships.values():
            for ship in ships:
                ship.unset()

    def reload(self):
        self.last_bombed = []
        # self.ships_counts = {ship.name: ship.count for ship in ShipType}
        self.reload_map() 
        for row in self.cell_list:
            for cell in row:
                cell.set_state(None)
                if cell.hidden:
                    cell.toggle_hidden(True)
                    cell.hidden = True
        # self.ships = {ship.name: [] for ship in ShipType}
        self.active_shiptype_selector = None
        self.selector_rotation = True
        self.selector_position = ()
        self.enable_ship_selector(not self.hidden)
        if self.hidden:
            self.bombs_enable(False)

