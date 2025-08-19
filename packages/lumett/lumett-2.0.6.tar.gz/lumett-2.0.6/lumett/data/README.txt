
LUMETT CLIENT PROJECT

A multi-platform mud client written with tintin++ scripts

Sistema per una client per mud scalabile e multipiattaforma.
Adattabile a qualsiasi mud.
La client e' scalcabile su sistemi diversi e dimensioni diverse.
Premessa: avere installato sul sistema tintin o una delle varianti 
(vedi wintin++) Linux o shell di comando linux esistono per tutti 
i sistemi operativi, vedi: WLS per windows, Termux per Android, 
Ish per IOS, Macchine virtuali varie.
Per tutte le informazioni del caso vedi il sito di 
  Tintin++ www.Mudhalla.com.

Su LINUX/IOS/ANDROID 
  - Installare uno dei seguenti terminali se non si e'
    su linux:

      - IOS ISH		https://ish.app
      - ANDROID TERMUX	https://termux.dev/en/)
      - ANDROID NATIVE LINUX TERMINAL (e' come linux)
      - WINDOWS MSYS2	https://www.msys2.org/docs/terminals/
      - WINDOWS WLS2	https://learn.microsoft.com/it-it/windows/wsl/install 
   
  - installare tintin++ https://tintin.mudhalla.net/install.php
  - posizionare i file scaricati dove fa comodo
  - accedere alla directory Lumett
  - digitare il comando sh lumett.sh
  - selezionare o creare il mud nel wizard.

Su WINDOWS  
  Si puo' avviare direttamente con i file .batch.
  Oppure è possibile utilizzare il sottositema linux
  WLS oppure msys2 (vedi linux) 
  
  - Scaricare il zip e decomprimere dove desiderato.
  - avviare lumett.bat
  - selezionare o creare il mud nel wizard.

 ---------------Release vers 2.0.4------------------------------
Bug fix vari.
Fix per un bug del login.
Nuova barra del personaggio con tabs.

---------------Release vers 2.0.3------------------------------
Bug fix vari.

---------------Release vers 2.0.2------------------------------
Bug fix vari.

---------------Release vers 2.0.1------------------------------
Bug fix vari.

---------------Release vers 2.0--------------------------------
Bug fix vari.
Menu cliccabili neil pannello laterale.
Aggiunta scheda Room nella sidebar.
La gui si puo' cambiare manualmente dal menu Gui.
Si puo' tornare al wizard delle connessioni con la voce Wizard.
Si puo' cambiare sessione con la voce sessione nella topbar.
La mappa finalmente sta diventando utile.
Cliccare su una stanza per a lungo mappa la stanza le adiacenti.
Funzione rsave per mappare la stanza corrente.
La gui viene salvata alla chiusura e ripresa all'apertura.

---------------Release vers 1.9--------------------------------
Bux fixese


---------------Release vers 1.8--------------------------------
Supporto per il mud Lumen et Umbra live e test.
Varie migliorie e bugfix

---------------Release vers 1.7--------------------------------
Aggiunto un selettore di avvio.
Aggiunto il supporto al nuovo leu oltre che al vecchio
E' possibile su desktop avviare la versione multi finestra
con l'ononimo comando lumettmulti.

---------------Release vers 1.6--------------------------------

Cambiate varie parti del codice e dei file, rimaneggiate 
varie directroy
Aggiunto in wizard delle connessioni

---------------Release vers 1.5.5 --------------------------------

Aggiornamenti sulla versione windows, ricopialto e aggiornato
con mingw64.
Introdotto il pannello della location dove mostra un'immagine
della stanza/zona.
Aggiornato su tutti i sitemi il protocollo gmcp ed eliminato msdp

---------------Release vers 1.5-----------------------------------

Connessione diretta e unica a leu.
Ora si crea solo i personaggi.
Possibilità di fare nuovi personaggi o
login diretto manuale.
Riorganizzazione del codice.
Nuovo sistema di caricamento dei moduli sulla riga di quello 
dello script tintin-helper 
https://github.com/perlsaiyan/tintin-helper.git
Nuovo sistema di login, solo a leu, inserire solo il pg

---------------Release vers 1.4-----------------------------------

Rimaneggiamento dei files..
La mappa viene salvata in /saves/map.dat.
Fa il suo ritorno la barra laterale destra.
L'interfaccia grafica scala in base alla dimensione della finestra.
Iniziale supporto a gmcp nell'ominmo file.
Ritocchi estetici all'interfaccia, aggiunta tab in alto per con 
nome del mud, del personaggio ed un link per chiudere la client.

---------------Release vers 1.3------------------------------------

Spostata la parte grafica in gui.tin.
Supporto a msldp e aggiunti alcui link cliccabili.
La lista degli alias si puo cliccare per richiamare l'alias.
Rimosso il file mnotd.tin e non viene piu mostrato all'avvio in quanto
sugli schermi piccoli fa confusione.

---------------Release vers 1.2-----------------------------------

Risolto bug di login ora si puo accedere anche solo con host e porta al mud
ma per usare tutte le funzionalità aggiungere il personaggio al login auto.
Risolto qualche bug.
Gestione semplificata dei alias e trigger, incantesimi e abilità alla fine
sono alias e si gestiscono da li.
Ora si possono aggiungere anche comandi complessi in mud con addalias 
e addtrigg la cui sintassi è:

        addalias nome_alias/comando|i_alias (utilizzabile %1 fino %99)
        Per piu comandi compessi editare saves/alias.dat con un text editor
        addtrig nome_trigger/comando|i_trigger (utilizzabile %1 fino %99)
        Per piu comandi compessi editare saves/alias.dat con un text editor

Eliminati i file Path.dat,Cast.dat.

---------------Release vers 1.1----------------------------------

Risolti alcuni bugs e rimosso il comando target (al momento in revisione).
Aggiunto il supporto al protocollo mxp.
Cliccare una stanza sulla mappa ti ci porta.
Comando travel: travel <direzione> seguira il percorso fino una diramazione
o vicolo cieco.
Alias, Paths, Triggers e Cast vengono gestiti attraverso liste nei files 
omonimi .dat Comandi addpaths,delpath,addalias,delalias,addcast,delcast
per gestirli in client.

---------------Release vers 1-----------------------------------

Per avviare il log usare il comando log on, per fermarlo log off

La finestra di comunicazione ed i dialoghi sono gestiti da comm_window.tt++

Alias, Incantesimi e Paths e triggers sono gestiti nell'ominmo file,
per aggiungerne basta editare le liste  dedicate nel file:
	lista_paths
	lista_cast
	lista_alias

Per ora i trigger sono svolti attraverso semplici #action

Per usare lo speedwalk inserici il punto e poi la stringa
	es: .ndw;run e

Comportamento di input stile zmud

Stats bar appena sopra la input bar e barra grafica

Mappa grafica, per ora piu scenica che funzionale

-----------------------------------------------------------------

TODO:
	sviluppare la mappa con salvataggi e caricamenti

------------------------------------------------------------------

Un ringraziamento per i suoi script ad:
	Igor van den Hoven - mudclient@gmail.com

Alla comunity di tintin++ 

Alla comunity di Lumen et Umbra, in particolare Nymiae,Xenon,Moylen,Oxon.

E alla ai vari autori di guide e manuali su Mudhalla.com

Ad mfontani per il suo progetto https://github.com/mfontani/tintin-dde
