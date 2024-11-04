class Piece():
    figure: str
    color: str
    position: tuple
    points: int

    def __init__(self, figure: str, color: str, position: tuple) -> None:
        self.figure = figure
        self.color = color
        self.position = position
        match figure:
            case "Q":
                self.points = 9
            case "R":
                self.points = 5
            case "B":
                self.points = 3
            case "N":
                self.points = 3
            case "p":
                self.points = 1
        
        

class GameBoard():
    '''
    Creates the Chess table of 2 dimentions of 8x8
    '''
    cells: tuple 
    userEquivalency: tuple
    

    def __init__(self) -> None:
        self.cells = tuple(tuple((i, j) for j in range(8)) for i in range(8))
        self.userEquivalency = tuple(tuple(f'{["A", "B", "C", "D", "E", "F", "G", "H"][i]}{j+1}' for i in range(8)) for j in range(8))