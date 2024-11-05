import tkinter as tk
import random
import logging

def main():
    global root, game_over, status_label, frame, rows_entry, cols_entry, bombs_entry
    root = tk.Tk()  # Initialize window
    root.title("MineSweeper")
    root.geometry("400x400")

    # Display game title
    game_name = tk.Label(root, text='MineSweeper')
    game_name.pack()

    # Input fields for customizing the board
    input_frame = tk.Frame(root)
    input_frame.pack()

    tk.Label(input_frame, text="Rows:").grid(row=0, column=0)
    rows_entry = tk.Entry(input_frame, width=5)
    rows_entry.grid(row=0, column=1)
    rows_entry.insert(0, "5")  # Default value

    tk.Label(input_frame, text="Columns:").grid(row=1, column=0)
    cols_entry = tk.Entry(input_frame, width=5)
    cols_entry.grid(row=1, column=1)
    cols_entry.insert(0, "5")  # Default value

    tk.Label(input_frame, text="Bombs:").grid(row=2, column=0)
    bombs_entry = tk.Entry(input_frame, width=5)
    bombs_entry.grid(row=2, column=1)
    bombs_entry.insert(0, "5")  # Default value

    # Status label
    status_label = tk.Label(root, text="Game in progress", fg="black")
    status_label.pack()

    # Create a frame to hold the game board (grid of buttons)
    frame = tk.Frame(root)
    frame.pack()  # Pack the frame into the root window

    # Start Game button
    start_button = tk.Button(root, text="Start Game", command=reset_game)
    start_button.pack()

    # Initialize game state
    game_over = False
    root.mainloop()

def Minesweeper(x, m, n, frame):
    global buttons, gboard, revealed_count, total_cells, num_bombs
    num_bombs = x
    revealed_count = 0
    total_cells = m * n

    # Generate an empty board with dimension m*n
    gboard = gen_board(m, n)

    # Randomly and uniquely place bombs
    b_points = rchoose(x, m, n)

    # Place bombs on the board
    gboard = replace_arr(gboard, b_points, 'B')
    logging.error(gboard)
    gboard = check_adj_bombs(gboard)

    # Create the Tkinter visual board
    create_board(gboard, frame)

def gen_board(m, n):
    return [[0 for _ in range(n)] for _ in range(m)]

def replace_arr(arr, points, val='B'):
    for (a, b) in points:
        arr[a][b] = val
    return arr

def rchoose(x, m, n): # randomly chooses bombs
    bomb_positions = set()  # Use a set to ensure unique positions
    while len(bomb_positions) < x:
        bomb_positions.add((random.randint(0, m - 1), random.randint(0, n - 1)))
    return list(bomb_positions)

def check_adj_bombs(board):
    rows = len(board)
    cols = len(board[0])
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 'B':
                continue  # Skip if the cell is a bomb

            bomb_count = 0
            for dx, dy in directions:
                ni, nj = i + dx, j + dy
                if 0 <= ni < rows and 0 <= nj < cols and board[ni][nj] == 'B':
                    bomb_count += 1

            board[i][j] = bomb_count

    return board

def reveal_cells(x, y):
    global revealed_count, game_over
    if game_over or buttons[x][y]["text"] != "":
        return  # Do nothing if the game is over or the cell is already revealed

    # Reveal current cell
    buttons[x][y].config(text=str(gboard[x][y]), bg="lightgrey")
    revealed_count += 1

    # Check for winning condition
    if revealed_count == total_cells - num_bombs:
        game_over = True
        end_game(win=True)
        return

    if gboard[x][y] == 0:
        # Recursively reveal neighboring cells if current cell is 0
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            ni, nj = x + dx, y + dy
            if 0 <= ni < len(gboard) and 0 <= nj < len(gboard[0]):
                reveal_cells(ni, nj)

def on_right_click(event, x, y):
    if game_over or buttons[x][y]["text"] in ["", "F"]:
        if buttons[x][y]["text"] == "F":
            buttons[x][y].config(text="", fg="black")  # Remove the flag
        else:
            buttons[x][y].config(text="F", fg="blue")  # Place a flag

def end_game(win=False):
    global game_over
    game_over = True
    if win:
        status_label.config(text="Congratulations! You've won!", fg="green")
    else:
        status_label.config(text="Boom! Game Over!", fg="red")

    # Reveal all bombs and disable all buttons
    for i in range(len(gboard)):
        for j in range(len(gboard[0])):
            if gboard[i][j] == 'B':
                buttons[i][j].config(text="B", bg="red")
            buttons[i][j].config(state="disabled")

def reset_game():
    global game_over
    game_over = False

    # Clear the frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Get values from the input fields
    try:
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
        bombs = int(bombs_entry.get())

        if bombs >= rows * cols:
            status_label.config(text="Too many bombs!", fg="red")
            return
    except ValueError:
        status_label.config(text="Invalid input!", fg="red")
        return

    status_label.config(text="Game in progress", fg="black")
    Minesweeper(bombs, rows, cols, frame)

def create_board(board, frame):
    global buttons
    buttons = [[None for _ in range(len(board[0]))] for _ in range(len(board))]

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            def on_click(x=i, y=j):
                if game_over:
                    return
                if board[x][y] == 'B':
                    end_game(win=False)
                else:
                    reveal_cells(x, y)

            button = tk.Button(frame, text="", width=4, height=2, command=on_click)
            button.grid(row=i, column=j, padx=1, pady=1)
            button.bind("<Button-3>", lambda event, x=i, y=j: on_right_click(event, x, y))
            buttons[i][j] = button

# Start the program
main()
