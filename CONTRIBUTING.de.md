# Zu PersonaLife beitragen

[English](CONTRIBUTING.md)

Hilf dabei, dauerhafte KI-Charaktere konsistenter, nachvollziehbarer und leichter integrierbar zu machen.

## Hilfreiche Beiträge

- Ein reproduzierbarer Widerspruch im Tagesablauf mit Zeitstempeln, Zeitzone und kleinem fiktivem Profil.
- Tests für Unterbrechungen, Wege, Nachtschichten, Wiederholungen und Neustarts.
- Kleine Integrationsbeispiele für die öffentliche Python- oder HTTP-API.
- Installationsrückmeldungen zu Windows, Linux oder macOS.
- Verständliche Dokumentation, Sprachpflege und bessere Zugänglichkeit.

Vor größeren Änderungen bitte Architektur und Weiterentwicklungsplan lesen. Die Zeitberechnung bleibt deterministisch und modellunabhängig. Neue Prosa darf nicht still zu maßgeblicher Historie werden. Änderungen zukünftiger Pläne benötigen eine ausdrückliche Begründung; ausgeführter Fortschritt muss Unterbrechungen überstehen.

## Entwicklung

```sh
python -m venv .venv
# Umgebung aktivieren, anschließend:
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/three_days.py --language de --output demo-output-de
```

Der tatsächliche AiMemory-Integrationstest läuft, wenn das optionale Paket installiert ist; andernfalls wird er ausdrücklich übersprungen. Tests sollen keine bezahlten Anbieter oder privaten Konten benötigen.

Ein Pull Request sollte Problem, Verhaltensänderung und relevante Testergebnisse erklären. In Berichten nur fiktive Daten verwenden, keine API-Schlüssel, privaten Chats oder persönlichen Erinnerungsdatenbanken. Größere neue Abhängigkeiten und Architekturänderungen vor umfangreicher Arbeit besprechen. Es gibt keine zugesagte Antwortzeit oder Supportvereinbarung.

## Beide Sprachen pflegen

Änderungen an einer öffentlichen Markdown-Seite müssen auch in der zugehörigen Sprachfassung enthalten sein. Fachliche Bezeichner und Befehle bleiben unverändert. Eigene Oberflächentexte gehören in `personalife/i18n.py`. Der Sprachtest prüft Dokumentpaare, Verweise und Laufzeitverhalten.
