import tkinter as tk
from tkinter import messagebox, font as tkfont
import random
from collections import deque



PERKS = {
    "Iron Will":     "Start each floor with +1 extra life (once per run).",
    "Eagle Eye":     "One random safe cell is auto-revealed each floor.",
    "Cartographer":  "Corner cells are always revealed for you.",
    "Scavenger":     "Flagging a mine gives +5 XP bonus.",
    "Berserker":     "Chord-click reveals 1 extra unrevealed neighbor.",
    "Sixth Sense":   "One mine location is briefly shown at floor start.",
    "Lucky Charm":   "Bomb cells have a 15 % chance to be duds (safe).",
    "Pathfinder":    "First click always opens a large clear area.",
}

FLOOR_THEMES = [
    ("Dungeon",   "#1a1a2e", "#e8c97a", "💀"),
    ("Crypt",     "#0d1b2a", "#9fbbcc", "🕯️"),
    ("Cavern",    "#1c1c1e", "#b87333", "⛏️"),
    ("Abyss",     "#0a0a14", "#7b68ee", "🌀"),
    ("Hellgate",  "#1a0000", "#ff6b6b", "🔥"),
    ("Void",      "#050510", "#00ffcc", "⭐"),
]

NUMBER_COLORS = {
    1: "#6ec6ff",
    2: "#81c784",
    3: "#e57373",
    4: "#9575cd",
    5: "#ff8a65",
    6: "#4dd0e1",
    7: "#f06292",
    8: "#eeeeee",
}

XP_PER_SAFE  = 2
XP_PER_FLAG  = 5
XP_PER_FLOOR = 30
XP_LEVEL_BASE = 60   
XP_LEVEL_SCALE = 1.4


def xp_for_level(level):
    return int(XP_LEVEL_BASE * (XP_LEVEL_SCALE ** (level - 1)))


def floor_config(floor_num):
    """Return (rows, cols, mines) for a given floor."""
    rows = min(9 + (floor_num - 1) * 2, 20)
    cols = min(9 + (floor_num - 1) * 2, 30)
    base_cells = rows * cols
    density = min(0.12 + (floor_num - 1) * 0.015, 0.30)
    mines = max(10, int(base_cells * density))
    return rows, cols, mines




class RogueMinesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("MineSweeper Roguelike")
        self.master.configure(bg="#0d0d1a")
        self._run_state_defaults()
        self.show_title_screen()


    def _run_state_defaults(self):
        self.floor        = 0
        self.lives        = 3
        self.player_xp    = 0
        self.player_level = 1
        self.xp_to_next   = xp_for_level(1)
        self.perks        = []        
        self.score        = 0
        self.total_flags  = 0
        self.floors_cleared = 0


    def show_title_screen(self):
        self._clear_window()
        self.master.configure(bg="#0d0d1a")

        wrap = tk.Frame(self.master, bg="#0d0d1a")
        wrap.pack(expand=True, pady=60)

        tk.Label(wrap, text="💣", font=("Segoe UI Emoji", 56),
                 bg="#0d0d1a", fg="#e8c97a").pack()
        tk.Label(wrap, text="MINESWEEPER", font=("Courier New", 32, "bold"),
                 bg="#0d0d1a", fg="#e8c97a").pack()
        tk.Label(wrap, text="R O G U E L I K E", font=("Courier New", 14),
                 bg="#0d0d1a", fg="#7b7b9e").pack(pady=(0, 20))

        tk.Label(wrap,
                 text="Descend through cursed floors.\nFlag every mine. Survive as long as you can.",
                 font=("Courier New", 11), bg="#0d0d1a", fg="#aaaacc",
                 justify="center").pack(pady=(0, 30))

        btn = tk.Button(wrap, text="▶  BEGIN DESCENT",
                        font=("Courier New", 13, "bold"),
                        bg="#e8c97a", fg="#0d0d1a", activebackground="#ffe08a",
                        relief=tk.FLAT, padx=20, pady=10, cursor="hand2",
                        command=self.start_run)
        btn.pack(pady=6)

        tk.Label(wrap,
                 text="Left-click: reveal   Right-click: flag   Middle-click: chord",
                 font=("Courier New", 9), bg="#0d0d1a", fg="#555577").pack(pady=(20, 0))


    def start_run(self):
        self._run_state_defaults()
        self.next_floor()


    def show_perk_screen(self, callback):
        self._clear_window()
        bg = "#0d0d1a"
        self.master.configure(bg=bg)

        wrap = tk.Frame(self.master, bg=bg)
        wrap.pack(expand=True, pady=40)

        tk.Label(wrap, text="⚡  LEVEL UP!", font=("Courier New", 22, "bold"),
                 bg=bg, fg="#e8c97a").pack(pady=(0, 6))
        tk.Label(wrap, text=f"You reached level {self.player_level}. Choose a perk:",
                 font=("Courier New", 11), bg=bg, fg="#aaaacc").pack(pady=(0, 20))

    
        available = [p for p in PERKS if p not in self.perks]
        choices = random.sample(available, min(3, len(available)))
        if not choices:
            callback()
            return

        for perk in choices:
            pf = tk.Frame(wrap, bg="#1a1a30", bd=0, relief=tk.FLAT)
            pf.pack(fill=tk.X, padx=40, pady=5, ipadx=10, ipady=8)

            tk.Label(pf, text=f"  {perk}",
                     font=("Courier New", 12, "bold"),
                     bg="#1a1a30", fg="#e8c97a", anchor="w").pack(fill=tk.X)
            tk.Label(pf, text=f"  {PERKS[perk]}",
                     font=("Courier New", 9),
                     bg="#1a1a30", fg="#aaaacc", anchor="w", wraplength=400,
                     justify="left").pack(fill=tk.X)

            def pick(p=perk, cb=callback):
                self.perks.append(p)
                self._apply_permanent_perk(p)
                cb()

            tk.Button(pf, text="Choose →",
                      font=("Courier New", 10, "bold"),
                      bg="#e8c97a", fg="#0d0d1a", activebackground="#ffe08a",
                      relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
                      command=pick).pack(anchor="e", padx=6, pady=4)

    def _apply_permanent_perk(self, perk):
        if perk == "Iron Will":
            self.lives += 1


    def next_floor(self):
        self.floor += 1

        self._start_floor()

    def _start_floor(self):
        self._clear_window()
        rows, cols, mines = floor_config(self.floor)
        theme = FLOOR_THEMES[(self.floor - 1) % len(FLOOR_THEMES)]
        self._build_floor(rows, cols, mines, theme)


    def _build_floor(self, rows, cols, mines, theme):
        self.rows        = rows
        self.cols        = cols
        self.mine_count  = mines
        self.theme       = theme
        self.theme_bg, self.theme_fg, self.theme_icon = theme[1], theme[2], theme[3]

        self.buttons       = []
        self.mine_locs     = set()
        self.flagged       = set()
        self.revealed      = set()
        self.duds          = set() 
        self.first_click   = True
        self.floor_ended   = False
        self.floor_seconds = 0

        self.master.configure(bg=self.theme_bg)


        hud = tk.Frame(self.master, bg=self.theme_bg)
        hud.pack(fill=tk.X, padx=8, pady=4)


        left = tk.Frame(hud, bg=self.theme_bg)
        left.pack(side=tk.LEFT)

        self.mine_lbl = tk.Label(left, text=f"💣 {self.mine_count}",
                                  font=("Courier New", 11, "bold"),
                                  bg=self.theme_bg, fg=self.theme_fg)
        self.mine_lbl.pack(side=tk.LEFT, padx=6)

        self.timer_lbl = tk.Label(left, text="⏱ 0",
                                   font=("Courier New", 11, "bold"),
                                   bg=self.theme_bg, fg=self.theme_fg)
        self.timer_lbl.pack(side=tk.LEFT, padx=6)


        center = tk.Frame(hud, bg=self.theme_bg)
        center.pack(side=tk.LEFT, expand=True)

        tk.Label(center,
                 text=f"{self.theme_icon}  FLOOR {self.floor}  {self.theme_icon}",
                 font=("Courier New", 13, "bold"),
                 bg=self.theme_bg, fg=self.theme_fg).pack()


        right = tk.Frame(hud, bg=self.theme_bg)
        right.pack(side=tk.RIGHT)

        self.lives_lbl = tk.Label(right, text=self._lives_text(),
                                   font=("Courier New", 11, "bold"),
                                   bg=self.theme_bg, fg="#ff6b6b")
        self.lives_lbl.pack(side=tk.RIGHT, padx=6)

        self.level_lbl = tk.Label(right, text=f"Lv {self.player_level}",
                                   font=("Courier New", 11, "bold"),
                                   bg=self.theme_bg, fg="#81c784")
        self.level_lbl.pack(side=tk.RIGHT, padx=6)

        self.score_lbl = tk.Label(right, text=f"★ {self.score}",
                                   font=("Courier New", 11, "bold"),
                                   bg=self.theme_bg, fg="#e8c97a")
        self.score_lbl.pack(side=tk.RIGHT, padx=6)


        xp_frame = tk.Frame(self.master, bg=self.theme_bg)
        xp_frame.pack(fill=tk.X, padx=8)
        self.xp_canvas = tk.Canvas(xp_frame, height=6,
                                    bg="#222233", highlightthickness=0)
        self.xp_canvas.pack(fill=tk.X)
        self._redraw_xp_bar()


        if self.perks:
            perk_bar = tk.Frame(self.master, bg=self.theme_bg)
            perk_bar.pack(fill=tk.X, padx=8, pady=2)
            for p in self.perks:
                short = p[:3].upper()
                tk.Label(perk_bar, text=f"[{short}]",
                         font=("Courier New", 8),
                         bg="#1a1a30", fg=self.theme_fg,
                         padx=4).pack(side=tk.LEFT, padx=2)


        grid_wrap = tk.Frame(self.master, bg=self.theme_bg)
        grid_wrap.pack(padx=4, pady=4)

        btn_w = max(2, min(3, 28 // cols))
        btn_font_size = max(7, min(10, 20 // cols * 2))

        for r in range(self.rows):
            row_btns = []
            for c in range(self.cols):
                btn = tk.Button(
                    grid_wrap,
                    width=btn_w, height=1,
                    font=("Courier New", btn_font_size, "bold"),
                    bg="#2a2a44", fg=self.theme_fg,
                    activebackground="#3a3a60",
                    relief=tk.RAISED, bd=1,
                    cursor="hand2",
                    command=lambda r=r, c=c: self.click(r, c)
                )
                btn.bind("<Button-3>",
                         lambda e, r=r, c=c: self.toggle_flag(r, c))
                btn.bind("<Button-2>",
                         lambda e, r=r, c=c: self.chord_click(r, c))
                btn.grid(row=r, column=c, padx=1, pady=1)
                row_btns.append(btn)
            self.buttons.append(row_btns)


        self.master.after(300, self._apply_entrance_perks)


    def _apply_entrance_perks(self):
        """Perks that fire at the start of a floor (before first click)."""
        if "Cartographer" in self.perks:
            corners = [(0,0),(0,self.cols-1),(self.rows-1,0),(self.rows-1,self.cols-1)]

            self._cartographer_pending = True
        if "Sixth Sense" in self.perks:
 
            self._sixth_sense_pending = True


    def _lives_text(self):
        return "❤️ " * self.lives if self.lives > 0 else "💀"

    def _clear_window(self):
        for w in self.master.winfo_children():
            w.destroy()

    def _redraw_xp_bar(self):
        self.xp_canvas.update_idletasks()
        w = self.xp_canvas.winfo_width() or 400
        frac = min(self.player_xp / self.xp_to_next, 1.0)
        self.xp_canvas.delete("all")
        self.xp_canvas.create_rectangle(0, 0, w, 6, fill="#222233", outline="")
        self.xp_canvas.create_rectangle(0, 0, int(w * frac), 6, fill="#81c784", outline="")
        self.xp_canvas.create_text(w // 2, 3,
                                    text=f"XP {self.player_xp}/{self.xp_to_next}",
                                    font=("Courier New", 6), fill="#aaaacc")

    def get_neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def count_adj_mines(self, r, c):
        return sum(1 for nr, nc in self.get_neighbors(r, c)
                   if (nr, nc) in self.mine_locs and (nr, nc) not in self.duds)

    def place_mines(self, safe_r, safe_c):
        forbidden = {(safe_r, safe_c)} | set(self.get_neighbors(safe_r, safe_c))
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)
                     if (r, c) not in forbidden]
        chosen = random.sample(all_cells, min(self.mine_count, len(all_cells)))
        self.mine_locs = set(chosen)


        if "Lucky Charm" in self.perks:
            dud_count = max(1, int(len(self.mine_locs) * 0.15))
            self.duds = set(random.sample(list(self.mine_locs), dud_count))


    def _tick(self):
        if not self.floor_ended:
            self.floor_seconds += 1
            self.timer_lbl.config(text=f"⏱ {self.floor_seconds}")
            self.master.after(1000, self._tick)


    def _gain_xp(self, amount):
        self.player_xp += amount
        levelled = False
        while self.player_xp >= self.xp_to_next:
            self.player_xp -= self.xp_to_next
            self.player_level += 1
            self.xp_to_next = xp_for_level(self.player_level)
            levelled = True
        self._redraw_xp_bar()
        if hasattr(self, "level_lbl"):
            self.level_lbl.config(text=f"Lv {self.player_level}")
        return levelled

  
    def click(self, r, c):
        if self.floor_ended:
            return
        if (r, c) in self.flagged or (r, c) in self.revealed:
            return

        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False
            self.master.after(100, self._tick)
            self._post_first_click_perks(r, c)

        real_mine = (r, c) in self.mine_locs and (r, c) not in self.duds

        if real_mine:
            self._hit_mine(r, c)
            return

        self.reveal(r, c)
        levelled = self._gain_xp(XP_PER_SAFE)
        self.score += 1
        if hasattr(self, "score_lbl"):
            self.score_lbl.config(text=f"★ {self.score}")
        if levelled:
            self.floor_ended = True   
            self.master.after(200, lambda: self.show_perk_screen(self._resume_floor))

        safe_count = self.rows * self.cols - len(self.mine_locs) + len(self.duds)
        if len(self.revealed) >= safe_count:
            self._floor_clear()

    def _resume_floor(self):
        self.floor_ended = False
        self._start_floor()   

    def _post_first_click_perks(self, r, c):
        if getattr(self, "_cartographer_pending", False):
            corners = [(0,0),(0,self.cols-1),(self.rows-1,0),(self.rows-1,self.cols-1)]
            for cr, cc in corners:
                if (cr, cc) not in self.mine_locs and (cr, cc) not in self.revealed:
                    self.reveal(cr, cc)
            self._cartographer_pending = False

        if getattr(self, "_sixth_sense_pending", False):
            if self.mine_locs:
                m = random.choice(list(self.mine_locs))
                self.buttons[m[0]][m[1]].config(bg="#ff4444", text="💣")
                self.master.after(1200, lambda: self._hide_sixth_sense(m))
            self._sixth_sense_pending = False

        if "Eagle Eye" in self.perks:
            safes = [(r2, c2) for r2 in range(self.rows) for c2 in range(self.cols)
                     if (r2, c2) not in self.mine_locs
                     and (r2, c2) not in self.revealed
                     and (r2, c2) != (r, c)]
            if safes:
                pick = random.choice(safes)
                self.reveal(pick[0], pick[1])

        if "Pathfinder" in self.perks:

            pass  

    def _hide_sixth_sense(self, m):
        if m not in self.revealed and m not in self.flagged:
            self.buttons[m[0]][m[1]].config(bg="#2a2a44", text="")

    def toggle_flag(self, r, c):
        if self.floor_ended or (r, c) in self.revealed:
            return
        if (r, c) in self.flagged:
            self.flagged.remove((r, c))
            self.buttons[r][c].config(text="", bg="#2a2a44")
        else:
            self.flagged.add((r, c))
            self.buttons[r][c].config(text="🚩", bg="#1a1a30")
            bonus_xp = XP_PER_FLAG if "Scavenger" in self.perks else 0

            if (r, c) in self.mine_locs:
                self._gain_xp(XP_PER_FLAG + bonus_xp)
                self.total_flags += 1
        remaining = self.mine_count - len(self.flagged)
        self.mine_lbl.config(text=f"💣 {remaining}")

    def chord_click(self, r, c):
        if self.floor_ended or (r, c) not in self.revealed:
            return
        count = self.count_adj_mines(r, c)
        flags = sum(1 for nr, nc in self.get_neighbors(r, c) if (nr, nc) in self.flagged)
        if flags == count:
            extra = 1 if "Berserker" in self.perks else 0
            targets = [(nr, nc) for nr, nc in self.get_neighbors(r, c)
                       if (nr, nc) not in self.flagged and (nr, nc) not in self.revealed]
    
            for nr, nc in targets[:len(targets) - extra if extra else len(targets)]:
                self.click(nr, nc)


    def reveal(self, start_r, start_c):
        queue = deque([(start_r, start_c)])
        while queue:
            r, c = queue.popleft()
            if (r, c) in self.revealed:
                continue
            self.revealed.add((r, c))
            self.flagged.discard((r, c))
            count = self.count_adj_mines(r, c)
            btn = self.buttons[r][c]
            is_dud = (r, c) in self.duds
            btn.config(relief=tk.SUNKEN,
                       bg="#13132a" if not is_dud else "#1a2a1a",
                       state=tk.DISABLED, text="")
            if is_dud:
                btn.config(text="💫", fg="#ffe08a")
            elif count > 0:
                btn.config(text=str(count),
                           fg=NUMBER_COLORS.get(count, "#eeeeee"))
            else:
                for nr, nc in self.get_neighbors(r, c):
                    if (nr, nc) not in self.revealed:
                        queue.append((nr, nc))


    def _hit_mine(self, r, c):
        self.floor_ended = True
        self.buttons[r][c].config(text="💥", bg="#ff2200", state=tk.DISABLED)
        self.master.after(400, lambda: self._process_death(r, c))

    def _process_death(self, r, c):

        for mr, mc in self.mine_locs:
            if (mr, mc) not in self.revealed and (mr, mc) not in self.duds:
                self.buttons[mr][mc].config(
                    text="💣", bg="#440000" if (mr, mc) != (r, c) else "#ff2200",
                    state=tk.DISABLED
                )
        self.lives -= 1
        if hasattr(self, "lives_lbl"):
            self.lives_lbl.config(text=self._lives_text())

        if self.lives <= 0:
            self.master.after(800, self.show_game_over)
        else:
            self.master.after(1200, lambda: self._confirm_continue(r, c))

    def _confirm_continue(self, r, c):
        ans = messagebox.askyesno(
            "💀 You died!",
            f"BOOM! You hit a mine on Floor {self.floor}.\n\n"
            f"Lives remaining: {self.lives}\n\n"
            "Spend a life and retry this floor?",
            icon="warning"
        )
        if ans:
            self._start_floor()
        else:
            self.show_game_over()

    def _floor_clear(self):
        self.floor_ended = True
        self.floors_cleared += 1
        bonus = XP_PER_FLOOR + max(0, 120 - self.floor_seconds) // 4
        levelled = self._gain_xp(bonus)
        self.score += bonus


        for mr, mc in self.mine_locs:
            if (mr, mc) not in self.flagged and (mr, mc) not in self.duds:
                self.flagged.add((mr, mc))
                self.buttons[mr][mc].config(text="🚩", bg="#002200")

        if levelled:
            self.master.after(600, lambda: self.show_perk_screen(self.next_floor))
        else:
            msg = (f"Floor {self.floor} cleared in {self.floor_seconds}s!\n\n"
                   f"+{bonus} XP bonus\n\n"
                   f"Descend to Floor {self.floor + 1}?")
            self.master.after(400, lambda: self._descend_prompt(msg))

    def _descend_prompt(self, msg):
        ans = messagebox.askyesno(f"⬇  Floor {self.floor} Cleared!", msg, icon="info")
        if ans:
            self.next_floor()
        else:
            self.show_game_over(voluntary=True)


    def show_game_over(self, voluntary=False):
        self._clear_window()
        bg = "#0d0d1a"
        self.master.configure(bg=bg)

        wrap = tk.Frame(self.master, bg=bg)
        wrap.pack(expand=True, pady=40)

        if voluntary:
            tk.Label(wrap, text="🏳", font=("Segoe UI Emoji", 48),
                     bg=bg, fg="#e8c97a").pack()
            tk.Label(wrap, text="YOU RETREATED", font=("Courier New", 26, "bold"),
                     bg=bg, fg="#e8c97a").pack(pady=(4, 0))
        else:
            tk.Label(wrap, text="💀", font=("Segoe UI Emoji", 48),
                     bg=bg, fg="#ff6b6b").pack()
            tk.Label(wrap, text="GAME  OVER", font=("Courier New", 28, "bold"),
                     bg=bg, fg="#ff6b6b").pack(pady=(4, 0))

        tk.Label(wrap, text="─" * 38,
                 font=("Courier New", 10), bg=bg, fg="#333355").pack(pady=8)

        stats = [
            ("Floors Cleared",   self.floors_cleared),
            ("Final Floor",      self.floor),
            ("Player Level",     self.player_level),
            ("Total Score",      self.score),
            ("Mines Flagged",    self.total_flags),
            ("Lives Remaining",  self.lives),
        ]

        sf = tk.Frame(wrap, bg="#111122", bd=0)
        sf.pack(padx=40, pady=8, fill=tk.X)
        for label, val in stats:
            row = tk.Frame(sf, bg="#111122")
            row.pack(fill=tk.X, padx=16, pady=2)
            tk.Label(row, text=label, font=("Courier New", 11),
                     bg="#111122", fg="#7777aa", anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=str(val), font=("Courier New", 11, "bold"),
                     bg="#111122", fg="#e8c97a", anchor="e").pack(side=tk.RIGHT)

        if self.perks:
            tk.Label(wrap, text="Perks Acquired:",
                     font=("Courier New", 10), bg=bg, fg="#555577").pack(pady=(12, 2))
            tk.Label(wrap, text="  ·  ".join(self.perks),
                     font=("Courier New", 9, "bold"),
                     bg=bg, fg="#9575cd").pack()

        tk.Label(wrap, text="─" * 38,
                 font=("Courier New", 10), bg=bg, fg="#333355").pack(pady=8)

        btn_frame = tk.Frame(wrap, bg=bg)
        btn_frame.pack()
        tk.Button(btn_frame, text="▶  Play Again",
                  font=("Courier New", 12, "bold"),
                  bg="#e8c97a", fg="#0d0d1a", activebackground="#ffe08a",
                  relief=tk.FLAT, padx=16, pady=8, cursor="hand2",
                  command=self.start_run).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="✕  Quit",
                  font=("Courier New", 12),
                  bg="#2a2a44", fg="#aaaacc", activebackground="#3a3a60",
                  relief=tk.FLAT, padx=16, pady=8, cursor="hand2",
                  command=self.master.quit).pack(side=tk.LEFT, padx=8)



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper Roguelike")
    root.resizable(True, True)
    root.configure(bg="#0d0d1a")

    try:
        root.iconbitmap("")
    except Exception:
        pass

    app = RogueMinesweeper(root)
    root.mainloop()