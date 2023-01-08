import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Uczniowie(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Pesel", "Imie", "Nazwisko", "Data urodzenia", "Klasa"]
        self.__rows = []
        self.__klasy_rows = []
        self.__klasy = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__rows = self.__get_rows_data()
        self.__klasy_rows = self.__get_rows_klasy()
        self.__klasy = [str(k[0]) + " " + str(k[2]) for k in self.__klasy_rows]

        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Uczniowie")
        table = self._create_table(frame, self.__list_labels, self.__rows, self.__frame_edit_row, self.__frame_del_row)
        button = tk.Button(master=frame, text="Nowy uczeń", command=self.__frame_add_uczen)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM uczniowie")
        rows = cur.fetchall()
        new_rows = []
        for row in rows:
            new_rows.append((row[0], row[1], row[2], row[3], row[4] + " " + row[5]))
        return new_rows

    def __get_rows_klasy(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM klasy")
        rows = cur.fetchall()

        return rows

    def __frame_add_uczen(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie nowego ucznia",
                                               ["Pesel", "Imię", "Nazwisko", "Data urodzenia", "Klasa"],
                                               None,
                                               [str, str, str, str, self.__klasy],
                                               self.__add_uczen_to_db, "Dodaj", self.show_frame)
        frame.pack()

    def __add_uczen_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)

        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO uczniowie VALUES(?, ?, ?, ?, ?, ?)", list_data)
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianiu ucznia!", "Pesel musi być unikalny")
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianiu ucznia!", "Niezydentyfikowany błąd")

    def __data_validation(self, list_data):
        if not (
            self.check_pesel(list_data[0]) and
            self.check_date(list_data[3], "Data urodzenia") and
            self.check_varchar2(list_data[1], 30, "imie") and
            self.check_varchar2(list_data[2], 30, "nazwisko") and
            self.check_value_from_list(list_data[4], self.__klasy, "Klasa")
        ):
            return False

        klasa_nazwa_rocznik = list_data.pop().split(' ')
        list_data.append(klasa_nazwa_rocznik[0])
        list_data.append(klasa_nazwa_rocznik[1])

        return list_data

    def __frame_edit_row(self, id: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja ucznia",
                                               ["Pesel", "Imię", "Nazwisko", "Data urodzenia", "Klasa"],
                                               self.__rows[id],
                                               [None, str, str, str, self.__klasy],
                                               self.__edit_row_in_db, "Edytuj ucznia", self.show_frame)
        frame.pack()

    def __edit_row_in_db(self, list_data):
        list_data = self.__data_validation(list_data)

        if list_data is not False:
            try:

                self.__db.execute(
                    "UPDATE uczniowie SET imie=?, nazwisko=?, data_urodzenia=?, klasy_nazwa=?, klasy_rocznik=?  WHERE pesel=?",
                    [list_data[1], list_data[2], list_data[3], list_data[4], list_data[5], list_data[0]]
                )

                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji pracownika!", "Niezydentyfikowany błąd")

    def __frame_del_row(self, id: int):
        check_data = [
            [
                "SELECT * FROM oceny WHERE uczniowie_pesel=?",
                [self.__rows[id][0]],
                "Nie można usunąć ucznia, ponieważ są do niego przypisane oceny."
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć ucznia ('{self.__rows[id][0]}')  {self.__rows[id][1]} {self.__rows[id][2]}?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM uczniowie WHERE pesel=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")
