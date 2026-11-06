# Organizare Metin

Aplicație desktop: adaugi un nume, apoi scrii pe pagina acelui nume. Textele se salvează automat în
`%APPDATA%\Metin\note.json` (rămân acolo și la update sau dezinstalare).

## Rulare din cod

```
python "Organizare Metin.pyw"
```

## Installer

```
powershell -ExecutionPolicy Bypass -File build.ps1
```

Rezultă `dist\OrganizareMetinSetup.exe`. Îl rulezi pe orice calculator cu Windows; nu cere drepturi de administrator.

## Cum publici un update

1. Faci modificările în `Organizare Metin.pyw`.
2. Mărești `APP_VERSION` (de ex. `1.0.0` → `1.0.1`).
3. Rulezi `build.ps1`.
4. Publici installer-ul pe GitHub:
   ```
   gh release create v1.0.1 dist\OrganizareMetinSetup.exe --title "Organizare Metin 1.0.1" --notes "Ce s-a schimbat"
   ```

La pornire, aplicația instalată pe orice dispozitiv descarcă în fundal versiunea nouă și afișează discret
jos „Versiunea X e pregătită · se instalează când închizi aplicația”. La închidere salvează tot textul,
face o copie de siguranță (`%APPDATA%\Metin\note.backup.json`) și abia apoi instalează update-ul,
fără nicio fereastră. Data viitoare când o deschizi, rulează versiunea nouă.

Aplicațiile care au încă versiunea 1.0.0 afișează în schimb bara „Versiune nouă disponibilă” cu butonul
**Actualizează** (o singură dată, pentru a trece la sistemul nou).
