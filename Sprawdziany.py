import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Sprawdziany(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Klasa", "Przedmiot (Nauczyciel)", "Data", "Opis"]
        self.__list_przedmiot_and_teacher = []
        self.__list_klasy = []
        self.__list_id = []
        self.__rows = []

    def show_frame(self) -> None:
        self.__list_przedmiot_and_teacher = self.__get_list_przedmiot_and_teacher()
        self.__list_klasy = self.__get_list_klasy()
        self.__rows, self.__list_id = self.__get_rows_data()
        self._create_main_frame(self.__db, self.__window, "Sprawdziany", "Dodaj nowy sprawdzian", self.__list_labels,
                                self.__rows, self.__frame_add, self.__frame_edit, self.__frame_del).pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM sprawdziany")
        rows, list_id = [], []
        for row in cur.fetchall():
            przedmiot_and_teacher = ""
            for przedmiot_name, teacher_pesel, teacher_name, full_name in self.__get_list_przedmiot_and_teacher():
                if row[5] == teacher_pesel and row[4] == przedmiot_name:
                    przedmiot_and_teacher = full_name
                    break
            klasa = ""
            for name, rocznik, full_name in self.__list_klasy:
                if row[3] == name and row[6] == rocznik:
                    klasa = full_name
                    break

            rows.append([klasa, przedmiot_and_teacher, row[1], row[2]])
            list_id.append(row[0])
        return rows, list_id

    def __get_list_przedmiot_and_teacher(self):
        cur = self.__db.cursor()
        cur.execute("SELECT np.przedmiot_nazwa, p.pesel, p.nazwisko || ' ' || p.imie "
                    "FROM nauczyciele_przedmioty np JOIN pracownicy p ON p.pesel = np.nauczyciel_pesel")
        return [[el[0], el[1], el[2], f"{el[0]} <{el[2]} ({el[1]})>"] for el in cur.fetchall()]

    def __get_list_klasy(self):
        cur = self.__db.cursor()
        cur.execute("SELECT nazwa, rocznik FROM klasy")
        return [[el[0], el[1], f"{el[0]} ({el[1]})"] for el in cur.fetchall()]

    def __frame_add(self):
        self._create_add_frame(self.__window, "Dodanie sprawdzianu", "Stwórz sprawdzian", self.__list_labels,
                               [self.__get_list_klasy_full_name(), self.__get_list_string_przedmioty_and_teacher(),
                                str, str], self.__add_to_db, self.show_frame).pack()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                klasa_nazwa, klasa_rocznik = self.__get_klasa_nazwa_and_rocznik_by_title(list_data[0])
                przedmiot_nazwa, nauczyciel_pesel = self.__get_przedmiot_nazwa_and_nauczyciel_pesel_by_title(list_data[1])

                self.__db.execute("INSERT INTO sprawdziany VALUES((SELECT MAX(id) + 1 FROM sprawdziany), ?, ?, ?, ?, ?, ?)",
                                  [list_data[2], list_data[3], klasa_nazwa, przedmiot_nazwa, nauczyciel_pesel, klasa_rocznik])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd podczas dodawania!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_edit(self, index: int):
        self._create_edit_frame(self.__window, "Edycja sprawdzianu", "Edytuj sprawdzian", self.__list_labels,
                                self.__rows[index], [self.__get_list_klasy_full_name(),
                                                     self.__get_list_string_przedmioty_and_teacher(), str, str],
                                lambda data: self.__edit_row_in_db(data, index), self.show_frame).pack()

    def __edit_row_in_db(self, list_data, index):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                klasa_nazwa, klasa_rocznik = self.__get_klasa_nazwa_and_rocznik_by_title(list_data[0])
                przedmiot_nazwa, nauczyciel_pesel = self.__get_przedmiot_nazwa_and_nauczyciel_pesel_by_title(list_data[1])

                self.__db.execute("UPDATE sprawdziany SET data=?, opis=?, klasy_nazwa=?, przedmioty_nazwa=?, nauczyciele_pesel=?, klasy_rocznik=? WHERE id=?",
                                  [list_data[2], list_data[3], klasa_nazwa, przedmiot_nazwa, nauczyciel_pesel, klasa_rocznik, self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji sprawdzianu!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del(self, index: int):
        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć sprawdzian?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM sprawdziany WHERE id=?", [self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Usunięcie sprawdzianu się niepowiodło")
                self.__db.rollback()

    def __data_validation(self, list_data):
        if not (
            self.check_value_from_list(list_data[0], self.__get_list_klasy_full_name(), "Klasa") and
            self.check_value_from_list(list_data[1], self.__get_list_string_przedmioty_and_teacher(), "Przedmiot (Nauczyciel)") and
            self.check_date(list_data[2], "Data") and
            self.check_varchar2(list_data[3], 50, "Opis")
        ):
            return False
        return list_data

    def __get_list_klasy_full_name(self):
        return [r[2] for r in self.__list_klasy]

    def __get_list_string_przedmioty_and_teacher(self):
        return [r[3] for r in self.__list_przedmiot_and_teacher]

    def __get_klasa_nazwa_and_rocznik_by_title(self, title):
        for nazwa, rocznik, klasa_title in self.__list_klasy:
            if title == klasa_title:
                return nazwa, rocznik
        raise Exception("Brak klasy")

    def __get_przedmiot_nazwa_and_nauczyciel_pesel_by_title(self, title):
        for przedmiot, pesel, _, name in self.__list_przedmiot_and_teacher:
            if title == name:
                return przedmiot, pesel
        raise Exception("Brak przedmiotu i peselu nauczyciela")
