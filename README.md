# Metin

Aplicație desktop: adaugi un nume, apoi scrii pe pagina acelui nume. Textele se salvează automat în
`%APPDATA%\Metin\note.json` (rămân acolo și la update sau dezinstalare).

## Rulare din cod

```
python Metin.pyw
```

## Installer

```
powershell -ExecutionPolicy Bypass -File build.ps1
```

Rezultă `dist\MetinSetup.exe`. Îl rulezi pe orice calculator cu Windows; nu cere drepturi de administrator.

## Cum publici un update

1. Faci modificările în `Metin.pyw`.
2. Mărești `APP_VERSION` (de ex. `1.0.0` → `1.0.1`).
3. Rulezi `build.ps1`.
4. Publici installer-ul pe GitHub:
   ```
   gh release create v1.0.1 dist\MetinSetup.exe --title "Metin 1.0.1" --notes "Ce s-a schimbat"
   ```

La următoarea pornire, aplicația instalată pe orice dispozitiv vede versiunea nouă, afișează
„Versiune nouă disponibilă” și, la click pe **Actualizează**, se actualizează și repornește singură.
