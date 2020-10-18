# - Neu, Geändert, Entfallen visualisieren
# - Fokus nach Tags (Kreise) visualisieren
# - Relevanz auf Systemarchitektur visualisieren
# - Übersicht der Änderungen (1 Seite)
# - Anmerkugen zu Richtlinien (1 Seite)
# -

from pprint import pprint
import numpy as np
import pandas as pd
import seaborn as sns
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
                    select RICHTLINIE_ID, QUELLE, 'AKTIV' TYP, null "BEZEICHNUNG", null "VERBINDLICHKEIT", null "BESCHREIBUNG" from AR_RICHTLINIE where LEBENSZYKLUS='AKTIV'
	                union
                    select RICHTLINIE_ID, QUELLE, 'NEU' TYP, BEZEICHNUNG, VERBINDLICHKEIT, BESCHREIBUNG from [Aktuelle Änderungen] where beschreibung='neu'
                    union
                    select RICHTLINIE_ID, QUELLE, 'GEAENDERT' TYP, BEZEICHNUNG, VERBINDLICHKEIT, BESCHREIBUNG from [Aktuelle Änderungen] where beschreibung not in ('entfallen', 'neu')
                    union
                    select RICHTLINIE_ID, QUELLE, 'ENTFALLEN' TYP, BEZEICHNUNG, VERBINDLICHKEIT, BESCHREIBUNG from [Aktuelle Änderungen] where beschreibung='entfallen'
                )	
                order by TYP asc, RICHTLINIE_ID asc '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def fetch_tags(self):
        sql = ''' select
                    r.RICHTLINIE_ID ID,
                    t.TAG,
                    r.QUELLE,
                    d.BEZEICHNUNG,
                    d.VERBINDLICHKEIT
                from 
                    AR_TAG t
                    inner join AR_RICHTLINIE r on r.RICHTLINIE_ID=t.RICHTLINIE_ID
                    inner join AR_DETAIL d on r.DETAIL_ID_AKTUELL=d.id
                where 1=1
                    and r.LEBENSZYKLUS='AKTIV'
                order by t.tag '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows


class Plotter:
    title_arch = 'Architekturrichtlinie'
    title_tech = 'Technische Spez.'
    help_word_table = 'In Word einfügen und in Tabelle umwandeln: Einfügen -> Tabelle -> Text in Tabelle konvertieren ...'

    def __init__(self, db: Database):
        # Activate seaborn
        sns.set()
        # Read from db
        self.tags_db = db.fetch_tags()
        self.changes_db = db.fetch_changes()

    def plot_anzahl_aenderungen(self):
        order = ['NEU', 'GEAENDERT', 'ENTFALLEN']
        changes = pd.DataFrame(self.changes_db, columns=['id', 'quelle', 'typ', 'bezeichnung', 'verbindlichkeit', 'beschreibung'])
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

    def plot_liste_neu(self, quelle: Quelle):
        return self.plot_liste_neu_entfallen(quelle, ['NEU'])

    def plot_liste_entfallen(self, quelle: Quelle):
        return self.plot_liste_neu_entfallen(quelle, ['ENTFALLEN'])

    def plot_liste_neu_entfallen(self, quelle: Quelle, filterlist_typ):
        df = pd.DataFrame(self.changes_db, columns=['id', 'quelle', 'typ', 'bezeichnung', 'verbindlichkeit', 'beschreibung'])
        df = df[df.typ.isin(filterlist_typ)]
        df = df[df.quelle.isin([quelle.value])]
        df = df.fillna('')
        #pprint(df)

        print()
        print('+++ LISTE DER RICHTLINIEN {}: {}'.format(filterlist_typ, quelle.value))
        print(self.help_word_table)
        print(" - - - ")
        for row in df.values:
            row = map(lambda s: s.replace('\n', ' '), row)
            print('{0}|{3}|{4}'.format(*row))
        print(" - - - ")

    def plot_liste_aenderungen(self, quelle: Quelle):
        df = pd.DataFrame(self.changes_db, columns=['id', 'quelle', 'typ', 'bezeichnung', 'verbindlichkeit', 'beschreibung'])
        df = df[df.typ.isin(['GEAENDERT'])]
        df = df[df.quelle.isin([quelle.value])]
        #pprint(df)

        print()
        print('+++ BESCHREIBUNG DER GEÄNDERTEN RICHTLINIEN: {}'.format(quelle.value))
        print(self.help_word_table)
        print(" - - - ")
        for row in df.values:
            row = map(lambda s: s.replace('\n', ' '), row)
            print('{0}|{3}|{5}|{4}'.format(*row))
        print(" - - - ")

    def plot_tags(self):
        tags = pd.DataFrame(self.tags_db, columns=['id', 'tag', 'quelle', 'bezeichnung', 'verbindlichkeit'])
        tags = tags.groupby(['tag']).size().to_frame('count').sort_values('count', ascending=False)

        tags.columns.rename('Dokument', 1)
        #tags.columns = [self.title_arch, self.title_tech]
        tags.index.rename('Schlagwort', 1)
        #pprint(tags)
        sns.heatmap(tags, annot=True, fmt=".0f")
        plt.show()

    def plot_liste_tags(self):
        df = pd.DataFrame(self.tags_db, columns=['id', 'tag', 'quelle', 'bezeichnung', 'verbindlichkeit'])
        df = df.sort_values(['tag', 'id'])
        pprint(df)
        tag = ''
        ids = ''
        for row in df.values:
            #row = map(lambda s: s.replace('\n', ' '), row)

            if tag == row[1]:
                str = '{}{}' if ids == '' else '{}, {}'
                ids = str.format(ids, row[0])
            else:
                print('{}|{}'.format(row[1], ids))
                ids=''

            tag=row[1]

def main():
    db = Database(database)
    changes_db = db.fetch_changes()

    plotter = Plotter(db)
    #plotter.plot_tags()
    plotter.plot_liste_tags()
    exit(0)

    plotter.plot_anzahl_aenderungen()
    plotter.plot_liste_neu(Quelle.ARCH)
    plotter.plot_liste_neu(Quelle.TECH)
    plotter.plot_liste_aenderungen(Quelle.ARCH)
    plotter.plot_liste_aenderungen(Quelle.TECH)
    plotter.plot_liste_entfallen(Quelle.ARCH)
    plotter.plot_liste_entfallen(Quelle.TECH)
    exit(0)


if __name__ == "__main__":
    main()
