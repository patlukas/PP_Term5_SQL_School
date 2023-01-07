import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods
from datetime import date


class Klasy(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Nazwa", "Rocznik", "Wychowawca"]
        self.__list_teacher = []
        self.__rows = []
        self.__list_rocznik = [f"{r}/{r + 1}" for r in range(date.today().year, 2000, -1)]

    def show_frame(self) -> None:
        self.__list_teacher = self.__get_list_teacher()
        self.__rows = self.__get_rows_data()
        self._create_main_frame(self.__db, self.__window, "Klasy", "Dodaj klasę", self.__list_labels, self.__rows,
                                self.__frame_add, self.__frame_edit, self.__frame_del).pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM klasy")
        rows = []
        for nazwa, wychowawca_pesel, rocznik in cur.fetchall():
            wychowawca = self.__get_teacher_name_by_pesel(wychowawca_pesel)
            rows.append([nazwa, rocznik, wychowawca])
        return rows

    def __get_list_teacher(self):
        cur = self.__db.cursor()
        cur.execute("SELECT p.pesel, p.nazwisko, p.imie FROM nauczyciele n JOIN pracownicy p ON n.pesel = p.pesel")
        return [[pesel, f"{nazwisko} {imie} ({pesel})"] for pesel, nazwisko, imie in cur.fetchall()]

    def __frame_add(self):
        list_teacher_name = [teacher[1] for teacher in self.__list_teacher]
        self._create_add_frame(self.__window, "Dodawanie klasy", "Dodaj klasę", self.__list_labels,
                               [str, self.__list_rocznik, list_teacher_name], self.__add_to_db, self.show_frame).pack()

    def __frame_edit(self, index: int):
        list_teacher_name = [teacher[1] for teacher in self.__list_teacher]
        self._create_edit_frame(self.__window, "Edycja klasy", "Edytuj klasę", self.__list_labels, self.__rows[index],
                                [str, self.__list_rocznik, list_teacher_name],
                                lambda data: self.__edit_row_in_db(data, index), self.show_frame).pack()

    def __frame_del(self, index: int):
        arg = [self.__rows[index][0], self.__rows[index][1]]
        check_data = [
            [
                "SELECT * FROM uczniowie WHERE Klasy_nazwa=? AND Klasy_rocznik=?", arg,
                f"Nie można usunąć klasy, bo istnieją uczniowie należący do tej klasy"
            ],
            [
                "SELECT * FROM sprawdziany WHERE Klasy_nazwa=? AND Klasy_rocznik=?", arg,
                f"Nie można usunąć klasy, bo istnieją sprawdziany zaplanowane dla tej klasy"
            ],
            [
                "SELECT * FROM zajecia WHERE Klasy_nazwa=? AND Klasy_rocznik=?", arg,
                f"Nie można usunąć klasy, bo klasa na zaplanowane zajęcia"
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć klasę o nazwie '{arg[0]}' z rocznika {arg[1]}?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM klasy WHERE nazwa=? AND rocznik=?", arg)
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie klasy o nazwie '{arg[0]}' z rocznika {arg[1]}")
                self.__db.rollback()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)

        if list_data is not False:
            try:
                pesel = self.__get_teacher_pesel_by_name(list_data[2])
                self.__db.execute("INSERT INTO klasy VALUES(?, ?, ?)", [list_data[0], pesel, list_data[1]])
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie klasy!", "Już istnieje klasa z taką nazwą w wybranym roczniku")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie klasy!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __edit_row_in_db(self, list_data, index):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                pesel = self.__get_teacher_pesel_by_name(list_data[2])
                self.__db.execute(
                    "UPDATE klasy SET nazwa=?, rocznik=?, nauczyciele_pesel=? WHERE nazwa=? AND rocznik=?",
                    [list_data[0], list_data[1], pesel, self.__rows[index][0], self.__rows[index][1]]
                )
                self.__db.execute(
                    "UPDATE zajecia SET klasy_nazwa=?, klasy_rocznik=? WHERE klasy_nazwa=? AND klasy_rocznik=?",
                    [list_data[0], list_data[1], self.__rows[index][0], self.__rows[index][1]]
                )
                self.__db.execute(
                    "UPDATE uczniowie SET klasy_nazwa=?, klasy_rocznik=? WHERE klasy_nazwa=? AND klasy_rocznik=?",
                    [list_data[0], list_data[1], self.__rows[index][0], self.__rows[index][1]]
                )
                self.__db.execute(
                    "UPDATE sprawdziany SET klasy_nazwa=?, klasy_rocznik=? WHERE klasy_nazwa=? AND klasy_rocznik=?",
                    [list_data[0], list_data[1], self.__rows[index][0], self.__rows[index][1]]
                )
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy edycji klasy!", "Już istnieje klasa z taką nazwą w wybranym roczniku")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji klasy!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __data_validation(self, list_data):
        list_nauczyciel_name = [name for _, name in self.__list_teacher]
        if not (
                self.check_varchar2(list_data[0], 5, "Nazwa klasy") and
                self.check_value_from_list(list_data[1], self.__list_rocznik, "Rocznik") and
                self.check_value_from_list(list_data[2], list_nauczyciel_name, "Wychowawca")
        ):
            return False
        return list_data

    def __get_teacher_pesel_by_name(self, wychowawca_name) -> str:
        for nauczyciel_pesel, nauczyciel_name in self.__list_teacher:
            if wychowawca_name == nauczyciel_name:
                return nauczyciel_pesel
        return ""

    def __get_teacher_name_by_pesel(self, pesel):
        for nauczyciel_pesel, nauczyciel in self.__list_teacher:
            if nauczyciel_pesel == pesel:
                return nauczyciel
        return ""
