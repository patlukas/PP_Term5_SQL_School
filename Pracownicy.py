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
        self.__db.commit()
        self.__list_etat_row = self.__get_list_etat_row()
        self.__list_etat = [row[0] for row in self.__list_etat_row]
        self.__rows = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Pracownicy")
        table = self._create_table(frame, self.__list_labels, self.__rows, self.__frame_edit_row, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj etat", command=self.__frame_add_etat)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM pracownicy")
        rows_pracownicy = cur.fetchall()
        cur.execute("SELECT pesel FROM nauczyciele")
        rows_nauczyciele = cur.fetchall()
        nauczyciele = [nauczyciel[0] for nauczyciel in rows_nauczyciele]
        rows = []
        for i in range(len(rows_pracownicy)):
            rows.append(list(rows_pracownicy[i]) + [rows_pracownicy[i][0] in nauczyciele])
        return rows

    def __get_list_etat_row(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        rows = cur.fetchall()
        return rows

    def __frame_add_etat(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie pracownika", self.__list_labels, None,
                                               [str, str, str, str, str, str, self.__list_etat, bool],
                                               self.__add_pracownik_to_db, "Stwórz pracownika")
        frame.pack()

    def __frame_edit_row(self, id: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja pracownika", self.__list_labels, self.__rows[id],
                                               [None, str, str, str, str, str, self.__list_etat, bool],
                                               self.__edit_row_in_db, "Edytuj pracownika")
        frame.pack()

    def __frame_del_row(self, id: int):
        if self.__check_teacher_is_used(self.__rows[id][0], "Nie można usunąć pracownika z rolą nauczyciela"):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć pracownika z peselem '{self.__rows[id][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM pracownicy WHERE pesel=?", [self.__rows[id][0]])
                self.__db.execute("DELETE FROM nauczyciele WHERE pesel=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")
                self.__db.rollback()

    def __add_pracownik_to_db(self, list_data: list[str]):
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
                "SELECT * FROM Klasy WHERE Nauczyciele_pesel=?", [pesel],
                f"{message}, bo jest wychowawca klasy"
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
                    messagebox.showerror("Błędna płaca!",
                                         f"Płaca musi być z przedniału od {etat_row[1]} do {etat_row[2]}")
                    return False
        return list_data
