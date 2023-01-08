import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Etaty(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Nazwa etatu", "Płaca minimalna", "Płaca maksymalna"]
        self.__rows = []
        self.__keys = []

    def show_frame(self) -> None:
        self.__rows, self.__keys = self.__get_rows_data()
        self._create_main_frame(self.__db, self.__window, "Etaty", "Dodaj etat", self.__list_labels, self.__rows,
                                self.__frame_add, self.__frame_edit_row, self.__frame_del_row).pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        rows = cur.fetchall()
        keys = [r[0] for r in rows]
        return rows, keys

    def __frame_add(self):
        self._create_add_frame(self.__window, "Dodanie etatu", "Stwórz etat", self.__list_labels, [str, str, str],
                               self.__add_to_db, self.show_frame).pack()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO etaty VALUES(?, ?, ?)", list_data)
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie etatu!", "Nazwa etatu musi być unikalna")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie etatu!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_edit_row(self, index: int):
        self._create_edit_frame(self.__window, "Edycja etatu", "Edytuj etat", self.__list_labels, self.__rows[index],
                                [str, str, str], lambda data: self.__edit_row_in_db(data, index), self.show_frame).pack()

    def __edit_row_in_db(self, list_data, index):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                name, placa_min, placa_max = list_data
                self.__db.execute("UPDATE etaty SET nazwa=?, placa_min=?, placa_max=? WHERE nazwa=?",
                                  [name, placa_min, placa_max, self.__keys[index]])
                self.__db.execute("UPDATE pracownicy SET Etaty_nazwa=? WHERE Etaty_nazwa=?", [name, self.__keys[index]])
                self.__db.execute("UPDATE pracownicy SET płaca=? WHERE Etaty_nazwa=? AND płaca<?", [placa_min, name, placa_min])
                self.__db.execute("UPDATE pracownicy SET płaca=? WHERE Etaty_nazwa=? AND płaca>?", [placa_max, name, placa_max])
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy edycji etatu!", "Nazwa etatu musi być unikalna")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji etatu!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del_row(self, index: int):
        check_data = [
            [
                "SELECT * FROM pracownicy WHERE Etaty_nazwa=?", [self.__rows[index][0]],
                "Nie można usunąć etatu, bo istnieje pracownik zatrudniony na tym etacie"
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć etat o nazwie '{self.__rows[index][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM etaty WHERE nazwa=?", [self.__rows[index][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!",
                                     f"Niepowiodło się usunięcie '{self.__rows[index][0]}'")
                self.__db.rollback()

    def __data_validation(self, list_data):
        if not (
            self.check_varchar2(list_data[0], 20, "Nazwa etatu") and
            self.check_number(list_data[1], 9, 2, "Płaca minimalna") and
            self.check_number(list_data[2], 9, 2, "Płaca maksymalna")
        ):
            return False

        list_data[1], list_data[2] = float(list_data[1]), float(list_data[2])
        if list_data[1] > list_data[2] or list_data[1] < 0 or list_data[2] < 0:
            messagebox.showerror("Błędne wartości płac!", "Podano błędne wartości płac")
            return False
        return list_data
