import sqlite3
import tkinter as tk
from tkinter import messagebox
from Methods import Methods


class Zajecia(Methods):
    def __init__(self, window: tk.Frame, db: sqlite3.Connection):
        self.__window = window
        self.__db = db
        self.__list_labels = ["Klasa", "Dzień zajęć", "Godzina zajęć", "Sala", "Przedmiot i Nauczyciel"]
        self.__list_day = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
        self.__list_hour = ["8:00 - 8:45", "8:55 - 9:40", "9:50 - 10:35", "10:45 - 11:30", "11:45 - 12:30", "12:40 - 13:25", "13:35 - 14:20", "14:30 - 15:15", "15:25 - 16:10"]
        self.__list_przedmiot_and_teacher = self.__get_list_przedmiot_and_teacher()
        self.__list_klasy = self.__get_list_klasy()
        self.__list_sale = self.__get_list_sale()
        self.__list_id = []
        self.__rows = []

    def show_frame(self) -> None:
        self.__db.commit()
        self.__list_przedmiot_and_teacher = self.__get_list_przedmiot_and_teacher()
        self.__list_klasy = self.__get_list_klasy()
        self.__list_sale = self.__get_list_sale()
        self.__rows, self.__list_id = self.__get_rows_data()
        print(self.__rows)
        print(self.__list_id)
        for x in self.__window.winfo_children():
            x.destroy()
        frame = tk.Frame(master=self.__window)
        label = tk.Label(master=frame, text="Zajęcia")
        table = self._create_table(frame, self.__list_labels, self.__rows, self.__frame_edit, self.__frame_del_row)
        button = tk.Button(master=frame, text="Dodaj nowe zajęcia", command=self.__frame_add)
        label.pack()
        table.pack()
        button.pack()
        frame.pack()

    def __get_rows_data(self):
        cur = self.__db.cursor()
        cur.execute("SELECT Klasy_nazwa, Klasy_rocznik, Nauczyciele_pesel, Przedmioty_nazwa, Sale_numer, dzień_zajęc, godzina_zajęć, id FROM zajecia")
        rows_read = cur.fetchall()
        rows, list_id = [], []
        for row in rows_read:
            przedmiot_and_teacher = ""
            for przedmiot_name, teacher_pesel, teacher_name, full_name in self.__get_list_przedmiot_and_teacher():
                if row[2] == teacher_pesel and row[3] == przedmiot_name:
                    przedmiot_and_teacher = full_name
                    break
            klasa = ""
            for name, rocznik, full_name in self.__list_klasy:
                if row[0] == name and row[1] == rocznik:
                    klasa = full_name
                    break

            rows.append([klasa, row[5], row[6], str(row[4]), przedmiot_and_teacher])
            list_id.append(row[7])
        return rows, list_id

    def __get_list_przedmiot_and_teacher(self):
        cur = self.__db.cursor()
        cur.execute("SELECT np.przedmiot_nazwa, p.pesel, p.nazwisko || ' ' || p.imie FROM nauczyciele_przedmioty np JOIN pracownicy p ON p.pesel = np.nauczyciel_pesel")
        return [[el[0], el[1], el[2], f"{el[0]} <{el[2]} ({el[1]})>"] for el in cur.fetchall()]

    def __get_list_sale(self):
        cur = self.__db.cursor()
        cur.execute("SELECT numer FROM sale")
        return [str(el[0]) for el in cur.fetchall()]

    def __get_list_klasy(self):
        cur = self.__db.cursor()
        cur.execute("SELECT nazwa, rocznik FROM klasy")
        return [[el[0], el[1], f"{el[0]} ({el[1]})"] for el in cur.fetchall()]

    def __frame_add(self):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Dodanie zajęć",
                                               self.__list_labels, None,
                                               [self.__get_list_klasy_full_name(), self.__list_day, self.__list_hour,
                                                self.__list_sale, self.__get_list_string_przedmioty_and_teacher()],
                                               self.__add_to_db, "Stwórz")
        frame.pack()

    def __add_to_db(self, list_data: list[str]):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                klasa_nazwa = przedmiot_nazwa = nauczyciel_pesel = klasa_rocznik = ""

                for klasa in self.__list_klasy:
                    if klasa[2] == list_data[0]:
                        klasa_nazwa = klasa[0]
                        klasa_rocznik = klasa[1]
                        break

                for przedmiot_teacher in self.__list_przedmiot_and_teacher:
                    if przedmiot_teacher[3] == list_data[4]:
                        przedmiot_nazwa = przedmiot_teacher[0]
                        nauczyciel_pesel = przedmiot_teacher[1]
                        break

                self.__db.execute("INSERT INTO zajecia VALUES((SELECT MAX(id) + 1 FROM zajecia), ?, ?, ?, ?, ?, ?, ?)",
                                  [klasa_nazwa, list_data[1], list_data[2], list_data[3], przedmiot_nazwa, nauczyciel_pesel, klasa_rocznik])
                self.show_frame()
            except sqlite3.IntegrityError:
                messagebox.showerror("Błąd podczas dodawania!", "Takie zajęcia już istnieją")
                self.__db.rollback()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd podczas dodawania!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_edit(self, index: int):
        for x in self.__window.winfo_children():
            x.destroy()
        frame = self._create_frame_edit_or_add(self.__window, "Edycja zajęć",
                                               self.__list_labels, self.__rows[index],
                                               [self.__get_list_klasy_full_name(), self.__list_day, self.__list_hour,
                                                self.__list_sale, self.__get_list_string_przedmioty_and_teacher()],
                                               lambda list_data: self.__edit_row_in_db(list_data, index), "Edytuj zajęcia")
        frame.pack()

    def __edit_row_in_db(self, list_data, index):
        list_data = self.__data_validation(list_data)
        if list_data is not False:
            try:
                klasa_nazwa = przedmiot_nazwa = nauczyciel_pesel = klasa_rocznik = ""

                for klasa in self.__list_klasy:
                    if klasa[2] == list_data[0]:
                        klasa_nazwa = klasa[0]
                        klasa_rocznik = klasa[1]
                        break

                for przedmiot_teacher in self.__list_przedmiot_and_teacher:
                    if przedmiot_teacher[3] == list_data[4]:
                        przedmiot_nazwa = przedmiot_teacher[0]
                        nauczyciel_pesel = przedmiot_teacher[1]
                        break

                self.__db.execute("UPDATE zajecia SET klasy_nazwa=?, dzień_zajęc=?, godzina_zajęć=?, sale_numer=?, przedmioty_nazwa=?, nauczyciele_pesel=?, klasy_rocznik=? WHERE id=?",
                                  [klasa_nazwa, list_data[1], list_data[2], list_data[3], przedmiot_nazwa,
                                   nauczyciel_pesel, klasa_rocznik, self.__list_id[index]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy edycji zajęć!", "Niezydentyfikowany błąd")
                self.__db.rollback()

    def __frame_del_row(self, id: int):
        check_data = [
            [
                "SELECT * FROM lekcje WHERE zajęcia_id=?", [self.__list_id[id]],
                "Nie można usunąć przedmiotu zajęć, bo przeprowadzone lekcje z tych zajęć"
            ]
        ]
        if not self.check_delete_is_possible(self.__db, check_data):
            return

        decision = messagebox.askquestion("Usuwanie rekordu", f"Czy jesteś pewny że chcesz usunąć zajęcia?")
        if decision == "yes":
            try:
                self.__db.execute("DELETE FROM zajecia WHERE id=?", [self.__list_id[id]])
                self.show_frame()
            except Exception as e:
                print(e)
                messagebox.showerror("Błąd przy usuwaniu rekordu!", f"Usunięcie zajęć się niepowiodło")
                self.__db.rollback()

    def __data_validation(self, list_data):
        if not (
            self.check_value_from_list(list_data[0], self.__get_list_klasy_full_name(), "Klasa") and
            self.check_value_from_list(list_data[1], self.__list_day, "Dzień zajęć") and
            self.check_value_from_list(list_data[2], self.__list_hour, "Godzina zajęć") and
            self.check_value_from_list(list_data[3], self.__list_sale, "Sala") and
            self.check_value_from_list(list_data[4], self.__get_list_string_przedmioty_and_teacher(), "Przedmiot i Nauczyciel")
        ):
            return False
        return list_data

    def __get_list_klasy_full_name(self):
        return [r[2] for r in self.__list_klasy]

    def __get_list_string_przedmioty_and_teacher(self):
        return [r[3] for r in self.__list_przedmiot_and_teacher]
