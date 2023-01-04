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
        current_year = date.today().year
        self.__list_rocznik = [f"{r}/{r + 1}" for r in range(current_year, 2000, -1)]

    def show_frame(self) -> None:
        self.__db.commit()
        self.__list_teacher = self.__get_list_teacher()
        self.__rows = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Klasy")
        table = self._create_table(frame, self.__list_labels, self.__rows, self.__frame_edit_row, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj klasę", command=self.__frame_add_klasa)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM klasy")
        rows_klasy = cur.fetchall()
        rows = []
        for nazwa, wychowawca_pesel, rocznik in rows_klasy:
            wychowawca = ""
            for nauczyciel_pesel, nauczyciel in self.__list_teacher:
                if nauczyciel_pesel == wychowawca_pesel:
                    wychowawca = nauczyciel
                    break
            rows.append([nazwa, rocznik, wychowawca])
        return rows

    def __get_list_teacher(self):
        cur = self.__db.cursor()
        cur.execute("SELECT p.pesel, p.nazwisko || ' ' || p.imie FROM nauczyciele n JOIN pracownicy p ON n.pesel = p.pesel")
        list_rows_from_db = cur.fetchall()
        rows = [[pesel, nazwa+" ("+pesel+")"] for pesel, nazwa in list_rows_from_db]
        return rows

    def __frame_add_klasa(self):
        for x in self.__window.winfo_children():
            x.destroy()
        list_teacher_name = [teacher[1] for teacher in self.__list_teacher]
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie klasy", self.__list_labels, None,
                                               [str, self.__list_rocznik, list_teacher_name],
                                               self.__add_klasa_to_db, "Stwórz klasę")
        frame.pack()

    def __frame_edit_row(self, id: int):
        for x in self.__window.winfo_children():
            x.destroy()
        list_teacher_name = [teacher[1] for teacher in self.__list_teacher]
        frame = self._create_frame_edit_or_add(self.__window, "Edycja klasy", self.__list_labels, self.__rows[id],
                                               [None, None, list_teacher_name],
                                               self.__edit_row_in_db, "Edytuj klasę")
        frame.pack()

    def __frame_del_row(self, id: int):
        arg = [self.__rows[id][0], self.__rows[id][1]]
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

    def __add_klasa_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)

        if list_data is not False:
            try:
                pesel = self.__get_teacher_pesel(list_data[2])
                self.__db.execute("INSERT INTO klasy VALUES(?, ?, ?)", [list_data[0], pesel, list_data[1]])
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie klasy!", "Już istnieje klasa z taką nazwą w wybranym roczniku")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie klasy!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __edit_row_in_db(self, list_data):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                pesel = self.__get_teacher_pesel(list_data[2])
                self.__db.execute(
                    "UPDATE klasy SET nauczyciele_pesel=? WHERE nazwa=? AND rocznik=?",
                    [pesel, list_data[0], list_data[1]]
                )
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji klasy!", "Niezydentyfikowany błąd")

    def __data_validation(self, list_data):
        list_nauczyciel_name = [name for _, name in self.__list_teacher]
        if not (
                self.check_varchar2(list_data[0], 5, "Nazwa klasy") and
                self.check_value_from_list(list_data[1], self.__list_rocznik, "Rocznik") and
                self.check_value_from_list(list_data[2], list_nauczyciel_name, "Wychowawca")
        ):
            return False
        return list_data

    def __get_teacher_pesel(self, wychowawca_name) -> str:
        for nauczyciel_pesel, nauczyciel_name in self.__list_teacher:
            if wychowawca_name == nauczyciel_name:
                return nauczyciel_pesel
        return ""
