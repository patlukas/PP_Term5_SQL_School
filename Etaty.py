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
        table = self._create_table(frame, ["Nazwa", "Płaca minimalna", "Płaca maksymalna"], self.__rows, self.__frame_edit_row, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj etat", command=self.__frame_add_etat)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        rows = cur.fetchall()
        return rows

    def __frame_add_etat(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie etatu", ["Nazwa etatu", "Płaca minimalna", "Płaca maksymalna"], None, self.__add_etat_to_db, "Stwórz etat")
        frame.pack()
        print("Dodaj etat")

    def __add_etat_to_db(self, list_entry: list[tk.Entry]):
        for entry in list_entry:
            print(entry.get())

    def __frame_edit_row(self, id: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja etatu", ["Nazwa etatu", "Płaca minimalna", "Płaca maksymalna"], self.__rows[id], lambda x: print(f"Click {x}"), "Edytuj etat")
        frame.pack()

        print(f"Edycja {self.__rows[id]}")

    def __frame_del_row(self, id: int):
        print(f"Usuń {self.__rows[id]}")



