
function send(data)
  tt.exec(data)
end

function echo(msg)
	tt.exec("#line ignore #show <fca>"..msg)
end

function echo2(msg)
  tt.set("echomsg",msg)
  tt.exec("#line ignore #show {$echomsg}")
end

function pecho(subj,msg)
    tt.exec("#line ignore #show <acf>"..subj.."<caf>: <afc>"..msg)
    --echo(subj..": "..msg)
end

function reagisci_turbine(direzione)
  sposta(getPosition(direzione))
end

function reagisci_raggio(direzione)
  gmcp = tt.get("gmcp")
  if gmcp.char.vitals.roomPos == getPosition(direzione) then
    if gmcp.char.vitals.roomPos == 5 then
      sposta(1)
    else
      sposta(5)
    end
  end
end

function reagisci_tremore(direzioneA, direzioneB)
  echo("\n--------------> SPOSTATI " .. getPosition(direzioneA) .. " O " .. getPosition(direzioneB) .. "!!!!!<--------------")
  if tremoreDir ~= nil and tremoreDir ~= 0 then
    if tremoreDir == 1 then
      sposta(getPosition(direzioneA))
    else
      sposta(getPosition(direzioneB))
    end
  end
end

function reagisci_aura()
  echo("\n--------------> CURA !!!!!<--------------")
end

function reagisci_R()
  send("stop")
end

function getPosition(direzione)
  if direzione == 'sud' then
    return 2
  elseif direzione == 'est' then
    return 6
  elseif direzione == 'nord' then
    return 8
  elseif direzione == 'ovest' then
    return 4
  elseif direzione == 'sud-ovest' then
    return 1
  elseif direzione == 'sud-est' then
    return 3
  elseif direzione == 'nord-est' then
    return 9
  elseif direzione == 'nord-ovest' then
    return 7
  elseif direzione == 'centro' then
    return 5
  end
end

function setUnionePosizione(dir)
  unioneDir = dir
end

function sposta(dir)
  gmcp = tt.get("gmcp")
  if tonumber(dir) ~= tonumber(gmcp.char.vitals.roomPos) then
    send("sposta " .. dir)
  end
end

function reagisci_unione()
  sposta(unioneDir or 9)
end

tt.exec("#action { sembra guardare verso il lato %1 della stanza.} {#lua exec reagisci_raggio(\"%1\")}")
tt.exec("#action { sembra guardare verso l'angolo %1 della stanza.} {#lua exec reagisci_raggio(\"%1\")}")
tt.exec("#action { sembra guardare verso il %1 della stanza.} {#lua exec reagisci_raggio(\"%1\")}")

tt.exec("#action { viene circondato da una potentissima aura d'assorbimento!} {#lua exec reagisci_aura()}")

tt.exec("#action {Per fortuna, il luogo d'origine non sembra essere stato colpito!} {#lua exec sposta(5)}")
tt.exec("#action {Sbattendo i piedi, riesci a placare il tremore prima che esploda!} {#lua exec sposta(5)}")
tt.exec("#action {Sbattendo i piedi, %1 riesce a placare il tremore prima che esploda!} {#lua exec sposta(5)}")

tt.exec("#action {%1, %2] dice 'R} {#lua exec reagisci_R()}")

tt.exec("#action { scaglia un lampo di energia pura verso l'angolo %1 della stanza} {#lua exec sposta(5)}")
tt.exec("#action { scaglia un lampo di energia pura verso il lato %1 della stanza} {#lua exec sposta(5)}")
tt.exec("#action { scaglia un lampo di energia pura verso il %1 della stanza.} {#lua exec sposta(5)}")

tt.exec("#action { crea un turbine di energia presso l'angolo %1 della stanza.} {#lua exec reagisci_turbine(\"%1\")}")
tt.exec("#action { crea un turbine di energia presso il lato %1 della stanza.} {#lua exec reagisci_turbine(\"%1\")}")
tt.exec("#action { crea un turbine di energia presso il %1 della stanza.} {#lua exec reagisci_turbine(\"%1\")}")

tt.exec("#action { ride sguaiatamente, mentre l'intera stanza inizia a tremare} {#lua exec reagisci_unione()}")

tt.exec("#action { un tremore scuote il lato %1 e l'angolo %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote il lato %1 e il lato %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote il %1 e l'angolo %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote il %1 e il lato %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote l'angolo %1 e l'angolo %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote l'angolo %1 e il lato %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote l'angolo %1 e il %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")
tt.exec("#action { un tremore scuote il lato %1 e il %2 della stanza} {#lua exec reagisci_tremore(\"%1\",\"%2\")}")

