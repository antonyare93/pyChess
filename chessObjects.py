import pickle
import os

class Piece():
    def __init__(self, figure: str, color: str, position: tuple) -> None:
        self.figure = figure
        self.color = color
        self.position = position
        self.has_moved = False
        self.points = self._get_points(figure)
    
    def _get_points(self, figure: str) -> int:
        points_map = {
            "K": 0,  # Añadido el Rey
            "Q": 9,
            "R": 5,
            "B": 3,
            "N": 3,
            "p": 1
        }
        return points_map.get(figure, 0)

class GameBoard():
    def __init__(self) -> None:
        self.cells = tuple(tuple((i, j) for j in range(8)) for i in range(8))
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.userEquivalency = self._create_user_equivalency()
    
    def _create_user_equivalency(self) -> list:
        files = "ABCDEFGH"
        return [[f'{files[j]}{8-i}' for j in range(8)] for i in range(8)]
    
    def get_square_notation(self, position: tuple) -> str:
        i, j = position
        return self.userEquivalency[i][j]

class GameStart():
    def __init__(self) -> None:
        self.board = GameBoard()
        self.pieces = []
        self._initialize_pieces()
        self.white_points = 0
        self.black_points = 0
        self.current_turn = "white"
        self.is_game_over = False
        self.winner = None
        self.save_file = "chess_save.chssv"
    
    def _initialize_pieces(self) -> None:
        # Inicializar piezas blancas
        self._setup_back_rank("white", 7) 
        self._setup_pawns("white", 6)
        
        # Inicializar piezas negras
        self._setup_back_rank("black", 0)  
        self._setup_pawns("black", 1)
    
    def _setup_back_rank(self, color: str, rank: int) -> None:
        piece_order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for file in range(8):
            piece = Piece(piece_order[file], color, (rank, file))
            self.pieces.append(piece)
            self.board.board[rank][file] = piece
    
    def _setup_pawns(self, color: str, rank: int) -> None:
        for file in range(8):
            piece = Piece("p", color, (rank, file))
            self.pieces.append(piece)
            self.board.board[rank][file] = piece
    
    def __str__(self) -> str:
        # Caracteres Unicode para las piezas de ajedrez
        piece_symbols = {
            'K': {'white': '♚', 'black': '♔'},
            'Q': {'white': '♛', 'black': '♕'},
            'R': {'white': '♜', 'black': '♖'},
            'B': {'white': '♝', 'black': '♗'},
            'N': {'white': '♞', 'black': '♘'},
            'p': {'white': '♟', 'black': '♙'}
        }
        
        # Crear el tablero como string
        board_str = "\n  A B C D E F G H\n"
        for i in range(8):
            board_str += f"{8-i} "
            for j in range(8):
                piece = self.board.board[i][j]
                if piece is None:
                    # Alternar colores de casillas vacías
                    square = "□" if (i + j) % 2 == 0 else "■"
                else:
                    # Obtener el símbolo Unicode correspondiente
                    square = piece_symbols[piece.figure][piece.color]
                board_str += square + " "
            board_str += f"{8-i}\n"
        board_str += "  A B C D E F G H"
        
        return board_str

    def make_move(self, from_pos: str, to_pos: str) -> bool:
        # Convertir notación de usuario (ej: "E2") a coordenadas del tablero (ej: (6,4))
        from_coords = self._get_coords(from_pos)
        to_coords = self._get_coords(to_pos)
        
        if not from_coords or not to_coords:
            return False
        
        piece = self.board.board[from_coords[0]][from_coords[1]]
        
        # Verificar si hay una pieza en la posición inicial
        if not piece:
            return False
            
        # Verificar si es el turno correcto
        if piece.color != self.current_turn:
            return False
            
        # Verificar movimiento especial de peón (doble paso inicial)
        if piece.figure == "p" and not piece.has_moved:
            from_rank, from_file = from_coords
            to_rank, to_file = to_coords
            
            # Verificar si es movimiento vertical y de dos casillas
            if from_file == to_file and abs(to_rank - from_rank) == 2:
                # Verificar dirección correcta según color
                if (piece.color == "white" and to_rank - from_rank == 2) or \
                   (piece.color == "black" and to_rank - from_rank == -2):
                    # Verificar que no haya piezas en el camino
                    middle_rank = (from_rank + to_rank) // 2
                    if self.board.board[middle_rank][from_file] is None and \
                       self.board.board[to_rank][to_file] is None:
                        # Realizar el movimiento
                        self.board.board[from_rank][from_file] = None
                        self.board.board[to_rank][to_file] = piece
                        piece.position = to_coords
                        piece.has_moved = True
                        self.current_turn = "black" if self.current_turn == "white" else "white"
                        return True
        
        # Verificar la casilla destino
        target = self.board.board[to_coords[0]][to_coords[1]]
        
        # No se puede capturar una pieza del mismo color
        if target and target.color == piece.color:
            return False
            
        # No se puede capturar un rey
        if target and target.figure == "K":
            return False
            
        # Realizar el movimiento
        if target:  # Captura
            if piece.color == "white":
                self.white_points += target.points
            else:
                self.black_points += target.points
                
        # Actualizar el tablero
        self.board.board[from_coords[0]][from_coords[1]] = None
        self.board.board[to_coords[0]][to_coords[1]] = piece
        piece.position = to_coords
        piece.has_moved = True
        
        # Cambiar el turno
        self.current_turn = "black" if self.current_turn == "white" else "white"
        
        return True

    def _get_coords(self, notation: str) -> tuple:
        """Convierte notación de ajedrez (ej: 'E2') a coordenadas del tablero (ej: (6,4))"""
        if len(notation) != 2:
            return None
            
        file = ord(notation[0].upper()) - ord('A')
        rank = 8 - int(notation[1])
        
        if not (0 <= file <= 7 and 0 <= rank <= 7):
            return None
            
        return (rank, file)

    def save_game(self) -> None:
        """Guarda el estado actual del juego en un archivo binario"""
        game_state = {
            'board': self.board.board,
            'pieces': self.pieces,
            'white_points': self.white_points,
            'black_points': self.black_points,
            'current_turn': self.current_turn,
            'is_game_over': self.is_game_over,
            'winner': self.winner
        }
        
        with open(self.save_file, 'wb') as f:
            pickle.dump(game_state, f)
        print(f"\nPartida guardada en {self.save_file}")

    def load_game(self) -> bool:
        """Carga una partida guardada"""
        try:
            with open(self.save_file, 'rb') as f:
                game_state = pickle.load(f)
                
            self.board.board = game_state['board']
            self.pieces = game_state['pieces']
            self.white_points = game_state['white_points']
            self.black_points = game_state['black_points']
            self.current_turn = game_state['current_turn']
            self.is_game_over = game_state['is_game_over']
            self.winner = game_state['winner']
            return True
        except Exception as e:
            print(f"Error al cargar la partida: {e}")
            return False

    def delete_save(self) -> None:
        """Elimina el archivo de guardado si existe"""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)

    def play_game(self) -> None:
        # Verificar si existe una partida guardada
        if os.path.exists(self.save_file):
            response = input("Se encontró una partida guardada. ¿Desea continuarla? (s/n): ").lower()
            if response == 's':
                if not self.load_game():
                    print("Iniciando nueva partida...")
                    self.delete_save()
            else:
                self.delete_save()
                print("Iniciando nueva partida...")

        print("¡Bienvenido al juego de ajedrez!")
        print("Comandos especiales:")
        print("- 'resign': para rendirse")
        print("- 'draw': para ofrecer tablas")
        print("- 'quit': para guardar y salir del juego")
        
        while not self.is_game_over:
            os.system('cls' if os.name == 'nt' else 'clear')  # Limpiar pantalla
            print(self)  # Muestra el tablero
            print(f"\nPuntos Blancos: {self.white_points}")
            print(f"Puntos Negros: {self.black_points}")
            print(f"\nTurno de las {self.current_turn}s")
            
            # Obtener movimiento
            while True:
                try:
                    move = input("Ingrese su movimiento (ejemplo: E2 E4) o comando especial: ").strip().lower()
                    
                    # Procesar comandos especiales
                    if move == 'resign':
                        self.winner = 'black' if self.current_turn == 'white' else 'white'
                        self.is_game_over = True
                        break
                    elif move == 'draw':
                        response = input(f"El jugador de {self.current_turn}s ofrece tablas. ¿Aceptar? (s/n): ").lower()
                        if response == 's':
                            self.is_game_over = True
                            break
                        else:
                            print("Tablas rechazadas. Continúa el juego.")
                            continue
                    elif move == 'quit':
                        self.save_game()
                        print("¡Hasta pronto!")
                        return
                    
                    # Procesar movimiento normal
                    from_pos, to_pos = move.split()
                    if self.make_move(from_pos, to_pos):
                        break
                    else:
                        print("Movimiento inválido. Intente de nuevo.")
                
                except ValueError:
                    print("Formato inválido. Use 'desde hacia' (ejemplo: E2 E4)")
                except Exception as e:
                    print(f"Error: {e}")
        
        # El juego ha terminado, eliminar el archivo de guardado si existe
        self.delete_save()
        self._show_game_result()

    def _show_game_result(self) -> None:
        print("\n¡Juego terminado!")
        print(self)  # Mostrar estado final del tablero
        print(f"\nPuntos finales:")
        print(f"Blancos: {self.white_points}")
        print(f"Negros: {self.black_points}")
        
        if self.winner:
            print(f"\n¡Las {self.winner}s ganan!")
        else:
            print("\n¡El juego termina en tablas!")