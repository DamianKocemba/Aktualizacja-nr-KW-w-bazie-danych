# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 22:10:41 2022

@author: damian kocemba
"""
import re
import fdb

#OKRESLENIE PARMETROW
#parametry do polaczenia z baza danych
db_path = 'D:\\BAZA_KATASTER\\1202024.FDB'
host_name = 'localhost'
user_name = 'sysdba'
user_password = 'masterkey'

#sciezka do lokalizacji raportu z przenumerowania KW
path = 'D:\\BAZA_KATASTER\\'

#kod sadu wieczystoksiegowego
kod_sadu_wieczystoksiegowego = 'TR1B'
#numer obrebu w bazie danych (mozna wybrac ze slownika 'obreby')
obreb = 1

#czy wykonac update w bazie danych? - nalezy wpisac True lub False
czy_update_w_bazie_danych = False


#%%
# poloczenie z baza danych
con = fdb.connect( host=host_name, database=db_path, 
                  user=user_name, password=user_password)  
cursor = con.cursor()


# funkcja kontrolująca wprowadzany kod sądu
def kod_sadu(kod):
    if re.match('[A-Z]{2}[1-3]{1}[A-Z]{1}', kod):
        return True
    else:
        return False

#%%FUNKCJE POMOCNICZE DO EKSPOLARACJI BAZY DANYCH
# funkcja wyszukująca dostępne jednostki ewidencyjne w bazie danych
def dostepne_jednostki(cursor):
    sql_query = """ SELECT teryt, nzw
    FROM jedn_ewid
    """
    cursor.execute(sql_query)
    
    jedn_ewid = {}
    for j_ew in cursor.fetchall():
        jedn_ewid[j_ew[0]] = j_ew[1]
        
    return jedn_ewid

jedn_ewid = dostepne_jednostki(cursor)


# funkcja wyszukująca dostępne obręby w ramach wybranej jednostki ewidencyjnej
def dostepne_obreby(cursor, jednostka_ewidencyna):
    sql_query = """ SELECT id, naz
    FROM obreby WHERE teryt = '{0}'
    """.format(jednostka_ewidencyna)
    
    cursor.execute(sql_query)
    obreb_ewid = {}
    for o_ew in cursor.fetchall():
        obreb_ewid[o_ew[0]] = o_ew[1]
        
    return obreb_ewid

obreby = dostepne_obreby(cursor, '120202_4')


#%%funkcja zamieniajaca stary format ksiegi wieczystej na nowy format
def nowa_ksiega_wieczysta(nr_kw, kod_sadu):
    "stary format nr: 'KW 12345', dalej przetwarzany jest sam numer, bez przedrostka  'KW' "
    stary_nr = nr_kw.split()[1]
    if len(stary_nr) < 8:
        o = 8 - len(stary_nr)
        pelny_numer = ('0' * o) + stary_nr  
        
        szyfr = {'0':0,
             '1':1,
             '2':2,
             '3':3,
             '4':4,
             '5':5,
             '6':6,
             '7':7,
             '8':8,
             '9':9,
             'X':10,
             'A':11,
             'B':12,
             'C':13,
             'D':14,
             'E':15,
             'F':16,
             'G':17,
             'H':18,
             'I':19,
             'J':20,
             'K':21,
             'L':22,
             'M':23,
             'N':24,
             'O':25,
             'P':26,
             'R':27,
             'S':28,
             'T':29,
             'U':30,
             'W':31,
             'Y':32,
             'Z':33}
        
        suma =  1 * szyfr[kod_sadu[0]] + \
                3 * szyfr[kod_sadu[1]] + \
                7 * szyfr[kod_sadu[2]] + \
                1 * szyfr[kod_sadu[3]] + \
                3 * szyfr[pelny_numer[0]] + \
                7 * szyfr[pelny_numer[1]] + \
                1 * szyfr[pelny_numer[2]] + \
                3 * szyfr[pelny_numer[3]] + \
                7 * szyfr[pelny_numer[4]] + \
                1 * szyfr[pelny_numer[5]] + \
                3 * szyfr[pelny_numer[6]] + \
                7 * szyfr[pelny_numer[7]]

        cyfra_kontrolna = str(suma % 10)
        
        nkw = kod_sadu + '/' + pelny_numer + '/' + cyfra_kontrolna
    
        return nkw

#%%funkcja generująca raport z przenumerowania KW
def generuj_raport(line, path):
    with open(path+'raport_z_przenumerowania_KW.txt', 'a') as file:
        file.write(line + '\n')
        
#%%WLASCIWY PROGRAM
# zapytanie do bazy danych programu EWopis
sql_query = """SELECT 
            dok.syg AS NR_KW, 
            LIST((d.idobr || '-' || d.idd), ', ') AS DZIALKI 
            FROM dokumenty dok \
            INNER JOIN dokumenty_dzialki_rpwl AS rpwl ON rpwl.iddok=dok.id AND dok.kdk=5 
            LEFT JOIN dzialka AS d ON d.id=rpwl.iddz AND rpwl.status IN (0,1) 
            WHERE d.status in (0,1) AND d.idobr = {0} -- NALEZY PODAC NR OBREBU 
            GROUP BY dok.syg 
            ORDER BY dok.syg """.format(obreb)

cursor.execute(sql_query)

flag = kod_sadu(kod_sadu_wieczystoksiegowego)

for row in cursor.fetchall():
    if flag == False:
        print("-"*10+"Błędny kod sądu"+"-"*10)
        break
    print('\n',row)
    kw = row[0]
    dzialki = row[1]
    print('Pierwotny nr: ', kw)
    #Opcja 1: poprawny numer KW w bazie
    if re.match("^[A-Z]{2}[1-3]{1}[A-Z]{1}/[0-9]{8}/[0-9]{1}",kw):
        print("Numer jest wlasciwy: ", kw)
        line = kw + '\t' + dzialki + '\t Numer jest poprawny'
        generuj_raport(line, path)
    #Opcja 2: niepoprawny numer KW, podlegajacy poprawie
    elif re.match("KW [0-9]+", kw):
        nkw = nowa_ksiega_wieczysta(kw, kod_sadu_wieczystoksiegowego)
        #update KW w bazie danych !!!
        if czy_update_w_bazie_danych == True:
            sql_query_update = "UPDATE dokumenty SET syg = '{0}', syg_pelna = '{0}' where syg = '{1}'".format(nkw, kw)
            cursor.execute(sql_query_update)
        print('Nowa kw: ', nkw)
        line = kw + '\t' + dzialki + '\t Nowy nr: ' + nkw
        generuj_raport(line, path)
    #Opcja 3: błędny format numeru KW, który nalezy przeanalizowac ręcznie
    else:
        print("ZŁY FORMAT NUMERU KW")
        line = kw + '\t' + dzialki + '\t Zły format numeru KW'
        generuj_raport(line, path)

con.commit()
con.close()

print("\n"+"*"*10+" KONIEC DZIAŁANIA SKRYPTU "+"*"*10)















    