import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False
        
        self.create_widgets()
        self.draw_board()
    
    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.canvas.place(x=150, y=20)
        self.canvas.bind("<Button-1>", self.click_handler)
        
        self.status_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn", 
                                    font=("Arial", 14))
        self.status_label.place(x=200, y=340)
        
        reset_btn = tk.Button(self.root, text="Reset Game", command=self.reset_game)
        reset_btn.place(x=260, y=370)
    
    def draw_board(self):
        self.canvas.delete("all")
        # Draw vertical lines
        for i in range(1, 3):
            self.canvas.create_line(i*100, 0, i*100, 300, width=2)
        # Draw horizontal lines
        for i in range(1, 3):
            self.canvas.create_line(0, i*100, 300, i*100, width=2)
    
    def click_handler(self, event):
        if self.game_over:
            return
            
        col = event.x // 100
        row = event.y // 100
        
        if self.board[row][col] == "":
            self.board[row][col] = self.current_player
            self.draw_symbol(row, col)
            
            if self.check_win():
                self.status_label.config(text=f"Player {self.current_player} wins!")
                self.game_over = True
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
            elif self.check_tie():
                self.status_label.config(text="Game Tied!")
                self.game_over = True
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.status_label.config(text=f"Player {self.current_player}'s turn")
    
    def draw_symbol(self, row, col):
        x = col * 100 + 50
        y = row * 100 + 50
        
        if self.current_player == "X":
            self.canvas.create_line(x-30, y-30, x+30, y+30, width=2, fill="blue")
            self.canvas.create_line(x+30, y-30, x-30, y+30, width=2, fill="blue")
        else:
            self.canvas.create_oval(x-30, y-30, x+30, y+30, width=2, outline="red")
    
    def check_win(self):
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != "":
                return True
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return True
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return True
        return False
    
    def check_tie(self):
        for row in self.board:
            if "" in row:
                return False
        return True
    
    def reset_game(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.draw_board()
        self.status_label.config(text=f"Player {self.current_player}'s turn")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()