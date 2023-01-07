import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Oceny(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Klasa | Uczeń", "Przedmiot (Nauczyciel)", "Data", "Ocena", "Waga", "Opis"]
        self.__list_przedmiot_and_teacher = self.__get_list_przedmiot_and_teacher()
        self.__list_uczniowie = self.__get_list_uczniowie()
        self.__list_ocen = ["1", "2", "3", "4", "5", "6"]
        self.__list_wag = ["1", "2", "3", "4", "5"]
        self.__list_id = []
        self.__rows = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__list_przedmiot_and_teacher = self.__get_list_przedmiot_and_teacher()
        self.__list_uczniowie = self.__get_list_uczniowie()
        self.__rows, self.__list_id = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        tk.Label(master=frame, text="Oceny").pack()
        self._create_table(frame, self.__list_labels, self.__rows, self.__frame_edit, self.__frame_del_row).pack()
        tk.Button(master=frame, text="Dodaj nową ocenę", command=self.__frame_add).pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM oceny")
        rows_read = cur.fetchall()
        rows, list_id = [], []
        for row in rows_read:
            przedmiot_and_teacher = ""
            for przedmiot_name, teacher_pesel, teacher_name, full_name in self.__list_przedmiot_and_teacher:
                if row[7] == teacher_pesel and row[6] == przedmiot_name:
                    przedmiot_and_teacher = full_name
                    break
            klasa_and_uczen = ""
            for pesel, name in self.__list_uczniowie:
                if row[3] == pesel:
                    klasa_and_uczen = name
                    break
            rows.append([klasa_and_uczen, przedmiot_and_teacher, row[2], str(row[1]), str(row[4]), row[5]])
            list_id.append(row[0])
        return rows, list_id

    def __get_list_przedmiot_and_teacher(self):
        cur = self.__db.cursor()
        cur.execute("SELECT np.przedmiot_nazwa, p.pesel, p.nazwisko || ' ' || p.imie FROM nauczyciele_przedmioty np JOIN pracownicy p ON p.pesel = np.nauczyciel_pesel")
        return [[el[0], el[1], el[2], f"{el[0]} <{el[2]} ({el[1]})>"] for el in cur.fetchall()]

    def __get_list_uczniowie(self):
        cur = self.__db.cursor()
        cur.execute("SELECT pesel, imie, nazwisko, klasy_nazwa, klasy_rocznik FROM uczniowie")
        return [[el[0], f"{el[3]} {el[4]} | {el[2]} {el[1]} ({el[0]})"] for el in cur.fetchall()]

    def __frame_add(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie oceny",
                                               self.__list_labels, None,
                                               [self.__get_list_klas_and_uczen_title(),
                                                self.__get_list_przedmiot_and_teacher_title(),
                                                str, self.__list_ocen, self.__list_wag, str],
                                               self.__add_to_db, "Dodaj ocenę", self.show_frame)
        frame.pack()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                uczen_pesel = self.__get_uczen_pesel_by_title(list_data[0])
                przedmiot_nazwa, nauczyciel_pesel = self.__get_przedmiot_nazwa_and_nauczyciel_pesel_by_title(list_data[1])
                self.__db.execute("INSERT INTO oceny VALUES((SELECT MAX(id) + 1 FROM oceny), ?, ?, ?, ?, ?, ?, ?)",
                                  [list_data[3], list_data[2], uczen_pesel, list_data[4], list_data[5], przedmiot_nazwa, nauczyciel_pesel])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd podczas dodawania oceny!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_edit(self, index: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja oceny",
                                               self.__list_labels, self.__rows[index],
                                               [self.__get_list_klas_and_uczen_title(),
                                                self.__get_list_przedmiot_and_teacher_title(),
                                                str, self.__list_ocen, self.__list_wag, str],
                                               lambda list_data: self.__edit_row_in_db(list_data, index), "Edytuj ocenę",
                                               self.show_frame)
        frame.pack()

    def __edit_row_in_db(self, list_data, index):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                uczen_pesel = self.__get_uczen_pesel_by_title(list_data[0])
                przedmiot_nazwa, nauczyciel_pesel = self.__get_przedmiot_nazwa_and_nauczyciel_pesel_by_title(list_data[1])

                self.__db.execute("UPDATE oceny SET ocena=?, data=?, uczniowie_pesel=?, waga=?, opis=?, przedmioty_nazwa=?, nauczyciele_pesel=? WHERE id=?",
                                  [list_data[3], list_data[2], uczen_pesel, list_data[4], list_data[5], przedmiot_nazwa, nauczyciel_pesel, self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji oceny!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del_row(self, index: int):
        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć ocenę?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM oceny WHERE id=?", [self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Usunięcie oceny się niepowiodło")
                self.__db.rollback()

    def __data_validation(self, list_data):
        if not (
            self.check_value_from_list(list_data[0], self.__get_list_klas_and_uczen_title(), "Klasa | Uczeń") and
            self.check_value_from_list(list_data[1], self.__get_list_przedmiot_and_teacher_title(), "Przedmiot (Nauczyciel)") and
            self.check_date(list_data[2], "Data") and
            self.check_value_from_list(list_data[3], self.__list_ocen, "Ocena") and
            self.check_value_from_list(list_data[4], self.__list_wag, "Waga") and
            self.check_varchar2(list_data[5], 30, "Opis", True)
        ):
            return False
        return list_data

    def __get_list_klas_and_uczen_title(self):
        return [r[1] for r in self.__list_uczniowie]

    def __get_list_przedmiot_and_teacher_title(self):
        return [r[3] for r in self.__list_przedmiot_and_teacher]

    def __get_uczen_pesel_by_title(self, title):
        for pesel, name in self.__list_uczniowie:
            if title == name:
                return pesel
        raise Exception("Brak peselu ucznia")

    def __get_przedmiot_nazwa_and_nauczyciel_pesel_by_title(self, title):
        for przedmiot, pesel, _, name in self.__list_przedmiot_and_teacher:
            if title == name:
                return przedmiot, pesel
        raise Exception("Brak przedmiotu i peselu nauczyciela")
