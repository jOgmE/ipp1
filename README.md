### Implementační dokumentace k 1. úloze do IPP 2019/2020  
### Jméno a příjmení: Norbert Pócs  
### Login: xpocsn00  
  
## Vypracovanie projektu
Projekt je rozdelený na dve časti: načítanie vstupu a jeho kontrola a vytvorenie xml súboru. Na prvú časť bola použitý
modulárny prístup a ku generovaniu výstupného súboru xml objektovo orientovaný prístup.

### Načítanie vstupu a jeho kontrola
Na načítanie vstupu používam funkciu `load_line()`, vracia načíaný riadok, alebo EOF keď sa narazý na koniec súboru.
V tejto funkcii sa robí aj odmazanie komentárov, rozdelenie do pola a kontrola správnosti prvého riadku - hlavičky súboru.
Môže sa stať, že na jednom riadku je len komentár bez užitočného kódu, vtedy sa funkcia volá rekurzívne sám seba, s čím sa
načíta ďalší riadok.  
Na kontrolu lexikálnej a syntaxnej správnosti používam funkciu `parse()`. Funkcia rozdelí príkazy trojadresného kódu podľa
počtu potrebných operátorov a skontroluje ich syntaxnú správnosť. Ak príkaz je správny, vytvoria sa k inštrukcii patriace riadky v xml. Pomocné funkcie sú: `check_label_name(), check_type(), check_variable_name(), check_symbol_name(), check_literal()` ktoré kontrolujú syntaxnú správnosť operátorov inštrukcie pomocou regulárnych výrazov.

### XML
Objektum drží buffer pre súbor xml, do ktorého sa ukladajú samostatné inštrukcie riadok po riadku. Ďalej obsahuje funkcie pre
zjednodušenie pridávaní inštrukcií, argumentov alebo hlavičky súboru.  
  
Na konci je hlavná časť programu, kde sa spúšťa kontrola argumentov, načítanie riadkov a posielanie na kontrolu do `parse()`,
ukončenie xml súboru a nakoniec výpis celého výstupného súboru na stdout.
