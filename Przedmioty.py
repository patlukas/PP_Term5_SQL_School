import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Przedmioty(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Nazwa przedmiotu"]
        self.__column_widths = [200]

        self.__rows = []

    def show_frame(self) -> None:
        self.__rows = self.__get_rows_data()

        self._create_main_frame(self.__db, self.__window, "Przedmioty", "Dodaj przedmiot",
                                self.__list_labels,
                                self.__column_widths,
                                self.__rows,
                                self.__frame_add, None, self.__frame_del)

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM przedmioty")
        rows = cur.fetchall()
        return rows

    def __frame_add(self):
        self._create_add_frame(self.__window, "Dodanie nowego przedmiotu", "Dodaj przedmiot", self.__list_labels, [str],
                               self.__add_to_db, self.show_frame).pack()

    def __frame_del(self, id: int):
        check_data = [
            [
                "SELECT * FROM oceny WHERE przedmioty_nazwa=?",
                [self.__rows[id][0]],
                "Nie można usunąć przedmiotu, bo istnieją oceny z tego przedmiotu."
            ],
            [
                "SELECT * FROM sprawdziany WHERE przedmioty_nazwa=?",
                [self.__rows[id][0]],
                "Nie można usunąć przedmiotu, bo instnieją zaplanowane sprawdziany z tego przedmiotu.."
            ],
            [
                "SELECT * FROM zajecia WHERE przedmioty_nazwa=?",
                [self.__rows[id][0]],
                "Nie można usunąć przedmiotu, bo istnieją zajęcia z tego przedmiotu."
            ],
            [
                "SELECT * FROM nauczyciele_przedmioty WHERE przedmiot_nazwa=?",
                [self.__rows[id][0]],
                "Nie można usunąć przedmiotu, bo jest przypisany do nauczyciela uczącego."
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć przedmiot '{self.__rows[id][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM przedmioty WHERE nazwa=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO przedmioty VALUES(?)", list_data)
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie przedmiotu!", "Nazwa przedmiotu musi być unikalna")
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie przedmiotu!", "Niezydentyfikowany błąd")

    def __data_validation(self, list_data):
        list_data[0] = list_data[0].strip()

        if not (
                self.check_varchar2(list_data[0], 20, "przedmiotu")
        ):
            return False
        return list_data
