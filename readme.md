## PL: Skrypt do aktualizacji formatu numeru Księgi Wieczystej w bazie danych

Skrypt aktualizuje stary format numeru Księgi Wieczystej na nowy 
(np. KW 12345 na TR1B/00012345/6). Dane są pobierane z bazy danych .fdb 
(baza do prowadzenia EGiB). Użytkownik określa, czy program ma dokonać
przenumerowania w bazie  danych (jeśli nie, to generowany jest sam raport
z przenumerowania).

Dodatkowe info
- Załączona baza zawiera przykładowe, wymyślone dane na potrzeby testów.
- Podane numery KW w przykładowym raporcie z programu (raport_z_przenumerowania_KW.txt)
  są częsciowo ukryte z uwagi na ochronę danych osobowych.

## ENG: Script for updates of land registration format number

Script allows to update an old format of land registration number to a new one
(e.g. KW 12345 to TR1B/00012345/6). Data are downloaded from fdb database. User has
two options: programm can change the format number to a new one or generate only the report
of the changing numbers.

Additional informations:
- attached database contains exemplary, imaginary data for tests needs
- KW numbers in exemplary report from the programm (raport_z_przenumerowania_KW.txt)
  are partly hidden because of personal data security
