import pygame
import chess
from stockfish import Stockfish
from const import *
from utils import load_pieces, get_legal_moves
import copy

pieces = load_pieces(PIECE_SIZE)

chessboard = pygame.image.load('img/board2.png')
chessboard = pygame.transform.scale(chessboard, (BOARD_WIDTH, BOARD_HEIGHT))

pygame.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)

clock = pygame.time.Clock()

stockfish = Stockfish()

font = pygame.font.Font(None, 32)
white_button = pygame.Rect(WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
black_button = pygame.Rect(WIN_WIDTH // 2 + 20, WIN_HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
# Choosing a side
run = True
side_chosen = False
side = ''
while run and not side_chosen:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if white_button.collidepoint(mouse_pos):
                
                side = 'white'
                side_chosen = True
            elif black_button.collidepoint(mouse_pos):
                side = 'black'
                side_chosen = True

    
    screen.fill((30, 30, 30))

    pygame.draw.rect(screen, (255, 255, 255), white_button)
    pygame.draw.rect(screen, (0, 0, 0), black_button)

    w_text = font.render('White', True, (0, 0, 0))
    screen.blit(w_text, (white_button.x + (white_button.w - w_text.get_width()) // 2, 
                         white_button.y + (white_button.h - w_text.get_height()) // 2))

    b_text = font.render('Black', True, (255, 255, 255))
    screen.blit(b_text, (black_button.x + (black_button.w - b_text.get_width()) // 2, 
                         black_button.y + (black_button.h - b_text.get_height()) // 2))

    pygame.display.flip()  

game_state = chess.Board()

if side.lower() == "black":
    result = stockfish.get_best_move()
    game_state.push_uci(result)
    move_history.append(result)

def handle_click(square):
    global game_state, stockfish
    if selected_piece is not None:
        if square in legal_moves:
            game_state.push(chess.Move(selected_square, square))
            stockfish.set_position(game_state.move_stack)
            result = stockfish.get_best_move()
            game_state.push_uci(result)
            move_history.append(result)
            
        selected_piece = None
        selected_square = None
        selected_rect = None
        legal_moves = []
        offset = None

# Main variables
selected_piece = None
selected_rect = None
legal_moves = []
dragging = False
offset = None
start_dragging = False
click_move = []
move_history = []
move_history_rects = []
game_state_history = [copy.deepcopy(game_state)]

#Main
run = True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            point = pygame.Vector2(x, y)
            for i, rect in enumerate(move_history_rects):
                if rect.collidepoint(point):
                    if i < len(game_state_history):  # Check if i is a valid index
                        # Revert game state to the clicked move
                        game_state = copy.deepcopy(game_state_history[i])
                        stockfish.set_position(game_state.move_stack)
                        # Remove all the moves after the clicked move
                        del move_history[i + 1:]
                        del game_state_history[i + 1:]
                        del move_history_rects[i + 1:]
                    break

        # revert last move
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                for _ in range(2):  # pop two moves
                    if len(game_state.move_stack) > 0:
                        game_state.pop()
                        if move_history:  # check if move_history is not empty
                            move_history.pop()  # also remove the move from move history
                stockfish.set_position(game_state.move_stack)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            square = chess.square(x // SQUARE_SIZE[0], 7 - y // SQUARE_SIZE[1])
            piece = game_state.piece_at(square)
            if event.button == 1:  
                if piece is not None and not dragging:
                    selected_square = square
                    selected_piece = piece
                    selected_rect = pygame.Rect(x - PIECE_SIZE[0] // 2, y - PIECE_SIZE[1] // 2, SQUARE_SIZE[0], SQUARE_SIZE[1])
                    legal_moves = [move for move in game_state.legal_moves if move.from_square == selected_square]
                    offset = x - selected_rect.x, y - selected_rect.y
                    start_dragging = True
                
                elif not dragging:
                    
                    if len(click_move) == 0 and piece is not None:
                        click_move.append(square)
                    
                    elif len(click_move) == 1:
                        click_move.append(square)
                        game_state_history.append(copy.deepcopy(game_state))
                        
                        for move in game_state.legal_moves:
                            if move.from_square == click_move[0] and move.to_square == click_move[1]:
                                game_state.push(move)
                                move_history.append(move.uci())  # add this line
                                stockfish.set_position(game_state.move_stack)
                                result = stockfish.get_best_move()
                                game_state.push_uci(result)
                                move_history.append(result)
                                break

                        click_move = []

        elif event.type == pygame.MOUSEMOTION:
            if start_dragging:
                dragging = True
                start_dragging = False
            if dragging:
                x, y = event.pos
                selected_rect.x = x - offset[0]
                selected_rect.y = y - offset[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                dragging = False
                for move in legal_moves:
                    x, y = chess.square_file(move.to_square), 7 - chess.square_rank(move.to_square)
                    if x * SQUARE_SIZE[0] < selected_rect.x + SQUARE_SIZE[0] / 2 < (x + 1) * SQUARE_SIZE[0] and y * SQUARE_SIZE[1] < selected_rect.y + SQUARE_SIZE[1] / 2 < (y + 1) * SQUARE_SIZE[1]:
                        game_state_history.append(copy.deepcopy(game_state))  # add this line
                        game_state.push(move)
                        move_history.append(move.uci())  # add this line
                        stockfish.set_position(game_state.move_stack)
                        result = stockfish.get_best_move()
                        game_state.push_uci(result)
                        move_history.append(result)
                        break

                selected_piece = None
                selected_square = None
                selected_rect = None
                legal_moves = []
                offset = None

    screen.blit(chessboard, (0, 0))

    for i in range(8):
        for j in range(8):
            piece = game_state.piece_at(chess.square(i, j))
            if piece and (selected_piece is None or chess.square(i, j) != selected_square):
                square_x = i * SQUARE_SIZE[0]
                square_y = (7 - j) * SQUARE_SIZE[1]
                piece_x = square_x + (SQUARE_SIZE[0] - pieces[str(piece)].get_width()) // 2
                piece_y = square_y + (SQUARE_SIZE[1] - pieces[str(piece)].get_height()) // 2
                screen.blit(pieces[str(piece)], (piece_x, piece_y))

    if selected_piece is not None and selected_rect is not None:
        screen.blit(pieces[str(selected_piece)], (selected_rect.x, selected_rect.y))

    if legal_moves:
        for move in legal_moves:
            x, y = move.to_square % 8, 7 - move.to_square // 8
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x * SQUARE_SIZE[0], y * SQUARE_SIZE[1], SQUARE_SIZE[0], SQUARE_SIZE[1]), 2)
        # Display move history
    for i, move in enumerate(move_history):
        move_text = font.render(move, True, (255, 255, 255))
        rect = pygame.Rect(WIN_WIDTH * 0.75, 20 + i * 20, move_text.get_width(), move_text.get_height())
        move_history_rects.append(rect)
        screen.blit(move_text, (rect.x, rect.y))  # Adjusted position

    pygame.display.flip()
    clock.tick(60)
pygame.quit()