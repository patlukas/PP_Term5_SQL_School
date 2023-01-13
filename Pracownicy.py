import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Pracownicy(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Pesel", "Imie", "Nazwisko", "Data urodzenia", "Data zatrudnienia", "Płaca", "Etat",
                              "Czy nauczyciel"]
        self.__rows = []
        self.__list_etat_row = []
        self.__list_etat = []

    def show_frame(self) -> None:
        self.__list_etat_row = self.__get_list_etat_row()
        self.__list_etat = [row[0] for row in self.__list_etat_row]

        self.__rows = self.__get_rows_data()

        self._create_main_frame(self.__db, self.__window, "Pracownicy", "Dodaj pracownika", self.__list_labels, self.__rows,
                                self.__frame_add, self.__frame_edit, self.__frame_del)

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM pracownicy")
        rows_pracownicy = cur.fetchall()
        cur.execute("SELECT pesel FROM nauczyciele")
        nauczyciele = [nauczyciel[0] for nauczyciel in cur.fetchall()]
        rows = []
        for pracownik in rows_pracownicy:
            rows.append(list(pracownik) + [pracownik[0] in nauczyciele])
        return rows

    def __frame_add(self):
        self._create_add_frame(self.__window, "Dodanie pracownika", "Stwórz pracownika", self.__list_labels,
                               [str, str, str, str, str, str, self.__list_etat, bool], self.__add_to_db, self.show_frame
                               ).pack()

    def __frame_edit(self, index: int):
        self._create_edit_frame(self.__window, "Edycja pracownika", "Edytuj pracownika", self.__list_labels,
                                self.__rows[index], [None, str, str, str, str, str, self.__list_etat, bool],
                                self.__edit_row_in_db, self.show_frame).pack()

    def __frame_del(self, index: int):
        pesel = self.__rows[index][0]
        if self.__check_teacher_is_used(pesel, "Nie można usunąć pracownika z rolą nauczyciela"):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć pracownika z peselem '{pesel}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM pracownicy WHERE pesel=?", [pesel])
                self.__db.execute("DELETE FROM nauczyciele WHERE pesel=?", [pesel])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{pesel}'")
                self.__db.rollback()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO pracownicy VALUES(?, ?, ?, ?, ?, ?, ?)", list_data[:-1])
                if list_data[-1]:
                    self.__db.execute("INSERT INTO nauczyciele VALUES(?)", [list_data[0]])
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie pracownika!", "Pesel musi być unikalna")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie pracownika!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __edit_row_in_db(self, list_data):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                nauczyciel = True
                for row in self.__rows:
                    if row[0] == list_data[0]:
                        nauczyciel = row[-1]
                if nauczyciel and not list_data[-1]:
                    if self.__check_teacher_is_used(list_data[0], "Nie można usunąć pracownikowi roli nauczyciela"):
                        return

                self.__db.execute(
                    "UPDATE pracownicy SET imie=?, nazwisko=?, data_urodzenia=?, data_zatrudnienia=?, płaca=?, Etaty_nazwa=?  WHERE pesel=?",
                    [list_data[1], list_data[2], list_data[3], list_data[4], list_data[5], list_data[6], list_data[0]]
                )

                if nauczyciel != list_data[-1]:
                    if list_data[-1]:
                        self.__db.execute("INSERT INTO nauczyciele VALUES(?)", [list_data[0]])
                    else:
                        self.__db.execute("DELETE FROM nauczyciele WHERE pesel=?", [list_data[0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji pracownika!", "Niezydentyfikowany błąd")

    def __data_validation(self, list_data):
        if not (
                self.check_pesel(list_data[0]) and
                self.check_varchar2(list_data[1], 30, "Imie") and
                self.check_varchar2(list_data[2], 30, "Nazwisko") and
                self.check_date(list_data[3], "Data urodzenia") and
                self.check_date(list_data[4], "Data zatrudnienia") and
                self.check_number(list_data[5], 9, 2, "Płaca") and
                self.check_value_from_list(list_data[6], self.__list_etat, "Etat")
        ):
            return False

        list_data[5] = float(list_data[5])
        list_data[3], list_data[4] = list_data[3].strip(), list_data[4].strip()
        for etat_row in self.__list_etat_row:
            if etat_row[0] == list_data[6]:
                if list_data[5] < float(etat_row[1]) or list_data[5] > float(etat_row[2]):
                    messagebox.showerror("Błędna płaca!", f"Płaca musi być z przedniału od {etat_row[1]} do {etat_row[2]}")
                    return False
        return list_data

    def __get_list_etat_row(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        return cur.fetchall()

    def __check_teacher_is_used(self, pesel, message):
        check_data = [
            [
                "SELECT * FROM oceny WHERE Nauczyciele_pesel=?", [pesel],
                f"{message}, bo istnieją oceny wystawione przez tego nauczyciela"
            ],
            [
                "SELECT * FROM Nauczyciele_przedmioty WHERE Nauczyciel_pesel=?", [pesel],
                f"{message}, bo istnieją przedmioty do których jest przypisany jako nauczyciel"
            ],
            [
                "SELECT * FROM Klasy WHERE Nauczyciele_pesel=?", [pesel], f"{message}, bo jest wychowawca klasy"
            ],
            [
                "SELECT * FROM Sprawdziany WHERE Nauczyciele_pesel=?", [pesel],
                f"{message}, bo istnieją sprawdziany zaplanowane przez tego nauczyciela"
            ],
            [
                "SELECT * FROM Zajecia WHERE Nauczyciele_pesel=?", [pesel],
                f"{message}, bo istnieją zajęcia, które ma prodadzić."
            ]
        ]
        return not self.check_delete_is_possible(self.__db, check_data)
