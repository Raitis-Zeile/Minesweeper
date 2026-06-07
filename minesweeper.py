import tkinter as tk
from tkinter import messagebox
import random


class Minesweeper:
    COLORS = {
        1: "blue",
        2: "green",
        3: "red",
        4: "navy",
        5: "maroon",
        6: "teal",
        7: "black",
        8: "gray"
    }

    def __init__(self, master, rows=9, cols=9, mines=10):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines

        self.buttons = []
        self.mine_locations = set()
        self.flagged = set()
        self.revealed = set()

        self.first_click = True
        self.game_ended = False
        self.seconds = 0

        self.create_ui()

        self.update_timer()

    def create_ui(self):
        top = tk.Frame(self.master)
        top.pack(pady=5)

        self.mine_label = tk.Label(
            top,
            text=f"Mines Left: {self.mines}",
            font=("Arial", 11, "bold")
        )
        self.mine_label.pack(side=tk.LEFT, padx=10)

        self.timer_label = tk.Label(
            top,
            text="Time: 0",
            font=("Arial", 11, "bold")
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.difficulty = tk.StringVar(value="Easy")

        menu = tk.OptionMenu(
            top,
            self.difficulty,
            "Easy",
            "Medium",
            "Hard"
        )
        menu.pack(side=tk.LEFT, padx=10)

        restart_btn = tk.Button(
            top,
            text="Restart",
            command=self.restart_game
        )
        restart_btn.pack(side=tk.LEFT)

        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.pack()

        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                btn = tk.Button(
                    self.grid_frame,
                    width=3,
                    height=1,
                    font=("Arial", 10, "bold"),
                    command=lambda r=r, c=c: self.click(r, c)
                )

                btn.bind(
                    "<Button-3>",
                    lambda e, r=r, c=c: self.toggle_flag(r, c)
                )

                btn.grid(row=r, column=c)

                row.append(btn)

            self.buttons.append(row)

    def restart_game(self):
        difficulty = self.difficulty.get()

        settings = {
            "Easy": (9, 9, 10),
            "Medium": (16, 16, 40),
            "Hard": (16, 30, 99)
        }

        rows, cols, mines = settings[difficulty]

        self.master.destroy()

        root = tk.Tk()
        root.title("Minesweeper")

        Minesweeper(root, rows, cols, mines)

        root.mainloop()

    def update_timer(self):
        if not self.game_ended:
            self.timer_label.config(text=f"Time: {self.seconds}")
            self.seconds += 1
            self.master.after(1000, self.update_timer)

    def place_mines_safe(self, safe_r, safe_c):
        forbidden = {(safe_r, safe_c)}

        for nr, nc in self.get_neighbors(safe_r, safe_c):
            forbidden.add((nr, nc))

        while len(self.mine_locations) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            if (r, c) not in forbidden:
                self.mine_locations.add((r, c))

    def get_neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):

                if dr == 0 and dc == 0:
                    continue

                nr = r + dr
                nc = c + dc

                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def count_adjacent_mines(self, r, c):
        return sum(
            1
            for nr, nc in self.get_neighbors(r, c)
            if (nr, nc) in self.mine_locations
        )

    def toggle_flag(self, r, c):
        if self.game_ended:
            return

        if (r, c) in self.revealed:
            return

        if (r, c) in self.flagged:
            self.flagged.remove((r, c))
            self.buttons[r][c].config(text="")
        else:
            self.flagged.add((r, c))
            self.buttons[r][c].config(text="🚩")

        remaining = self.mines - len(self.flagged)
        self.mine_label.config(text=f"Mines Left: {remaining}")

    def click(self, r, c):
        if self.game_ended:
            return

        if (r, c) in self.flagged:
            return

        if (r, c) in self.revealed:
            return

        if self.first_click:
            self.place_mines_safe(r, c)
            self.first_click = False

        if (r, c) in self.mine_locations:
            self.game_over(False)
            return

        self.reveal(r, c)

        if len(self.revealed) == (self.rows * self.cols) - self.mines:
            self.game_over(True)

    def reveal(self, r, c):
        if (r, c) in self.revealed:
            return

        self.revealed.add((r, c))

        count = self.count_adjacent_mines(r, c)

        btn = self.buttons[r][c]

        btn.config(
            relief=tk.SUNKEN,
            bg="#e0e0e0",
            state=tk.DISABLED
        )

        if count > 0:
            btn.config(
                text=str(count),
                fg=self.COLORS.get(count, "black")
            )
        else:
            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in self.revealed:
                    self.reveal(nr, nc)

    def game_over(self, won):
        self.game_ended = True

        for r, c in self.mine_locations:
            self.buttons[r][c].config(
                text="💣",
                bg="green" if won else "red"
            )

        if won:
            messagebox.showinfo(
                "Victory!",
                f"You won in {self.seconds} seconds!"
            )
        else:
            messagebox.showinfo(
                "Game Over",
                "BOOM! You hit a mine."
            )

    # BONUS: Chord Click Support
    def chord_click(self, r, c):
        if (r, c) not in self.revealed:
            return

        count = self.count_adjacent_mines(r, c)

        flags = sum(
            1
            for nr, nc in self.get_neighbors(r, c)
            if (nr, nc) in self.flagged
        )

        if flags == count:
            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in self.flagged:
                    self.click(nr, nc)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper")

    Minesweeper(root, 9, 9, 10)

    root.mainloop()