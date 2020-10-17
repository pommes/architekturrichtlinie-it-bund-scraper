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
import sqlite3

database = r"/Users/tim/architekturrichtlinie-it-bund.db"


class Database:

    def __init__(self, db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print("ERROR: {}".format(e))

    def fetch_changes(self):
        sql = ''' select * from
                (
                    select RICHTLINIE_ID, QUELLE, 'AKTIV' TYP from AR_RICHTLINIE where LEBENSZYKLUS='AKTIV'
	                union
                    select RICHTLINIE_ID, QUELLE, 'NEU' TYP from [Aktuelle Änderungen] where beschreibung='neu'
                    union
                    select RICHTLINIE_ID, QUELLE, 'GEAENDERT' TYP from [Aktuelle Änderungen] where beschreibung not in ('entfallen', 'neu')
                    union
                    select RICHTLINIE_ID, QUELLE, 'ENTFALLEN' TYP from [Aktuelle Änderungen] where beschreibung='entfallen'
                )	
                order by TYP asc, RICHTLINIE_ID asc '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows


class Plotter:

    def plot_anzahl_aenderungen(self, changes_db):
        order = ['NEU', 'GEAENDERT', 'ENTFALLEN']
        changes = pd.DataFrame(changes_db, columns=['id', 'quelle', 'typ'])
        changes = changes[changes.typ.isin(['NEU', 'GEAENDERT', 'ENTFALLEN'])]

        g = changes.groupby(['typ', 'quelle']).size().to_frame('count').reset_index()
        from itertools import product
        combs = pd.DataFrame(list(product(changes['typ'].unique(), changes['quelle'].unique())),
                             columns=['typ', 'quelle'])
        result = g.merge(combs, how='right').fillna(0)
        # pprint(result)
        result = result.pivot(index='typ', columns='quelle', values='count').loc[order]
        result.columns.rename('Dokument', 1)
        result.columns = ['Architekturrichtlinie', 'Technische Spez.']
        result.index.rename('', 1)
        pprint(result)
        result.plot(kind='bar', legend=True, stacked=False, rot=0, color=tuple(['#2460A7FF', '#85B3D1FF']),
                    title='Anzahl geänderte Richtlinien je Dokument')
        plt.show()


db = Database(database)
db.fetch_changes()
changes_db = db.fetch_changes()

plotter = Plotter()
plotter.plot_anzahl_aenderungen(db.fetch_changes())
exit(0)

changes = pd.DataFrame(changes_db, columns=['id', 'quelle', 'typ'])
changes = changes[changes.typ.isin(['NEU', 'GEAENDERT', 'ENTFALLEN'])]
pprint(changes)
order = ['NEU', 'GEAENDERT', 'ENTFALLEN']
ch_plot = changes.groupby(['typ', 'quelle']).agg('count').loc[order]
#ch_plot.columns = ['id']

g = changes.groupby(['typ', 'quelle']).size().to_frame('count').reset_index()
from itertools import product
combs = pd.DataFrame(list(product(changes['typ'].unique(), changes['quelle'].unique())), columns=['typ', 'quelle'])
result = g.merge(combs, how = 'right').fillna(0)
#pprint(result)
result = result.pivot(index='typ', columns='quelle', values='count')
result.columns.rename('Dokument', 1)
result.columns = ['Architekturrichtlinie', 'Technische Spez.']
result.index.rename('', 1)
pprint(result)
result.plot(kind='bar', legend=True, stacked=True, rot=0, color=tuple(['#2460A7FF', '#85B3D1FF']), title='Anzahl der Änderungen')
plt.show()
exit(0)

pprint(ch_plot)
ch_plot.plot(kind='bar', legend=False, rot=0, color=tuple(['b', 'y', 'r']))
plt.show()

ch_count = changes.groupby('typ').agg('count').to_dict()
ch_list = list(ch_count.values())[0]
labels = ['NEU', 'GEÄNDERT', 'ENTFALLEN']
#pprint(ch_list)
#pprint(ch_list['NEU'])
#plt.bar(range(len(ch_list)), ch_list.values(), align='center')
plt.bar(0, ch_list['NEU'], tick_label=labels[0])
plt.bar(1, ch_list['GEAENDERT'], tick_label=labels[1])
plt.bar(2, ch_list['ENTFALLEN'], tick_label=labels[2])
plt.xticks(range(0, 3), labels)
plt.show()
exit(0)

plt.close('all')

ts = pd.Series(np.random.randn(1000),
               index=pd.date_range('1/1/2000', periods=1000))

ts = ts.cumsum()
ts.plot()
plt.show()

df = pd.DataFrame(np.random.randn(1000, 4),
                  index=ts.index, columns=list('ABCD'))
df = df.cumsum()
plt.figure()

df.plot()
plt.show()

df3 = pd.DataFrame(np.random.randn(1000, 2), columns=['B', 'C']).cumsum()
df3['A'] = pd.Series(list(range(len(df))))
df3.plot(x='A', y='B')
plt.show()

plt.figure()
df.iloc[5].plot.bar()
plt.axhline(0, color='k')
plt.show()
