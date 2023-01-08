import tkinter as tk
from gameController import gameController
#to run currently do
#g++ aiHandler.cpp ai.cpp -o aiHandler && keschet.py #Windows development
#g++ aiHandler.cpp ai.cpp -o aiHandler && python3.9 keschet.py #Mac development

root = tk.Tk()
root.title('Keschet')
game = gameController(root)
game.pack(fill="both", expand="true")
game.boardDisplay.import_pieces()
root.wm_iconphoto(False, game.boardDisplay.getWindowImage())
root.mainloop()