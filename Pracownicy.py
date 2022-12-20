import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Pracownicy(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__rows = []
        self.__list_etat_row = []
        self.__list_etat = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__list_etat_row = self.__get_list_etat_row()
        self.__list_etat = [row[0] for row in self.__list_etat_row]
        self.__rows = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Pracownicy")
        table = self._create_table(frame, ["Pesel", "Imie", "Nazwisko", "Data urodzenia", "Data zatrudnienia", "Płaca", "Etat"],
                                   self.__rows, self.__frame_edit_row, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj pracownika", command=self.__frame_add_etat)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM pracownicy")
        rows = cur.fetchall()
        return rows

    def __get_list_etat_row(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        rows = cur.fetchall()
        return rows

    def __frame_add_etat(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie pracownika",
                                               ["Pesel", "Imie", "Nazwisko", "Data urodzenia", "Data zatrudnienia", "Płaca", "Etat"],
                                               None,
                                               [str, str, str, str, str, str, self.__list_etat], self.__add_pracownik_to_db, "Stwórz pracownika")
        frame.pack()

    def __frame_edit_row(self, id: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja pracownika",
                                               ["Pesel", "Imie", "Nazwisko", "Data urodzenia", "Data zatrudnienia", "Płaca", "Etat"],
                                               self.__rows[id],
                                               [None, str, str, str, str, str, self.__list_etat], self.__edit_row_in_db, "Edytuj pracownika")
        frame.pack()

    def __frame_del_row(self, id: int):
        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć pracownika z peselem '{self.__rows[id][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM pracownicy WHERE pesel=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")

    def __add_pracownik_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO pracownicy VALUES(?, ?, ?, ?, ?, ?, ?)", list_data)
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie pracownika!", "Pesel musi być unikalna")
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie pracownika!", "Niezydentyfikowany błąd")

    def __edit_row_in_db(self, list_data):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute(
                    "UPDATE pracownicy SET imie=?, nazwisko=?, data_urodzenia=?, data_zatrudnienia=?, płaca=?, Etaty_nazwa=?  WHERE pesel=?",
                    [list_data[1], list_data[2], list_data[3], list_data[4], list_data[5], list_data[6], list_data[0]]
                )
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
            self.check_foreign_key(list_data[6], self.__list_etat, "Etat")
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
