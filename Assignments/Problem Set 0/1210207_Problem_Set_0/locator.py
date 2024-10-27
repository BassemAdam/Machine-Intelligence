from typing import Any, Set, Tuple
from grid import Grid


def locate(grid: Grid, item: Any) -> Set[Tuple[int,int]]:
    '''
    This function takes a 2D grid and an item
    It should return a list of (x, y) coordinates that specify the locations that contain the given item
    To know how to use the Grid class, see the file "grid.py"  
    '''
    positions = set()
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[x, y] == item:
                 positions.add((x, y))
    return positions