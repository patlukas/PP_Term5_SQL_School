import tkinter as tk


class MainGui:
    def __init__(self):
        self.__main_window: tk.Tk = self.__create_main_window()
        self.window: tk.Frame = self.__create_main_frame()
        self.__list_buttons: list[tk.Button] = []
        self.__list_button_labels: tk[str] = []
        self.__list_button_func: list = []

    def add_option(self, label: str, func) -> None:
        self.__list_button_labels.append(label)
        self.__list_button_func.append(func)

    def start_gui(self) -> None:
        self.__add_nav_column()
        self.__main_window.mainloop()

    @staticmethod
    def __create_main_window() -> tk.Tk:
        window = tk.Tk()
        window.title("Szkoła")
        window.geometry('+10+10')  # odległość od górnej i lewej krawędzi
        window.resizable(False, False)
        window.minsize(400, 400)
        window.update_idletasks()
        return window

    def __create_main_frame(self) -> tk.Frame:
        frame = tk.Frame(master=self.__main_window)
        frame.grid(row=1, column=0)
        return frame

    def __add_nav_column(self) -> None:
        frame = tk.Frame(master=self.__main_window)
        for i, label in enumerate(self.__list_button_labels):
            click_fun = lambda x: (lambda: self.__on_click_nav_column_button(x))
            button = tk.Button(master=frame, text=label, command=click_fun(i))
            self.__list_buttons.append(button)
            button.grid(row=0, column=i)
        frame.grid(row=0, column=0)

    def __on_click_nav_column_button(self, index_selected_option: int) -> None:
        for i, button in enumerate(self.__list_buttons):
            if i == index_selected_option:
                button.config(bg="yellow")
            else:
                button.config(bg="#666666")
        self.__list_button_func[index_selected_option]()
