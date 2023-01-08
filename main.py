from MainGui import MainGui
from Klasy import Klasy
from Etaty import Etaty
from Sale import Sale
from Pracownicy import Pracownicy
from Przedmioty import Przedmioty
from NauczycielePrzedmioty import NauczycielePrzedmioty
from Zajecia import Zajecia
from Uczniowie import Uczniowie
from Lekcje import Lekcje
from Oceny import Oceny
from Sprawdziany import Sprawdziany
import sqlite3


def main():
    db = sqlite3.connect("School_DB.db")
    main_gui = MainGui()
    main_gui.add_option("Etaty", Etaty(main_gui.window, db).show_frame)
    main_gui.add_option("Pracownicy", Pracownicy(main_gui.window, db).show_frame)
    main_gui.add_option("Klasy", Klasy(main_gui.window, db).show_frame)
    main_gui.add_option("Sale", Sale(main_gui.window, db).show_frame)
    main_gui.add_option("Przedmioty", Przedmioty(main_gui.window, db).show_frame)
    main_gui.add_option("Przedmioty nauczycieli", NauczycielePrzedmioty(main_gui.window, db).show_frame)
    main_gui.add_option("Zajęcia", Zajecia(main_gui.window, db).show_frame)
    main_gui.add_option("Uczniowie", Uczniowie(main_gui.window, db).show_frame)
    main_gui.add_option("Lekcje", Lekcje(main_gui.window, db).show_frame)
    main_gui.add_option("Oceny", Oceny(main_gui.window, db).show_frame)
    main_gui.add_option("Sprawdziany", Sprawdziany(main_gui.window, db).show_frame)
    main_gui.start_gui()
    db.close()


if __name__ == "__main__":
    main()




