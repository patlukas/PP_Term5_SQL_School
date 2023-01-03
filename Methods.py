import math
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import sqlite3


class Methods:
    def _create_table(self, master, labels, rows, on_edit, on_del):
        table = ttk.Treeview(master=master)
        table['columns'] = labels
        table.column("#0", width=0, stretch=tk.NO)
        for i in range(len(labels)):
            table.column(labels[i], anchor=tk.CENTER)
            table.heading(labels[i], text=labels[i], anchor=tk.CENTER)
        print(rows)
        for i, row in enumerate(rows):
            val_row = []
            for one_val in row:
                val_row.append(one_val if type(one_val) != bool else ("Tak" if one_val else "Nie"))
            table.insert(parent='', index='end', iid=i, text='', values=val_row)
        table.bind("<Button-3>", lambda x: self.__table_right_click(table, on_edit, on_del, x))
        return table

    @staticmethod
    def __table_right_click(table, on_edit, on_del, event):
        m = tk.Menu(tearoff=0)
        iid = table.identify_row(event.y)
        if on_edit is not None:
            m.add_command(label="Edytuj", command=lambda: on_edit(int(iid)))
        m.add_command(label="Usuń", command=lambda: on_del(int(iid)))
        if iid:
            table.selection_set(iid)
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()
        else:
            pass

    def _create_frame_edit_or_add(self, master, title, labels, values, types: list, on_click, button_label):
        """
        :param types: każdy element listy odpowiada jednej kolumnie, jeżeli
                        - None - wartość nie zmienialna (Label)
                        - str - wartość wpisywana ręcznie (Entry)
                        - lista z elementami - lista z wyborem (Combobox)
                        - bool - Checkbutton
        """
        frame = tk.Frame(master=master)
        list_label_el, list_input_widget, list_input_el = [], [], []
        for i, label in enumerate(labels):
            list_label_el.append(tk.Label(master=frame, text=label))
            text = "" if values is None else values[i]
            if types[i] == str:
                list_input_widget.append(tk.Entry(master=frame))
                list_input_widget[-1].insert(0, text)
            elif type(types[i]) == list:
                list_input_widget.append(ttk.Combobox(master=frame, state="readonly", values=types[i]))
                if text in types[i]:
                    list_input_widget[-1].current(types[i].index(text))
            elif types[i] == bool:
                check_var = tk.BooleanVar()
                if type(text) == bool:
                    check_var.set(text)
                list_input_widget.append(tk.Checkbutton(master=frame, variable=check_var))
                list_input_el.append(check_var)
            else:
                list_input_widget.append(tk.Label(master=frame, text=text))

            if len(list_input_widget) != len(list_input_el):
                list_input_el.append(list_input_widget[-1])
            list_label_el[-1].grid(row=1, column=i)
            list_input_widget[-1].grid(row=2, column=i)

        tk.Label(master=frame, text=title).grid(row=0, column=0, columnspan=len(list_label_el))
        button = tk.Button(master=frame, text=button_label, command=lambda: on_click(self.__get_list_str_from_list_el(list_input_el)))
        button.grid(row=3, column=len(list_label_el)-1)
        return frame

    @staticmethod
    def __get_list_str_from_list_el(list_el: list) -> list[str]:
        list_str = []
        for el in list_el:
            if type(el) in [tk.Entry, ttk.Combobox, tk.BooleanVar]:
                list_str.append(el.get())
            elif type(el) == tk.Label:
                list_str.append(el.cget("text"))
            else:
                list_str.append("")
        return list_str

    def check_varchar2(self, data, max_length, name, optional=False) -> bool:
        if len(data) > max_length:
            messagebox.showerror(f"Błędna wartość {name}", f"Długość {name} musi być dłuższa niż {max_length}")
            return False
        elif len(data) == 0 and not optional:
            messagebox.showerror(f"Błędna wartość {name}", f"{name} jest obowiązkowa")
            return False
        return True

    @staticmethod
    def check_number(data, precision, scale, name) -> bool:
        if data == "":
            messagebox.showerror(f"Błędna wartość {name}", f"{name} jest obowiązkowa")
            return False
        try:
            data = float(data)
            if data != math.floor(data*10**scale) / 10**scale:
                messagebox.showerror(f"Błędna wartość {name}", f"{name} może mieć maksymalnie {scale} cyfry po przecinku")
                return False
            data = abs(data)
            while data != int(data):
                data *= 10
            if data >= 10**precision:
                messagebox.showerror(f"Błędna wartość {name}",
                                     f"{name} może mieć maksymalnie {precision} cyfry")
                return False
        except ValueError:
            messagebox.showerror(f"Błędna wartość {name}", f"{name} musi być liczbą")
            return False
        return True

    @staticmethod
    def check_foreign_key(data, list_foreign_key, name) -> bool:
        if data in list_foreign_key:
            return True
        else:
            messagebox.showerror(f"Błędna wartość {name}", f"{name} musi być wybrane z listy kluczów obcych")
            return False

    @staticmethod
    def check_pesel(data: str, name="Pesel") -> bool:
        if len(data) != 11:
            messagebox.showerror(f"Błędna długość {name}", f"{name} musi mieć długość równą 11")
        elif not data.isnumeric():
            messagebox.showerror(f"Błędna wartość {name}", f"{name} musi składać się wyłącznei z cyfr")
        else:
            return True

    @staticmethod
    def check_date(data: str, name) -> bool:
        data = data.strip()
        date_split = data.split(".")
        if len(date_split) != 3:
            messagebox.showerror(f"Błędna format {name}", f"{name} mui być w formacie 'DD.MM.RRRR'")
        elif not date_split[0].isnumeric() or not date_split[1].isnumeric() or not date_split[2].isnumeric():
            messagebox.showerror(f"Błędna format {name}", f"{name} dzień, miesiąc i rok muszą być cyframi")
        else:
            try:
                d, m, y = int(date_split[0]), int(date_split[1]), int(date_split[2])
                datetime.datetime(year=y, month=m, day=d)
                return True
            except Exception as e:
                print(e)
                messagebox.showerror(f"Błędna format {name}", f"{name} jest błędną datą")
        return False

    @staticmethod
    def check_delete_is_possible(db: sqlite3.Connection, data: list[list]) -> bool:
        """
        :param db: połączenie z bazą danych
        :param data: lista trzyelementowych list z kolejno poleceniem sql, atrybutami do polecenia, treścią wiadomości do pokazania jak polecenie coś zwróci
            [
                str <polecenie SELECT sprawdzające czy sprawdzany rekord jest użyty>,
                list <lista strybutów potrzebnych do wywołania polecenia sql (to co trzeba wstawić zamiast '?'>
                str <wiadomość, jaka ma zostać wyświetlona w przypadku, gdy rekord jest używany>
            ]
        :return: True jeżeli można usunąć rekord, False jeżeli nie można usunąć rekordu
        """
        try:
            for sql, attributes, message in data:
                cur = db.cursor()
                cur.execute(sql, attributes)
                if cur.fetchone() is not None:
                    messagebox.showinfo("Problem z usuwaniem", message)
                    return False
            return True
        except Exception as e:
            print(e)
            messagebox.showerror("", "Błąd przy sprawdzaniu, czy usunięcie jest możliwe")
            return False
