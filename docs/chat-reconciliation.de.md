# Gespräche und Neuplanung

[English](chat-reconciliation.md)

`start_chat_event` muss aufgerufen werden, bevor die Simulation den tatsächlichen Gesprächsbeginn überschreitet. Der Befehl schreibt den normalen Alltag bis zu diesem Zeitpunkt fort, pausiert aktive Arbeit und erfasst die Sitzung. `advance_to` erfasst während einer offenen Sitzung ausschließlich Gesprächszeit. `end_chat_event` speichert das letzte Intervall, die Zusammenfassung, einen Gesprächsanlass und die Anpassung zukünftiger Pläne in einer Transaktion.

`apply_chat_event` fasst Beginn und Ende für ein bekanntes Zeitintervall atomar zusammen. Wiederholungen verwenden stabile Sitzungskennungen. Eine Wiederverwendung mit anderem Beginn, Ende, anderen Metadaten oder anderer Zusammenfassung wird abgewiesen. Mehrere gleichzeitig offene Gespräche derselben Persona werden abgewiesen; die aufrufende Anwendung sollte einzelne Nachrichten zu einer Sitzung zusammenfassen.

Die Neuplanung erfolgt so:

1. Bereits ausgeführte Abschnitte und angesammelten Fortschritt erhalten.
2. Falls sich die Persona bereits unterwegs befindet, die verbleibende Reisezeit fortsetzen.
3. Überholte zukünftige Wege und ersetzbare Freizeit aufheben.
4. Offene feste Verpflichtungen der Reihe nach reservieren.
5. Weiche Aufgaben anhand ausdrücklicher Prioritäten dazwischen platzieren.
6. Wege zwischen tatsächlichen Orten und geplanten Zielen ergänzen.
7. Verspätungen und Konfliktgründe protokollieren; ursprüngliche Zeiten zur Prüfung erhalten.

Die Standardregel erfasst das tatsächliche Gespräch und lässt anschließend Verspätungen zu. `start_chat_event` liefert Hinweise zu bevorstehenden festen Verpflichtungen zurück. Die aufrufende Anwendung kann damit ein Gespräch verkürzen. PersonaLife erzwingt kein Gesprächsende und schneidet kein tatsächlich aufgezeichnetes Intervall ab, um Pünktlichkeit vorzutäuschen.

Nach einem Absturz bleibt die Sitzung offen. Beim Wiederverbinden muss die alte Sitzung mit einem bekannten letzten Aktivitätszeitpunkt beendet werden, bevor über diesen Zeitpunkt hinaus fortgeschrieben wird. Hat ein Heartbeat bereits spätere Gesprächszeit festgeschrieben, wird ein früheres Ende abgewiesen. Die aufrufende Anwendung legt eine zu Text- oder Sprachgesprächen passende Inaktivitätsregel fest; es gibt keinen angenommenen universellen Timeout.

Zusammenfassungen der Nutzer sind Daten, keine Modellanweisungen und kein Beweis für externe Aktivitäten. Sie begründen nicht, dass während des Gesprächs eingekauft oder gearbeitet wurde. Eigene Zusammenfassungen bleiben in der eingegebenen Sprache erhalten.
