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
