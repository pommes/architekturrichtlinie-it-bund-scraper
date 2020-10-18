# - Neu, Geändert, Entfallen visualisieren
# - Fokus nach Tags (Kreise) visualisieren
# - Relevanz auf Systemarchitektur visualisieren
# - Übersicht der Änderungen (1 Seite)
# - Anmerkugen zu Richtlinien (1 Seite)
# -

from pprint import pprint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table
import sqlite3
from aritb_common import Quelle

database = r"architekturrichtlinie-it-bund.db"


class Database:

    def __init__(self, db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print("ERROR: {}".format(e))

    def fetch_changes(self):
        sql = ''' select * from
                (
                    select RICHTLINIE_ID, QUELLE, 'AKTIV' TYP, null "BEZEICHNUNG", null "BESCHREIBUNG" from AR_RICHTLINIE where LEBENSZYKLUS='AKTIV'
	                union
                    select RICHTLINIE_ID, QUELLE, 'NEU' TYP, BEZEICHNUNG, BESCHREIBUNG from [Aktuelle Änderungen] where beschreibung='neu'
                    union
                    select RICHTLINIE_ID, QUELLE, 'GEAENDERT' TYP, BEZEICHNUNG, BESCHREIBUNG from [Aktuelle Änderungen] where beschreibung not in ('entfallen', 'neu')
                    union
                    select RICHTLINIE_ID, QUELLE, 'ENTFALLEN' TYP, BEZEICHNUNG, BESCHREIBUNG from [Aktuelle Änderungen] where beschreibung='entfallen'
                )	
                order by TYP asc, RICHTLINIE_ID asc '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows


class Plotter:
    title_arch = 'Architekturrichtlinie'
    title_tech = 'Technische Spez.'
    help_word_table = 'In Word einfügen und in Tabelle umwandeln: Einfügen -> Tabelle -> Text in Tabelle konvertieren ...'

    def plot_anzahl_aenderungen(self, changes_db):
        order = ['NEU', 'GEAENDERT', 'ENTFALLEN']
        changes = pd.DataFrame(changes_db, columns=['id', 'quelle', 'typ', 'bezeichnung', 'beschreibung'])
        changes = changes[changes.typ.isin(['NEU', 'GEAENDERT', 'ENTFALLEN'])]

        g = changes.groupby(['typ', 'quelle']).size().to_frame('count').reset_index()
        from itertools import product
        combs = pd.DataFrame(list(product(changes['typ'].unique(), changes['quelle'].unique())),
                             columns=['typ', 'quelle'])
        result = g.merge(combs, how='right').fillna(0)
        # pprint(result)
        result = result.pivot(index='typ', columns='quelle', values='count').loc[order]
        result.columns.rename('Dokument', 1)
        result.columns = [self.title_arch, self.title_tech]
        result.index.rename('', 1)
        pprint(result)
        result.plot(kind='bar', legend=True, stacked=False, rot=0, color=tuple(['#2460A7FF', '#85B3D1FF']),
                    title='Anzahl geänderte Richtlinien je Dokument')
        plt.show()

    def plot_liste_neu(self, changes_db, quelle: Quelle):
        df = pd.DataFrame(changes_db, columns=['id', 'quelle', 'typ', 'bezeichnung', 'beschreibung'])
        df = df[df.typ.isin(['NEU'])]
        df = df[df.quelle.isin([quelle.value])]
        # pprint(df)

        print()
        print('+++ LISTE DER NEUEN RICHTLINIEN: {}'.format(quelle.value))
        print(self.help_word_table)
        print(" - - - ")
        for row in df.values:
            row = map(lambda s: s.replace('\n', ' '), row)
            print('{0}|{3}'.format(*row))
        print(" - - - ")

    def plot_liste_aenderungen(self, changes_db, quelle: Quelle):
        df = pd.DataFrame(changes_db, columns=['id', 'quelle', 'typ', 'bezeichnung', 'beschreibung'])
        df = df[df.typ.isin(['GEAENDERT'])]
        df = df[df.quelle.isin([quelle.value])]
        # pprint(df)

        print()
        print('+++ BESCHREIBUNG DER GEÄNDERTEN RICHTLINIEN: {}'.format(quelle.value))
        print(self.help_word_table)
        print(" - - - ")
        for row in df.values:
            row = map(lambda s: s.replace('\n', ' '), row)
            print('{0}|{3}|{4}'.format(*row))
        print(" - - - ")


def main():
    db = Database(database)
    changes_db = db.fetch_changes()

    plotter = Plotter()
    # plotter.plot_anzahl_aenderungen(changes_db)
    plotter.plot_liste_neu(changes_db, Quelle.ARCH)
    plotter.plot_liste_neu(changes_db, Quelle.TECH)
    plotter.plot_liste_aenderungen(changes_db, Quelle.ARCH)
    plotter.plot_liste_aenderungen(changes_db, Quelle.TECH)
    exit(0)


if __name__ == "__main__":
    main()
