import tkinter as tk
import random
from tkinter import messagebox

class Minesweeper:
    def __init__(self, master, rows=10, cols=10, mines=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.buttons = []
        self.mine_locations = set()
        self.flagged = set()
        self.revealed = set()
        
        self.setup_ui()
        self.place_mines()

    def setup_ui(self):
        """Creates the grid of buttons."""
        for r in range(self.rows):
            row_btns = []
            for c in range(self.cols):
                btn = tk.Button(self.master, width=3, height=1, 
                                command=lambda r=r, c=c: self.click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.toggle_flag(r, c))
                btn.grid(row=r, column=c)
                row_btns.append(btn)
            self.buttons.append(row_btns)

    def place_mines(self):
        """Randomly distributes mines across the grid."""
        while len(self.mine_locations) < self.mines:
            loc = (random.randint(0, self.rows-1), random.randint(0, self.cols-1))
            self.mine_locations.add(loc)

    def get_neighbors(self, r, c):
        """Returns valid adjacent coordinates."""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def count_adjacent_mines(self, r, c):
        return sum(1 for nr, nc in self.get_neighbors(r, c) if (nr, nc) in self.mine_locations)

    def toggle_flag(self, r, c):
        if (r, c) in self.revealed: return
        if (r, c) in self.flagged:
            self.flagged.remove((r, c))
            self.buttons[r][c].config(text="", fg="black")
        else:
            self.flagged.add((r, c))
            self.buttons[r][c].config(text="🚩", fg="red")

    def click(self, r, c):
        if (r, c) in self.flagged or (r, c) in self.revealed:
            return

        if (r, c) in self.mine_locations:
            self.game_over(False)
            return

        self.reveal(r, c)
        
        if len(self.revealed) == (self.rows * self.cols) - self.mines:
            self.game_over(True)

    def reveal(self, r, c):
        if (r, c) in self.revealed: return
        self.revealed.add((r, c))
        
        count = self.count_adjacent_mines(r, c)
        self.buttons[r][c].config(text=str(count) if count > 0 else "", 
                                  relief=tk.SUNKEN, bg="#ececec")
        
        if count == 0:
            for nr, nc in self.get_neighbors(r, c):
                self.reveal(nr, nc)

    def game_over(self, won):
        for (r, c) in self.mine_locations:
            self.buttons[r][c].config(text="💣", bg="red" if not won else "green")
        
        msg = "You Win!" if won else "BOOM! Game Over."
        messagebox.showinfo("Minesweeper", msg)
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper")
    game = Minesweeper(root)
    root.mainloop()