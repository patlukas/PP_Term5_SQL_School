import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Sale(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Numer sali"]
        self.__column_widths = [100]

        self.__rows = []

    def show_frame(self) -> None:
        self.__rows = self.__get_rows_data()

        self._create_main_frame(self.__db, self.__window, "Sale", "Dodaj sale",
                                self.__list_labels,
                                self.__column_widths,
                                self.__rows,
                                self.__frame_add, None, self.__frame_del)

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM sale")
        rows = cur.fetchall()
        return rows

    def __frame_add(self):
        self._create_add_frame(self.__window, "Dodanie nowej sali", "Stwórz etat", self.__list_labels, [str, str, str],
                               self.__add_to_db, self.show_frame).pack()

    def __frame_del(self, id: int):
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

    def __add_to_db(self, list_data: list[str]):
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
