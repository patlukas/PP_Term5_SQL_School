import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods
import datetime


class Lekcje(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Klasa (Zajęcia)", "Data zajęć", "Temat"]
        self.__list_zajecia = self.__get_list_zajecia()
        self.__list_id = []
        self.__rows = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__list_zajecia = self.__get_list_zajecia()
        self.__rows, self.__list_id = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        tk.Label(master=frame, text="Lekcje").pack()
        self._create_table(frame, self.__list_labels, self.__rows, self.__frame_edit, self.__frame_del_row).pack()
        tk.Button(master=frame, text="Dodaj nową lekcje", command=self.__frame_add).pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM lekcje")
        rows_read = cur.fetchall()
        rows, list_id = [], []
        for row in rows_read:
            klasa_and_zajecia = ""
            for el in self.__list_zajecia:
                if row[1] == el[0]:
                    klasa_and_zajecia = el[2]
                    break
            rows.append([klasa_and_zajecia, row[2], row[3]])
            list_id.append(row[0])
        return rows, list_id

    def __get_list_zajecia(self):
        cur = self.__db.cursor()
        cur.execute("SELECT id, przedmioty_nazwa, klasy_nazwa, klasy_rocznik, dzień_zajęc, godzina_zajęć FROM zajecia")
        return [[el[0], el[4], f"{el[2]} {el[3]} ({el[4]} | {el[4]} {el[5]})"] for el in cur.fetchall()]

    def __frame_add(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie lekcji", self.__list_labels, None,
                                               [self.__get_list_zajecia_title(), str, str], self.__add_to_db, "Stwórz")
        frame.pack()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                zajecia_id = self.__get_zajecia_id_by_title(list_data[0])
                self.__db.execute("INSERT INTO lekcje VALUES((SELECT MAX(id) + 1 FROM lekcje), ?, ?, ?)",
                                  [zajecia_id, list_data[1], list_data[2]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd podczas dodawania!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_edit(self, index: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja lekcji", self.__list_labels, self.__rows[index],
                                               [self.__get_list_zajecia_title(), str, str],
                                               lambda list_data: self.__edit_row_in_db(list_data, index), "Edytuj lekcje")
        frame.pack()

    def __edit_row_in_db(self, list_data, index):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                zajecia_id = self.__get_zajecia_id_by_title(list_data[0])
                self.__db.execute("UPDATE lekcje SET zajęcia_id=?, data_zajęć=?, temat_lekcji=? WHERE id=?",
                                  [zajecia_id, list_data[1], list_data[2], self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji lekcji!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del_row(self, index: int):
        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć lekcje?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM lekcje WHERE id=?", [self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Usunięcie lekcji się niepowiodło")
                self.__db.rollback()

    def __data_validation(self, list_data):
        if not (
            self.check_value_from_list(list_data[0], self.__get_list_zajecia_title(), "Klasa (Zajęcia)") and
            self.check_date(list_data[1], "Data lekcji") and
            self.check_varchar2(list_data[2], 50, "Temat lekcji") and
            self.__check_date_day_of_week(list_data[1], self.__get_zajecia_day_of_week_by_title(list_data[0]))
        ):
            return False
        return list_data

    def __get_list_zajecia_title(self):
        return [r[2] for r in self.__list_zajecia]

    def __get_zajecia_id_by_title(self, title):
        for id, _, name in self.__list_zajecia:
            if title == name:
                return id
        raise Exception("Brak id zajeć")

    def __get_zajecia_day_of_week_by_title(self, title):
        for _, day_of_week, name in self.__list_zajecia:
            if title == name:
                return day_of_week
        raise Exception("Brak dnia tygodnia zajeć")

    @staticmethod
    def __check_date_day_of_week(date, day_of_week):
        date = date.strip()
        date_split = date.split(".")
        list_day_of_week = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
        nr_day = 0

        try:
            d, m, y = int(date_split[0]), int(date_split[1]), int(date_split[2])
            date_obj = datetime.datetime(year=y, month=m, day=d)
            nr_day = date_obj.weekday()
            if day_of_week != list_day_of_week[nr_day]:
                raise Exception("Błędny dzień tygodnia")
            return True
        except Exception as e:
            print(e)
            messagebox.showerror(f"Błędny dzień tygodnia",
                                 f"Dzień tygodnia w wybranej dacie to {list_day_of_week[nr_day]}, "
                                 f"a zajęcia odbywają się w {day_of_week}")
        return False



