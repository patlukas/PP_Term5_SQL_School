import tkinter as tk
from tkinter import ttk

class GuiMethods:
    def _create_table(self, master, labels, rows, on_edit, on_del):
        table = ttk.Treeview(master=master)
        table['columns'] = labels
        table.column("#0", width=0, stretch=tk.NO)
        for i in range(len(labels)):
            table.column(labels[i], anchor=tk.CENTER)
            table.heading(labels[i], text=labels[i], anchor=tk.CENTER)
        for i, row in enumerate(rows):
            table.insert(parent='', index='end', iid=i, text='', values=row)
        table.bind("<Button-3>", lambda x: self.__table_right_click(table, on_edit, on_del, x))
        return table

    @staticmethod
    def __table_right_click(table, on_edit, on_del, event):
        m = tk.Menu()
        iid = table.identify_row(event.y)
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

    @staticmethod
    def _create_frame_edit_or_add(master, title, labels, values, on_click, button_label):
        frame = tk.Frame(master=master)
        list_label_el = []
        list_entry_el = []
        for i, label in enumerate(labels):
            list_label_el.append(tk.Label(master=frame, text=label))
            list_entry_el.append(tk.Entry(master=frame))
            list_label_el[-1].grid(row=1, column=i)
            list_entry_el[-1].grid(row=2, column=i)
            if values is not None:
                list_entry_el[-1].insert(0, values[i])

        tk.Label(master=frame, text=title).grid(row=0, column=0, columnspan=len(list_label_el))
        button = tk.Button(master=frame, text=button_label, command=lambda: on_click(list_entry_el))
        button.grid(row=3, column=len(list_label_el)-1)
        return frame
