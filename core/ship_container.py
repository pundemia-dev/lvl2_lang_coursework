import customtkinter as ctk 
from enum import Enum
from core.colors import Color


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
    def __init__(self, master, position, ship_mapping_func, ship_set_func, bomb_action_func, hidden):
        args = {
            "width": 30,
            "height": 30,
            "text": "",
            "fg_color": Color.gray,
            "hover_color": Color.green_dark,
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
        self.hidden = False
        self.toggle_hidden(self.hidden)
    
    def toggle_hidden(self, enable):
        self.hidden = enable
        self.configure(self.configure(state="disabled"))

    def bombs_enable(self, enable):
        if enable:
            self.bind("<Enter>", lambda _: self.bomb_hover(enable=True) if self.cget("state") == "normal" else None)
            self.bind("<Leave>", lambda _: self.bomb_hover(enable=False) if self.cget("state") == "normal" else None)
            self.configure(state="normal")
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
                self.bomb_action_func(self.position)

    def set_state(self, state):#state: CellState):
        self.state = state
        match (state, self.hidden):
            case (CellState.alive, 0):
                self.configure(fg_color=Color.green, state="normal")
                self.default_color = Color.green
            case (CellState.cell, 0):
                self.configure(fg_color=Color.gray, state="disabled")
                self.default_color = Color.gray
            case (CellState.dead, _):
                self.configure(fg_color=Color.red, state="normal")
                self.default_color = Color.red
            case (None, _):
                self.configure(fg_color=Color.gray, state="normal")
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
            self.configure(text="󱥸 ")
            self.set_state(CellState.dead)
            return CellState.alive
        else:
            self.configure(text=" ")
            return CellState.cell


class ShipsSelector(ctk.CTkFrame):
    def __init__(self, master, select_ship_func):
        super().__init__(master)
        self.grid_rowconfigure(9, weight=1) 
        self.buttons = {ship.name: None for ship in ShipType}

        for row, ship in enumerate(ShipType):
            button = ctk.CTkButton(self, text=f"{ship.type} {"*"*ship.cells_count}", fg_color=Color.purple, hover_color=Color.purple_dark, command=lambda shiptype=ship: select_ship_func(shiptype))
            button.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            self.buttons[ship.name] = button

    def enable_selector(self, ship, enable:bool):
        self.buttons[ship].configure(state="normal" if enable else "disabled")

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

    def unset(self):
        self.ship_unset_func(self.positions, self.ship_type)

    def is_me(self, position):
        return any([position is pos for pos in self.positions])

    def check_alive(self) -> bool:
        return sum([cell.check_alive() for cell in self.cells_list])


class Reload(ctk.CTkToplevel):
    def __init__(self, text, reload_func):
        super().__init__()
        self.label = ctk.CTkLabel(text=text)
        self.label.pack(padx=20, pady=10)
        self.button = ctk.CTkButton(text="Reload", fg_color=Color.aqua, hover_color=Color.aqua_dark, command=reload_func)

class ShipContainer(ctk.CTkFrame):
    def __init__(self, master, hidden=False):
        super().__init__(master)
        self.hidden = hidden
        self.bot_callback = None
        self.cells_frame = ctk.CTkFrame(self)
        self.cells_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.ship_selector = ShipsSelector(self, self.set_active_shiptype_selector)
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

        self.ships_counts = {ship.name: ship.count for ship in ShipType}
        self.ships = {ship.name: [] for ship in ShipType}
        self.active_shiptype_selector = None
        self.selector_rotation = True
        self.selector_position = ()
        self.reload()

    def add_bot_callback(self, bot_callback):
        self.bot_callback = bot_callback

    def toggle_hidden(self):
        self.hidden = not self.hidden
        for row in self.cell_list:
            for cell in row:
                cell.toggle_hidden(self.hidden)

        if self.hidden:
            self.ship_selector.grid_forget()
        else:
            self.ship_selector.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

    def toggle_selector_rotation(self, _):
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
        [self.ship_selector.enable_selector(ship.name, enable) for ship in ShipType]
        if enable:
            self.master.master.bind("<BackSpace>", self.toggle_selector_rotation)
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

                if True:#not sum(self.ships_counts.values()):
                    self.play_button.grid(row=10, column=0, padx=5, pady=5, sticky="sew")

    def ship_unset_func(self, positions, shiptype):
        for pos in positions:
            for x in range(pos[0]-1, pos[0]+2):
                for y in range(pos[1]-1, pos[1]+2):
                    if x in range(10) and y in range(10):
                        self.cell_list[y][x].set_state(None)
        self.ships[shiptype.name] = [ship for ship in self.ships[shiptype.name] if ship.is_me(positions[0])]
        self.ships_counts[shiptype.name] += 1
        if sum(self.ships_counts.values()):
            self.play_button.grid_forget()

    def bombs_enable(self, enable):
        for row in self.cell_list:
            for cell in row:
                cell.bombs_enable(enable)

    def win_window(self):
        Reload("You win", self.reload)
        

    def bomb_action(self, position)->bool:
        for y in range(position[1]):
            self.cell_list[y][position[0]].bomb_on_hover(True)
            [x for x in range(10000)] 
            self.cell_list[y][position[0]].bomb_on_hover(False)
        
        self.cell_list[position[1]][position[0]].bomb_action()
        self.check_alive()
        for ship in self.ships.value():
            if ship.is_me(position):
                return not ship.check_alive()
        return -1

    def check_alive(self):
        flag = not sum([ship.check_alive() for ship in self.ships.values()])
        if self.hidden:
            return flag 
        elif flag: 
            Reload("You lost", self.reload) 

    def play_game(self):
        self.enable_ship_selector(False)
        

    def reload(self):
        self.enable_ship_selector(True)
        

