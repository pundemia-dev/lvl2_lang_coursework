from enum import Enum
import customtkinter as ctk
from typing import Callable

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
        
    
class Ship:
    def __init__(self, ship_type: ShipType, ship_unset_func):
        self.ship_type = ship_type
        self.cells_list = list()
        self.alive = True

    def add_cell(self, cell):
        if len(self.cells_list) < self.ship_type.cells_count:
            self.cells_list.append(cell)
        else:
            pass # logs
    def is_me(self, position):
        return any(list(map(lambda cell: cell.is_me(position), self.cells_list)))

    def check_alive(self) -> bool:
        return self.alive


class ShipContainer:
    def __init__(self):
        self.alive = True
        self.ships_counts = {ship.name: ship.count for ship in ShipType}
        self.ships = {ship.type: [] for ship in ShipType}
        self.cells_list = []

        self.new_game()
    
    def enable_ship_mapping(self, enable: bool):
        pass

    def ship_on_hover(self, position):
        pass  

    def ship_set(self, position):
        pass 

    def new_game(self):
        pass



