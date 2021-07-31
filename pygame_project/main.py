import pygame
import random
import sys
from pygame.locals import DOUBLEBUF, KEYUP, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE, QUIT

pygame.init()

NUM_SHAPES = 5
PUZZLE_COLUMNS = 6
PUZZLE_ROWS = 12
SHAPE_WIDTH = 50
SHAPE_HEIGHT = 50

FPS = 15
WINDOW_WIDTH = PUZZLE_COLUMNS * SHAPE_WIDTH
WINDOW_HEIGHT = PUZZLE_ROWS * SHAPE_HEIGHT + 75

BACKGROUND = pygame.image.load("images/background.png")

JEWEL_1 = pygame.image.load("images/jewel_1.png")
JEWEL_2 = pygame.image.load("images/jewel_2.png")
JEWEL_3 = pygame.image.load("images/jewel_3.png")
JEWEL_4 = pygame.image.load("images/jewel_4.png")
JEWEL_5 = pygame.image.load("images/jewel_5.png")
SHAPES_LIST = [JEWEL_1, JEWEL_2, JEWEL_3, JEWEL_4, JEWEL_5]

BLANK = pygame.image.load("images/background.png")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT_SIZE = 36
TEXT_OFFSET = 5

MINIMUM_MATCH = 3
SINGLE_POINTS = 1
DOUBLE_POINTS = 3
TRIPLE_POINTS = 9
EXTRA_LENGTH_POINTS = 0
RANDOM_POINTS = 1

FPS_CLOCK = pygame.time.Clock()
DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF)
pygame.display.set_caption("Puzzle")


def main():
    global score
    global selector

    jewels_board = generate_random_board()
    selector = (0, 0)
    score = 0
    last_move_time = pygame.time.get_ticks()

    blit_board(jewels_board)
    draw_selector(selector)
    remove_matches(jewels_board, selector)

    blit_board(jewels_board)
    blit_score(score)
    draw_selector(selector)

    while True:
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_RIGHT and selector[0] < (PUZZLE_COLUMNS - 2):
                    selector = (selector[0] + 1, selector[1])
                if event.key == K_LEFT and selector[0] > 0:
                    selector = (selector[0] - 1, selector[1])
                if event.key == K_DOWN and selector[1] < (PUZZLE_ROWS - 1):
                    selector = (selector[0], selector[1] + 1)
                if event.key == K_UP and selector[1] > 0:
                    selector = (selector[0], selector[1] - 1)
                if event.key == K_SPACE:
                    last_move_time = pygame.time.get_ticks()

                    swap_pieces(selector, jewels_board)
                    if find_matches(jewels_board):
                        remove_matches(jewels_board, selector)
                    else:
                        swap_pieces(selector, jewels_board)

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        blit_board(jewels_board)
        blit_score(score)
        draw_selector(selector)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def generate_random_board():
    return [[random.choice(SHAPES_LIST) for _ in range(PUZZLE_COLUMNS)] for _ in range(PUZZLE_ROWS)]


def blit_score(score):
    font = pygame.font.Font(None, FONT_SIZE)
    text = font.render("Score: " + str(score), True, BLACK)
    DISPLAY_SURFACE.blit(text, (TEXT_OFFSET, WINDOW_HEIGHT - FONT_SIZE))


def blit_board(board):
    DISPLAY_SURFACE.blit(BACKGROUND, (0, 0))
    row_num = 0
    for row in board:
        column_num = 0
        for shape in row:
            DISPLAY_SURFACE.blit(shape, (SHAPE_WIDTH * column_num, SHAPE_HEIGHT * row_num))
            column_num += 1
        row_num += 1


def draw_selector(position):
    top_left = (position[0] * SHAPE_WIDTH, position[1] * SHAPE_HEIGHT)
    top_right = (top_left[0] + SHAPE_WIDTH * 2, top_left[1])
    bottom_left = (top_left[0], top_left[1] + SHAPE_HEIGHT)
    bottom_right = (top_right[0], top_right[1] + SHAPE_HEIGHT)
    pygame.draw.lines(DISPLAY_SURFACE, WHITE, True, [top_left, top_right, bottom_right, bottom_left], 3)


def swap_pieces(position, board):
    x, y = position
    board[y][x + 1], board[y][x] = board[y][x], board[y][x + 1]


def remove_matches(board, selector):
    matches = find_matches(board)

    while matches:
        score_matches(board, selector, matches)
        clear_matches(board, matches)
        refill_columns(board)
        matches = find_matches(board)
        selector = (0, 0)


def score_matches(board, selector, matches):
    global score
    player_matches = []

    selector = (selector[1], selector[0])

    for match in matches:
        for position in match:
            if (position == selector or position == (selector[0], selector[1] + 1)) and (not match in player_matches):
                player_matches.append(match)

    if len(player_matches) == 1:
        score += SINGLE_POINTS
    elif len(player_matches) == 2:
        score += DOUBLE_POINTS
    elif len(player_matches) == 3:
        score += TRIPLE_POINTS

    for match in player_matches:
        score += int((len(match) - MINIMUM_MATCH) * EXTRA_LENGTH_POINTS)

    for match in matches:
        if match not in player_matches:
            score += RANDOM_POINTS


def find_matches(board):
    clear_list = []

    for column in range(PUZZLE_COLUMNS):
        length = 1
        for row in range(1, PUZZLE_ROWS):
            if board[row][column] == board[row - 1][column]:
                length += 1

            if not board[row][column] == board[row - 1][column]:
                if length >= MINIMUM_MATCH:
                    match = []
                    for clearRow in range(row - length, row):
                        match.append((clearRow, column))
                    clear_list.append(match)
                length = 1

            if row == PUZZLE_ROWS - 1:
                if length >= MINIMUM_MATCH:
                    match = []
                    for clearRow in range(row - (length - 1), row + 1):
                        match.append((clearRow, column))
                    clear_list.append(match)

    for row in range(PUZZLE_ROWS):
        length = 1
        for column in range(1, PUZZLE_COLUMNS):
            if board[row][column] == board[row][column - 1]:
                length += 1

            if not board[row][column] == board[row][column - 1]:
                if length >= MINIMUM_MATCH:
                    match = []
                    for clear_column in range(column - length, column):
                        match.append((row, clear_column))
                    clear_list.append(match)
                length = 1

            if column == PUZZLE_COLUMNS - 1:
                if length >= MINIMUM_MATCH:
                    match = []
                    for clear_column in range(column - (length - 1), column + 1):
                        match.append((row, clear_column))
                    clear_list.append(match)

    return clear_list


def clear_matches(board, matches):
    for match in matches:
        for position in match:
            row, column = position
            board[row][column] = BLANK


def refill_columns(board):
    for column in range(PUZZLE_COLUMNS):
        for row in range(PUZZLE_ROWS):
            if board[row][column] == BLANK:
                test = 0
                length = 0

                while row + test < PUZZLE_ROWS and board[row + test][column] == BLANK:
                    length += 1
                    test += 1

                for blank_row in range(row, PUZZLE_ROWS):
                    try:
                        board[blank_row][column] = board[blank_row + length][column]
                    except IndexError:
                        board[blank_row][column] = SHAPES_LIST[random.randrange(0, len(SHAPES_LIST))]


if __name__ == '__main__':
    main()
