# Einführung in Windows-Container mit Docker

Dieses Kapitel behandelt die Grundlagen der Nutzung von Windows-Containern mit Docker.

## Windows-Container ausführen

Zieh zuerst ein Docker-Image, das du verwenden kannst, um einen Windows-Container auszuführen:

```powershell
docker image pull mcr.microsoft.com/windows/nanoserver:1809
```

Dadurch wird das Nano Server Docker-Image von Microsoft in Ihre Umgebung heruntergeladen. Dieses Image ist ein minimales Windows-Server-Betriebssystem, das als Docker-Container ausgeführt wird. Du kannst es als Basis für deine eigenen Apps nutzen oder Container direkt davon ausführen.

Versuchen Sie einen einfachen Container, indem Sie einen Befehl übergeben, damit der Container ausgeführt wird:

```powershell
PS> docker container run mcr.microsoft.com/windows/nanoserver:1809 hostname
a33758b2dbea
```

Dieser führt einen neuen Container aus dem Windows Nano Server Image aus und fordert ihn auf, den `hostname`-Befehl auszuführen. Die Ausgabe ist der Maschinenname des Containers, der tatsächlich eine zufällig von Docker gesetzte ID ist. Wiederhole den Befehl und du siehst jedes Mal einen anderen Host-Namen.

## Windows-Container-Images erstellen und pushen

Du paketierst deine eigenen Apps in Docker, indem du ein Docker-Image baust. Du teilst die App, indem du das Image in eine Registry pushst – das kann eine öffentliche Registry wie Docker Hub sein oder eine private Registry in deiner eigenen Umgebung wie Docker Trusted Registry. Jeder, der Zugriff auf dein Image hat, kann es abrufen und Container ausführen – genau wie du es mit Microsofts öffentlichem Windows Nano Server-Image gemacht hast.

Das Übertragen von Bildern auf Docker Hub erfordert eine kostenlose Docker-ID. Das Speichern von Images auf Docker Hub ist eine großartige Möglichkeit, Anwendungen zu teilen oder Build-Pipelines zu erstellen, die Apps von der Entwicklung in die Produktion mit Docker übertragen.

### Docker-ID einrichten

Registrieren Sie sich für ein Konto und speichern Sie dann Ihre Docker-ID in einer Variable in Ihrer PowerShell-Sitzung. Wir werden es im Rest des Labors verwenden:

```powershell
$dockerId = '<your-docker-id>'
```

**Hinweis:** Verwenden Sie hier unbedingt Ihre eigene Docker-ID. Zum Beispiel, wenn Ihre Docker-ID `sixeyed` ist, lautet der Befehl: `$dockerId = 'sixeyed'`

### Dockerfile erstellen

Docker-Images werden mit dem Befehl `docker image build` erstellt, wobei ein einfaches Skript namens Dockerfile verwendet wird. Die Dockerfile beschreibt die vollständige Bereitstellung Ihrer Anwendung und all ihrer Abhängigkeiten.

Man kann mit PowerShell eine sehr einfache Dockerfile generieren:

```powershell
'FROM mcr.microsoft.com/windows/nanoserver:1809' | Set-Content Dockerfile
'CMD echo Hello World!' | Add-Content Dockerfile
```

### Image bauen

Und jetzt führe `docker image build` aus, wobei das Bild ein Tag bekommt, das es mit deiner Docker-ID identifiziert:

```powershell
docker image build --tag $dockerId/hello-world .
```

Führe einen Container aus dem Image aus, und du wirst sehen, dass er einfach die Instruktion aus der `CMD`-Zeile ausführt:

```powershell
> docker container run $dockerId/hello-world
Hello World!
```

### Image auf Docker Hub pushen

Jetzt hast du ein Docker-Image für eine einfache Hello World-App. Das Image ist die tragbare Einheit – du kannst das Image auf Docker Hub übertragen, und jeder kann es herunterladen und deine App selbst ausführen. Führe zuerst `docker login` durch, um dich beim Register zu authentifizieren. Dann schieben Sie das Bild:

```powershell
docker login
docker image push $dockerId/hello-world
```

Images, die auf Docker Hub gespeichert sind, sind in der Weboberfläche verfügbar, und öffentliche Bilder können von anderen Docker-Nutzern abgerufen werden.

## Nächste Schritte

Fahren Sie mit **Schritt 3: Multi-Container-Anwendungen** fort, um zu sehen, wie man eine Webanwendung baut und betreibt, die eine ASP.NET Core-Webanwendung und eine SQL-Server-Datenbank verwendet – alle mit Docker-Windows-Containern.

---

## Zusammenfassung

In diesem Leitfaden haben Sie gelernt:

- ✅ Windows-Container-Images von Microsoft Container Registry herunterladen
- ✅ Einfache Windows-Container ausführen
- ✅ Dockerfiles für Windows-Anwendungen erstellen
- ✅ Docker-Images bauen und taggen
- ✅ Images zu Docker Hub pushen
- ✅ Container aus eigenen Images ausführen

## Weiterführende Ressourcen

- [Docker Hub](https://hub.docker.com/)
- [Microsoft Container Registry](https://mcr.microsoft.com/)
- [Windows Container Documentation](https://docs.microsoft.com/en-us/virtualization/windowscontainers/)
- [Docker Documentation](https://docs.docker.com/)
