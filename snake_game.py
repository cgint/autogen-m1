import curses
import random
import time
import json

def init_curses():
    curses.initscr()
    win = curses.newwin(curses.LINES, curses.COLS, 0, 0)
    curses.curs_set(0)
    win.keypad(1)
    win.timeout(100)
    return win

def write_game_state_to_disk(score, snake, food):
    state = {
        'score': score,
        'snake': snake,
        'food': food
    }
    with open('game_state.txt', 'w') as file:
        file.write(json.dumps(state))

def read_game_state_from_disk():
    try:
        with open('game_state.txt', 'r') as file:
            state = json.loads(file.read())
            return state['score'], state['snake'], state['food']
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def game_loop(win):
    key = curses.KEY_RIGHT
    score = 0
    snake = [[4,10], [4,9], [4,8]]
    food = [10, 20]

    if (state := read_game_state_from_disk()) is not None:
        score, snake, food = state

    while True:
        next_key = win.getch()
        key = key if next_key == -1 else next_key

        if snake[0][0] in [0, curses.LINES] or \
            snake[0][1]  in [0, curses.COLS] or \
            snake[0] in snake[1:]:
            write_game_state_to_disk(score, snake, food)
            break

        new_head = [snake[0][0], snake[0][1]]

        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_RIGHT:
            new_head[1] += 1

        snake.insert(0, new_head)

        if snake[0] == food:
            score += 1
            food = None
            while food is None:
                nf = [
                    random.randint(1, curses.LINES-1),
                    random.randint(1, curses.COLS-1)
                ]
                food = nf if nf not in snake else None
            win.addch(food[0], food[1], '*')
        else:
            tail = snake.pop()
            win.addch(tail[0], tail[1], ' ')

        win.addch(snake[0][0], snake[0][1], '#')

if __name__ == "__main__":
    win = init_curses()
    try:
        game_loop(win)
    finally:
        curses.endwin()
