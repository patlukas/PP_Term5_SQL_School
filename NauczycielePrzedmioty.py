import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class NauczycielePrzedmioty(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Nauczyciel", "Przedmiot"]
        self.__list_przedmioty = self.__get_list_przedmioty()
        self.__list_teacher = self.__get_list_teacher()
        self.__rows = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__list_przedmioty = self.__get_list_przedmioty()
        self.__list_teacher = self.__get_list_teacher()
        self.__rows = self.__get_rows_data()
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        tk.Label(master=frame, text="Przedmioty nauczycieli").pack()
        self._create_table(frame, self.__list_labels, self.__rows, None, self.__frame_del_row).pack()
        tk.Button(master=frame, text="Dodaj nauczycielowi przedmiot", command=self.__frame_add).pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT Nauczyciel_pesel, Przedmiot_nazwa FROM Nauczyciele_przedmioty ORDER BY Nauczyciel_pesel, Przedmiot_nazwa")
        rows_read = cur.fetchall()
        rows = []
        for nauczyciel_pesel, przedmiot_name in rows_read:
            nauczyciel_name = ""
            for pesel, name in self.__list_teacher:
                if nauczyciel_pesel == pesel:
                    nauczyciel_name = name
                    break
            rows.append([nauczyciel_name, przedmiot_name])
        return rows

    def __get_list_przedmioty(self):
        cur = self.__db.cursor()
        cur.execute("SELECT nazwa FROM przedmioty")
        return [el[0] for el in cur.fetchall()]

    def __get_list_teacher(self):
        cur = self.__db.cursor()
        cur.execute("SELECT p.pesel, p.nazwisko || ' ' || p.imie FROM nauczyciele n JOIN pracownicy p ON n.pesel = p.pesel")
        list_rows_from_db = cur.fetchall()
        rows = [[pesel, nazwa+" ("+pesel+")"] for pesel, nazwa in list_rows_from_db]
        return rows

    def __frame_add(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie nauczycielowi kolejnego przedmiotu",
                                               self.__list_labels, None,
                                               [self.__get_list_teacher_name(), self.__list_przedmioty], self.__add_to_db, "Stwórz")
        frame.pack()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO Nauczyciele_przedmioty VALUES(?, ?)",
                                  [self.__get_teacher_pesel(list_data[0]), list_data[1]])
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd podczas dodawania!", "Wybrany nauczyciel uczy już tego przedmiotu")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd podczas dodawania!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del_row(self, id: int):
        check_data = [
            [
                "SELECT * FROM oceny WHERE Nauczyciele_pesel=? AND Przedmioty_nazwa=?",
                [self.__get_teacher_pesel(self.__rows[id][0]), self.__rows[id][1]],
                "Nie można usunąć przedmiotu nauczycielowi, bo istnieje ocena wystawiona z tego przedmiotu przez tego nauczyciela"
            ],
            [
                "SELECT * FROM sprawdziany WHERE Nauczyciele_pesel=? AND Przedmioty_nazwa=?",
                [self.__get_teacher_pesel(self.__rows[id][0]), self.__rows[id][1]],
                "Nie można usunąć przedmiotu nauczycielowi, bo istnieje zaplanowany sprawdzian z tego przedmiotu przez tego naucyciela"
            ],
            [
                "SELECT * FROM zajecia WHERE Nauczyciele_pesel=? AND Przedmioty_nazwa=?",
                [self.__get_teacher_pesel(self.__rows[id][0]), self.__rows[id][1]],
                "Nie można usunąć przedmiotu nauczycielowi, bo istnieją zajęcia z tego przedmiotu które prowadzi ten nauczyciel"
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć przedmiot nauczycielowi?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM Nauczyciele_przedmioty WHERE  Nauczyciel_pesel=? AND Przedmiot_nazwa=?",
                                  [self.__get_teacher_pesel(self.__rows[id][0]), self.__rows[id][1]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Usunięcie się niepowiodło")
                self.__db.rollback()

    def __data_validation(self, list_data):
        if not (
            self.check_value_from_list(list_data[0], self.__get_list_teacher_name(), "Nauczyciel") and
            self.check_value_from_list(list_data[1], self.__list_przedmioty, "Przedmiot")
        ):
            return False
        return list_data

    def __get_list_teacher_name(self):
        return [teacher[1] for teacher in self.__list_teacher]

    def __get_teacher_pesel(self, teacher_name):
        for nauczyciel_pesel, nauczyciel_name in self.__list_teacher:
            if teacher_name == nauczyciel_name:
                return nauczyciel_pesel
        return ""


