from MainGui import MainGui
from Klasy import Klasy
from Etaty import Etaty
from Sale import Sale
from Pracownicy import Pracownicy
from Przedmioty import Przedmioty
import sqlite3


def main():
    db = sqlite3.connect("School_DB.db")
    main_gui = MainGui()
    main_gui.add_option("Etaty", Etaty(main_gui.window, db).show_frame)
    main_gui.add_option("Pracownicy", Pracownicy(main_gui.window, db).show_frame)
    main_gui.add_option("Klasy", Klasy(main_gui.window, db).show_frame)
    main_gui.add_option("Sale", Sale(main_gui.window, db).show_frame)
    main_gui.add_option("Przedmioty", Przedmioty(main_gui.window, db).show_frame)
    main_gui.add_option("opcja 5", lambda: print("Cześć jestem 5"))
    main_gui.add_option("opcja 6", lambda: print("Cześć jestem 6"))
    main_gui.start_gui()
    db.close()


# def create_db(db: sqlite3.Connection) -> None:
#     db.execute("""DROP TABLE etaty""")
#     db.execute("""
#         CREATE TABLE etaty (
#             nazwa     VARCHAR2(20) NOT NULL PRIMARY KEY,
#             placa_min NUMBER(9, 2) NOT NULL,
#             placa_max NUMBER(9, 2) NOT NULL
#         );
#     """)
#     db.execute("""INSERT INTO etaty VALUES ('etat 1', 123.45, 678.90);""")
#     db.execute("""INSERT INTO etaty VALUES ('etat 2', 246, 2468);""")
#     db.execute("""INSERT INTO etaty VALUES ('etat 3', 333, 3333);""")
#     db.commit()


if __name__ == "__main__":
    main()




