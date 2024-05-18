┌──(kali㉿kali)-[~]  
└─$ checksec editor  
[*] '/home/kali/editor'  
    Arch:     amd64-64-little  
    RELRO:    Full RELRO  
    Stack:    Canary found  
    NX:       NX enabled  
    PIE:      PIE enabled  

Z tohto nám vyplýva, že možnosti je málo. Treba sa zamerať na niečo konkétne.


Po dôkladnej statickej analýze som prišiel na to, že aplikácia odomňa pýta príkazy. Pokiaľ som neprihlásený, jediné príkazy, ktoré vezme sú login a exit. exit ukončí aplikáciu, login umožní prihlásiť sa menom a heslom guest:guest
Po prihlásení je možné zadať ďalšie príkazy a to get a put, pričom za nimi očakáva argument s názvom súboru.

Prvá zraniteľnosť bola v debug_msg() funkcii, kde nebol zadaný format specifier, čo nám umožní leaknuť pointre a rovnako stringy na pointeroch. Pre nás zaujímavý pointer bol "\%9\$p", ktorý nás nazmeroval na adresu v stacku, blízko samotne adresy, ktorú nám printlo a "\%8\$p", ktorý nás nasmeroval na adresu v heape s offsetom +0x720 (heap base je teda pointer - 0x720). Adresy sme si printli pomocou príkazu "get debug.log"

└─$ nc 127.0.0.1 2222  
Enter commands (type 'exit' to quit):  
\> \%9\$p  
\> \%8\$p  
\> login  
username> guest  
password> guest  
\# get debug.log   
get: debug.log  
\====================  
Unknown method or argument:0x7fffffffdd60 (stack)  
Unknown method or argument:0x55555555a720 (heap)
Success  
  
\====================  

Ďalší postreh bol, že funcia get si alohuje v heape 48 bajtov pre zápis názvu súboru, ktorý číta, ale na adresu+40 (bajty 41-48) zapíše adresu, na ktorú funckia strncat zapíše obsah súboru. Názov súboru ale mohol byť dlhý až 70 bajtov (69 + null terminator, takže len 69). Funkcia put nám umožní zapísať do súboru 20 bajtov.

Exploit teda spočíval v tom, že blízko adresy v stacku, ktorú sme printli z debug.log zapíšeme adresu z heapu, kde sa nám načítal súbor z vlajkou...  
>_Poznámka: vlajku nedokážeme vyčítať priamo, pretože pokiaľ riadok obsahu súboru obsahuje substring SK-CERT, funckia get tento riadok neprintne._

Ja osobne som si vlajku do pamäte načítal 4x, ale nie je to potrebné. Len sa bál, že po free pamäte sa nieco prepíše.

Zistil som však, po zadaní "get debug.log" a následne 4x "get flag.txt" sa mi obsahy vlajky uložili na heapbase +0x9E0, +0xEB0, +0x1300 a +0x1730. (pri debugu)

keže na týchto adresách obsah vlajky začínal štandardne SK-CERT, potrebujem vynechať aspoň jedno písmenko, takže pointer + 0x1 (heapbase+0x1731).  
Tento pointer zapíšeme na stack, ktorý si dokážeme vypísať, a pomocou format specifiera \%_n_\$s, keďže stack sa posúva, je potrebné nájsť _n_, to však môžeme iteráciou.

Pomocou put 40x"A" + adresa_stacku-0x20_napr vytvoríme súbor,
keď klient vypýta   
text\> zadáme adresu heapu, kde máme vlajku + jeden bajt (heap base + 0x1731)
pomocou get 40xA + adresa_stacku-0x20 prepíšeme adresu, kam sa zapíše obsah súboru (musí existovať ten súbor, preto ten put najskôr) a do toho stacku tak zapíšeme pointer, kde je obsah vlajky bez prvého znaku

Následne len použiť ako príkať \%_n_\$s (iterovať napríklad 21-30 pre n) a nakoniec použiť "get debug.log" a máme tam vlajku bez prvého S

Vlajka:  
#### SK-CERT{d1ff1cult_h34p_0w3rfl0w}