# Rejestr dokumentów projektu

| Identyfikator | Wersja | Autor | Data | Status |
|---|---|---|---|---|
| APT-DOC-010 | 1.0 | Kamil Wieckowski | 2026-10-25 | Zatwierdzony |

## Zasady kontroli dokumentów (wg ISO 10013)

1. **Identyfikacja.** Każdy dokument ma unikalny identyfikator `APT-DOC-NNN`, nadawany przy tworzeniu
   i nigdy nie używany ponownie.
2. **Metryka.** Na początku dokumentu jest tabela z identyfikatorem, wersją, autorem, datą i statusem.
3. **Wersjonowanie.** `MAJOR.MINOR`: drobne poprawki podnoszą MINOR, zmiana treści merytorycznej podnosi MAJOR.
4. **Historia zmian.** Na końcu dokumentu jest tabela: wersja, data, autor, opis zmiany.
5. **Statusy.** *Projekt* → *Do przeglądu* → *Zatwierdzony* → *Wycofany*.
6. **Przegląd i zatwierdzanie.** Zmiany w dokumentach przechodzą przez pull request z przeglądem.
   Historia w Git stanowi dodatkowy, niezmienialny zapis zmian.
7. **Przechowywanie.** Wersja obowiązująca to wersja na gałęzi `main`. Wcześniejsze wersje są dostępne w historii Git.
8. **Rejestr.** Ten dokument jest jedynym spisem wszystkich dokumentów projektu i aktualizuje się go przy każdej zmianie wersji.

## Wykaz dokumentów

| ID | Dokument | Plik | Wersja | Data | Autor | Status |
|---|---|---|---|---|---|---|
| APT-DOC-001 | README: opis projektu, dane, uruchomienie | [README.md](../README.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-002 | Zasady współtworzenia | [CONTRIBUTING.md](../CONTRIBUTING.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-003 | Kodeks postępowania | [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-004 | Rejestr zmian oprogramowania | [CHANGELOG.md](../CHANGELOG.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-010 | Rejestr dokumentów | [rejestr-dokumentow.md](rejestr-dokumentow.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-011 | Plan projektu | [plan-projektu.md](plan-projektu.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-012 | Dane i ich jakość | [dane.md](dane.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-013 | Architektura | [architektura.md](architektura.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-014 | Raport końcowy (ISO 21513) | [raport-koncowy.md](raport-koncowy.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |
| APT-DOC-015 | Lessons learned (PMI) | [lessons-learned.md](lessons-learned.md) | 1.0 | 2026-10-25 | Kamil Wieckowski | Zatwierdzony |

## Historia zmian dokumentu

| Wersja | Data | Autor | Opis |
|---|---|---|---|
| 1.0 | 2026-10-25 | Kamil Wieckowski | Pierwsza wersja |
