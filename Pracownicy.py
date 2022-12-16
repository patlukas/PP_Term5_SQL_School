import sqlite3
import tkinter as tk
from GuiMethods import GuiMethods


class Pracownicy(GuiMethods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db

    def show_frame(self) -> None:
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Pracownicy")
        label.pack()
        frame.pack()