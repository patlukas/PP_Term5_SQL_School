import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Sale(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__rows = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__rows = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Sale")
        table = self._create_table(frame, ["Nuner sali"], self.__rows,
                                   None, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj sale", command=self.__frame_add_sala)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM sale")
        rows = cur.fetchall()
        return rows

    def __frame_add_sala(self):
        for x in self.__window.winfo_children():
            x.destroy()

        frame = self._create_frame_edit_or_add(self.__window, "Dodanie nowej sali",
                                               ["Numer sali"],
                                               None,
                                               [str],
                                               self.__add_sala_to_db, "Dodaj sale", self.show_frame)
        frame.pack()

    def __frame_del_row(self, id: int):
        check_data = [
            [
                "SELECT * FROM zajecia WHERE sale_numer=?",
                [self.__rows[id][0]],
                "Nie można usunąć sali, ponieważ są w niej przeprowadzane zajęcia."
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć sale o numerze '{self.__rows[id][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM sale WHERE numer=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")

    def __add_sala_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO sale VALUES(?)", list_data)
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianiu sali!", "Nazwa sali musi być unikalna")
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianiu sali!", "Niezidentyfikowany błąd")

    def __data_validation(self, list_data):
        list_data[0] = list_data[0].strip()
        if not (
            self.check_number(list_data[0], 4, 2, "Numer sali")
        ):
            return False
        return list_data
