import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Przedmioty(Methods):
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
        label = tk.Label(master=frame, text="Przedmioty")
        table = self._create_table(frame, ["Nazwa"], self.__rows,
                                   None, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj przedmiot", command=self.__frame_add_przedmiot)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM przedmioty")
        rows = cur.fetchall()
        return rows

    def __frame_add_przedmiot(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie nowego przedmiotu",
                                               ["Nazwa"],
                                               None,
                                               [str],
                                               self.__add_przedmiot_to_db, "Dodaj przedmiot")
        frame.pack()



    def __frame_del_row(self, id: int):
        decision = messagebox.askquestion("Usuwanie rekordu",
                                          f"Czy jesteś pewny że chcesz usunąć przedmiot '{self.__rows[id][0]}'?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM przedmioty WHERE nazwa=?", [self.__rows[id][0]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Niepowiodło się usunięcie '{self.__rows[id][0]}'")

    def __add_przedmiot_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                self.__db.execute("INSERT INTO przedmioty VALUES(?)", list_data)
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd przy dodanianie przedmiotu!", "Nazwa przedmiotu musi być unikalna")
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy dodanianie przedmiotu!", "Niezydentyfikowany błąd")

    def __data_validation(self, list_data):
        print(list_data)
        return list_data