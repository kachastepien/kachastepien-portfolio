# kachastepien.com

Portfolio Katarzyny Stępień. Cała strona to jeden plik: `index.html`.

## Co jest w folderze

- `index.html` – strona (tekst, style, zdjęcia, wszystko w jednym pliku)
- `CNAME` – mówi GitHub Pages, że strona ma działać pod `kachastepien.com`
- `.nojekyll` – wyłącza przetwarzanie Jekyll na GitHubie, strona idzie 1:1

## Publikacja (GitHub Pages)

1. Otwórz ten folder w VS Code.
2. **Source Control** (ikona gałązki) → **Initialize Repository** → wpisz opis, np. `portfolio` → **Commit**.
3. **Publish to GitHub** → wybierz **public**.
4. Na github.com w repozytorium: **Settings → Pages**
   - Source: **Deploy from a branch**, branch **main**, folder **/ (root)** → **Save**
   - Custom domain powinno się uzupełnić samo z pliku `CNAME` (`kachastepien.com`). Jeśli nie, wpisz i zapisz.
5. W **home.pl** w ustawieniach DNS domeny dodaj:

   | Typ   | Host  | Wartość                  |
   |-------|-------|--------------------------|
   | A     | @     | 185.199.108.153          |
   | A     | @     | 185.199.109.153          |
   | A     | @     | 185.199.110.153          |
   | A     | @     | 185.199.111.153          |
   | CNAME | www   | kachastepien.github.io   |

   Usuń stare, domyślne rekordy A / CNAME dla `@` i `www`, jeśli home.pl jakieś dodał.
6. Poczekaj (od kilkunastu minut do doby), potem w **Settings → Pages** zaznacz **Enforce HTTPS**.

## Zmiany na stronie

Edytujesz `index.html` → **Commit** → **Sync / Push**. Po minucie zmiana jest online.

Podgląd lokalnie: otwórz `index.html` w przeglądarce (dwuklik) albo użyj rozszerzenia **Live Server** w VS Code.
