import tkinter as tk
from gameBoard import GameBoard

root = tk.Tk()
root.title('Keschet')
game = GameBoard(root)
game.pack(fill="both", expand="true")
game.import_pieces()
root.wm_iconphoto(False, game.getWindowImage())
root.mainloop()