import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Etaty(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__rows = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__rows = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Etaty")
        table = self._create_table(frame, ["Nazwa", "Płaca minimalna", "Płaca maksymalna"], self.__rows,
                                   self.__frame_edit_row, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj etat", command=self.__frame_add_etat)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM etaty")
        rows = cur.fetchall()
        return rows

    def __frame_add_etat(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie etatu",
                                               ["Nazwa etatu", "Płaca minimalna", "Płaca maksymalna"], None,
                                               [str, str, str], self.__add_etat_to_db, "Stwórz etat", self.show_frame)
        frame.pack()

    def __add_etat_to_db(self, list_data: list[str]):
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

    def __frame_edit_row(self, id: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja etatu",
                                               ["Nazwa etatu", "Płaca minimalna", "Płaca maksymalna"], self.__rows[id],
                                               [None, str, str], self.__edit_row_in_db, "Edytuj etat", self.show_frame)
        frame.pack()

    def __edit_row_in_db(self, list_data):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("UPDATE etaty SET placa_min=?, placa_max=? WHERE nazwa=?", [list_data[1], list_data[2], list_data[0]])
                self.__db.execute("UPDATE pracownicy SET płaca=? WHERE Etaty_nazwa=? AND płaca<?", [list_data[1], list_data[0], list_data[1]])
                self.__db.execute("UPDATE pracownicy SET płaca=? WHERE Etaty_nazwa=? AND płaca>?", [list_data[2], list_data[0], list_data[2]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji etatu!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del_row(self, id: int):
        check_data = [
            [
                "SELECT * FROM pracownicy WHERE Etaty_nazwa=?",
                [self.__rows[id][0]],
                "Nie można usunąć etatu, bo istnieje pracownik zatrudniony na tym etacie"
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć etat o nazwie '{self.__rows[id][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM etaty WHERE nazwa=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")
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
            messagebox.showerror("Błędne wartości płac!", "Podane błędne wartości płac")
            return False
        return list_data
