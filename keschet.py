import tkinter as tk
from gameController import gameController

root = tk.Tk()
root.title('Keschet')
game = gameController(root)
game.pack(fill="both", expand="true")
game.boardDisplay.import_pieces()
root.wm_iconphoto(False, game.boardDisplay.getWindowImage())
root.mainloop()