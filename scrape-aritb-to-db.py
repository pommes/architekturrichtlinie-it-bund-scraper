import camelot
import sqlite3
import re
from enum import Enum
from pprint import pprint
from aritb_common import Quelle

tech_pdf = 'Desktop/architekturrichtlinie_it_bund_techn_spezif_2020.pdf'
# tech_pdf='Desktop/architekturrichtlinie_it_bund_techn_spezif_2019-anmerkungen-TIM.pdf'
tech_pages = '8-27'  # 8-27
tech_version = '20200731-1.0'
tech_jahr = 2020
arch_pdf = 'Desktop/architekturrichtlinie_it_bund_2020.pdf'
# arch_pdf='Desktop/architekturrichtlinie_it_bund_2019_anmerkungen-TIM.pdf'
arch_pages = '30-131'  # 30-131
arch_version = '20200731-1.0'
arch_jahr = 2020
database = r"architekturrichtlinie-it-bund.db"


class Richtlinie:
    def __init__(self, id, quelle, lebenszyklus):
        self.id = id
        self.quelle = quelle
        self.lebenszyklus = lebenszyklus

    def __repr__(self):
        return "Richtlinie(ID='{0}'".format(self.id)


class Spec(Richtlinie):
    def __init__(self, themenbereich, bezeichnung, id, verbindlichkeit, beschreibung, version, jahr, quelle,
                 lebenszyklus):
        self.themenbereich = themenbereich
        self.bezeichnung = bezeichnung
        self.verbindlichkeit = verbindlichkeit
        self.beschreibung = beschreibung
        self.version = version
        self.jahr = jahr
        super().__init__(id, quelle, lebenszyklus)

    def __repr__(self):
        return "Spec(ID='{}', QUELLE={}, LEBENSZYKLUS={}, THEMENBEREICH='{}, BEZEICHNUNG='{}', VERBINDLICHKEIT='{}', BESCHREIBUNG='{}', VERSION='{}', JAHR='{}'".format(
            self.id, self.quelle, self.lebenszyklus, self.themenbereich, self.bezeichnung, self.verbindlichkeit,
            self.beschreibung, self.version, self.jahr)


def parse_arch(arch_pdf, arch_pages, arch_version, arch_jahr):
    print("+++ Parse PDF '{0}' ...".format(arch_pdf))
    tables = camelot.read_pdf(arch_pdf, pages=arch_pages, line_scale=40)

    specs = []
    id_pattern = re.compile("^[A-Z]{2}-[0-9]{4}-[A-Z][0-9]+$")
    for table in tables:
        try:
            id = (table.df.values[1][0])[len('ID: '):]
            bezeichnung = ' '.join(table.df.values[0][0].split()).replace('\r', '').replace('\n', '')
            if id_pattern.match(id):
                themenbereich_bezeichnung = table.df.values[0][0].split("-", 1)

                specs.append(Spec(
                    themenbereich=themenbereich_bezeichnung[0],
                    bezeichnung=bezeichnung,
                    id=id,
                    verbindlichkeit=table.df.values[0][2],
                    beschreibung=table.df.values[2][1],
                    version=arch_version, jahr=arch_jahr, quelle=Quelle.ARCH.value, lebenszyklus="AKTIV")
                )
            else:
                print("WARN: Ungültige ID: '{0}', BEZEICHNUNG: '{1}'".format(id, bezeichnung))

        except IndexError as e:
            print("ERROR: {0}: {1}".format(e, table.df))
        # camelot.plot(table, kind='grid').show()

    # pprint(specs)
    print("Seite '{0}' von PDF gelesen. '{1}' Tabellen gefunden.".format(arch_pages, len(specs)))
    return specs


def parse_tech(tech_pdf, tech_pages, tech_version, tech_jahr):
    print("+++ Parse PDF '{0}' ...".format(tech_pdf))
    tables = camelot.read_pdf(tech_pdf, pages=tech_pages, line_scale=40)

    tech_specs = []
    for table in tables:
        try:
            themenbereich_bezeichnung = table.df.values[0][0].split("-", 1)
            bezeichnung = ' '.join(table.df.values[0][0].split()).replace('\r', '').replace('\n', '')
            tech_specs.append(Spec(
                themenbereich=themenbereich_bezeichnung[0],
                bezeichnung=bezeichnung,
                id=(table.df.values[1][0])[len('ID: '):],
                verbindlichkeit=table.df.values[0][1],
                beschreibung=table.df.values[2][0],
                version=tech_version, jahr=tech_jahr, quelle=Quelle.TECH.value, lebenszyklus="AKTIV")
            )
        except IndexError as e:
            print("ERROR: {0}: {1}".format(e, table.df))

    print("Seite '{0}' von PDF gelesen. '{1}' Tabellen gefunden.".format(tech_pages, len(tech_specs)))
    return tech_specs


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def add_richtlinie(conn, r: Richtlinie):
    sql = ''' INSERT INTO ar_richtlinie(richtlinie_id, quelle, lebenszyklus)
              VALUES(:id, :quelle, :lebenszyklus) '''
    cur = conn.cursor()
    cur.execute(sql, (r.id, r.quelle, r.lebenszyklus))
    conn.commit()
    return cur.lastrowid


