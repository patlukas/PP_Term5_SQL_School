import sqlite3
import tkinter as tk
from GuiMethods import GuiMethods


class Etaty(GuiMethods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__rows = self.__get_rows_data()

    def show_frame(self) -> None:
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Etaty")
        table = self._create_table(frame, ["Nazwa", "Płaca minimalna", "Płaca maksymalna"], self.__rows, self.__edit_row, self.__del_row)
        button = tk.Button(master=frame, text="Dodaj etat", command=self.__add_etat)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        rows = cur.fetchall()
        return rows

    def __add_etat(self):
        print("Dodaj etat")

    def __edit_row(self, id: int):
        print(f"Edycja {self.__rows[id]}")

    def __del_row(self, id: int):
        print(f"Usuń {self.__rows[id]}")


