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