def add_detail(conn, r: Spec):
    sql = ''' INSERT INTO ar_detail(richtlinie_id, themenbereich, bezeichnung, verbindlichkeit, beschreibung, version, jahr)
              VALUES(:id, :themenbereich, :bezeichnung, :verbindlichkeit, :beschreibung, :version, :jahr) '''
    cur = conn.cursor()
    cur.execute(sql, (r.id, r.themenbereich, r.bezeichnung, r.verbindlichkeit,
                      r.beschreibung, r.version, r.jahr))
    conn.commit()
    return cur.lastrowid


def update_detail(conn, r: Spec):
    sql = ''' UPDATE ar_detail
              SET  
              	themenbereich=:themenbereich,
                bezeichnung=:bezeichnung, 
                verbindlichkeit=:verbindlichkeit, 
                beschreibung=:beschreibung, 
                jahr=:jahr
              WHERE
                1=1
                and richtlinie_id=:id
                and version=:version '''
    params = {
        'id': r.id, 'themenbereich': r.themenbereich, 'bezeichnung': r.bezeichnung,
        'verbindlichkeit': r.verbindlichkeit,
        'beschreibung': r.beschreibung, 'version': r.version, 'jahr': r.jahr}
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    return cur.lastrowid


def update_detail_links(conn, version, quelle: Quelle):
    sql = ''' SELECT id, richtlinie_id, version FROM ar_detail WHERE version=? '''
    cur = conn.cursor()
    cur.execute(sql, (version,))
    rows = cur.fetchall()

    sql = ''' UPDATE ar_richtlinie SET detail_id_aktuell=:empty WHERE quelle=:quelle '''
    cur.execute(sql, (None, quelle.value))

    sql = ''' UPDATE ar_richtlinie SET detail_id_aktuell=:detail_id_aktuell WHERE richtlinie_id=:richtlinie_id AND lebenszyklus='AKTIV' AND quelle=:quelle '''
    rowcount = 0
    for row in rows:
        cur.execute(sql, (row[0], row[1], quelle.value))
        rowcount += cur.rowcount

    conn.commit()
    return rowcount


def main():
    # ... PARSE ...
    specs = []
    specs.extend(parse_arch(arch_pdf, arch_pages, arch_version, arch_jahr))
    specs.extend(parse_tech(tech_pdf, tech_pages, tech_version, tech_jahr))
    # pprint(specs)
    # exit(0)

    print("+++ Verbinde DB '{0}' ...".format(database))
    conn = create_connection(database)

    print("+++ Aktualisiere 'AR_RICHTLINIE' ...")
    rlnew = []
    for spec in specs:
        try:
            add_richtlinie(conn, spec)
            rlnew.append(spec.id)
        except sqlite3.IntegrityError:
            pass
        # print("Richtlinie mit ID '{0}' existiert bereits. Nichts zu tun.".format(spec.id))

    print("{0} neue Richtlinien hinzugefügt: {1}".format(len(rlnew), rlnew))

    print("+++ Aktualisiere 'AR_DETAIL' ...")
    dnew = []
    dupd = []
    for spec in specs:
        try:
            add_detail(conn, spec)
            dnew.append(spec.id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                try:
                    update_detail(conn, spec)
                    dupd.append(spec.id)
                except sqlite3.IntegrityError as e:
                    print("ERROR: {0}: {1}".format(e, spec))
            else:
                print("ERROR: {0}: {1}".format(e, spec))

    print("{0} neue Details hinzugefügt: {1}".format(len(dnew), dnew))
    print("{0} bestehende Details aktualisiert: {1}".format(len(dupd), dupd))

    print("+++ Aktualisiere Verknüpfungen 'AR_RICHTLINIE' ...")
    last_rowid = 0
    last_rowid += update_detail_links(conn, arch_version, Quelle.ARCH)
    last_rowid += update_detail_links(conn, tech_version, Quelle.TECH)
    print("{0} Details-Links an 'AR_RICHTLINIE' aktualisiert zu Details".format(last_rowid))


if __name__ == "__main__":
    main()
