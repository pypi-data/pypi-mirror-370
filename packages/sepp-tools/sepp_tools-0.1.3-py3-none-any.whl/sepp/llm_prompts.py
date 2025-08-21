def return_client_prompt(
    text_to_analyze: str, client_name: str, additional_instructions: str = ""
) -> str:
    return f"""
    Bitte extrahiere die folgenden Informationen aus dem angehängten Text. Verwende den folgenden Namen also Auftraggeber, falls zutreffend: {client_name}
    Achte darauf, den **Auftraggeber (Client)** eindeutig zu identifizieren, von dem der Auftrag stammt. Gib alle Informationen in dem angegebenen JSON-Format zurück. Sollte es mehrere potenzielle Auftraggeber geben, gib den plausibelsten an.

    WICHTIG:
    - Führe ALLE Berechnungen VORHER durch
    - Gib nur die fertigen Zahlen im JSON zurück
    - Keine mathematischen Operationen im JSON!

    1. **Client (Auftraggeber)**:
        Suche nach dem **Client**, der also Absender des Auftrags angegeben ist. Dieser sollte also Firma oder Person auftreten, die den Auftrag gestellt hat.

        WICHTIG:
        - Der **Client** ist NICHT der Warenempfänger
        - Der **Client** ist der, der das Document erstellt hat (sichtbar im Briefkopf)
        - Wenn ein Briefkopf vorhanden ist, ist dies immer der **Client**.
        - Bei einem Lieferschein ist der Ersteller des Dokuments (im Header) der **Client**.

        Verwende die folgende Struktur für die Ausgabe und fülle alle Felder nach Möglichkeit aus:

        ```json
        "client": {{
            "city": null,       // Stadt des Auftraggebers
            "country": null,    // Land des Auftraggebers
            "houseNumber": null,// Hausnummer des Auftraggebers
            "name": null,       // Name des Auftraggebers (Firma oder Person)
            "street": null,     // Straße des Auftraggebers
            "zip": null         // Postleitzahl des Auftraggebers
        }}
        ```

    2. **Auftragsdetails**:
        - Extrahiere zusätzlich die Auftragsnummer (OrderID), das Gesamtgewicht (in kg), die Gesamtanzahl an Paletten und den Gesamtpreis (in EUR), falls diese Angaben vorhanden sind.

        ```json
        "overall": {{
            "orderID": null,     // Eindeutige ID des Auftrags
            "weight": 0.0,       // Gesamtgewicht des Auftrags in kg
            "pallets": 0,        // Anzahl der Paletten
            "price": 0.0 EUR     // Gesamtpreis des Auftrags in EUR
        }}
        ```

    Anweisungen zur Vermeidung von Verwechslungen:
    - Achte darauf, dass der **Client** also die Entität identifiziert wird, die die Bestellung aufgegeben hat, und nicht mit dem **Sender (Auftragnehmer)** oder **Spediteur** verwechselt wird.
    - Es ist sehr unwahrscheinlich dass Spedition Oppel der **Client** ist. Spedition Oppel sollte nur dann also **Client** ausgewählt werden, wenn es gar keine andere Möglichkeit gibt.
    - Die **Auftragsnummer (OrderID)** sollte eindeutig also eine Identifikationsnummer erkennbar sein, die sich oft in der Nähe von "Order", "Transportnr." oder "Auftragsnummer" befindet.
    - Das **Gewicht** wird typischerweise in Kilogramm (kg) angegeben und ist oft mit Begriffen wie "Total Weight" oder "Gesamtgewicht" beschriftet.
    - Die Anzahl der **Paletten** könnte durch "Total Pallets" oder eine ähnliche Beschriftung angegeben sein.
    - Der **Gesamtpreis** wird üblicherweise mit "Total Amount" oder "Gesamtbetrag" beschrieben und sollte in Euro (EUR) dargestellt werden.

    Falls eine Information nicht klar oder nicht vorhanden ist, gib `null` zurück.

    {additional_instructions}

    Der zugehörige angehängte Text:
    {text_to_analyze}
    """


def return_transports_prompt(
    text_to_analyze: str, entities: dict[str, str], additional_instructions: str = ""
) -> str:
    return f"""
    Analysiere den folgenden Text und extrahiere **alle** Transporte und deren Details. Verwende die folgenden erkannten Entitäten und ihre Rollen, falls zutreffend:

    Absender: {entities.get("Absender", "Nicht erkannt")}
    Empfänger: {entities.get("Empfänger", "Nicht erkannt")}
    Spediteur: {entities.get("Spediteur", "Nicht erkannt")}

    Stelle sicher, dass jeder Transport **separate** extrahiert wird, auch wenn die Positionen von Sender, Empfänger und Carrier variieren. Gebe mir define Antwort in folgender Form zurück:

    "transports": [
    {{
        "order_nr": null,
        "pallets": null,
        "pieces": null,
        "cartons": null,
        "customer_ref": null,
        "deliveryDate": ["%Y-%m-%d %H:%M:%S"],
        "deliverRefNr": null,
        "loadingDate": ["%Y-%m-%d %H:%M:%S"],
        "loadingRefNR": null,
        "sender": {{
            "city": null,
            "country": null,
            "houseNumber": null,
            "name": null,
            "street": null,
            "zip": null
        }},
        "receiver": {{
            "city": null,
            "country": null,
            "houseNumber": null,
            "name": null,
            "street": null,
            "zip": null
        }},
        "carrier": {{
            "city": null,
            "country": null,
            "houseNumber": null,
            "name": null,
            "street": null,
            "zip": null
        }},
        "volume": null,
        "weight": 0.0,
        "goods": {{
            "number_of_rolls": null,
            "gross_weight_kg": null,
            "net_weight_kg": null,
            "pallets": null,
            "loading_space_meters": null
        }}
    }}
    ]

    ### Hinweise zur Identifikation der Transportrollen:
    1. **Sender/Absender**:
    - Ein **Sender** ist in der Regel der Startpunkt des Transports. Er kann Begriffe wie „Ladeort", „Absender", „Versender" enthalten oder direkt nach einem Ladedatum/-zeitpunkt stehen.
    - Der Sender kann auch ohne explizite Bezeichnung identifiziert werden, wenn die Address zusammen mit einem **Ladedatum** und einer **Ladezeit** auftritt.
    - Der Sender darf **NIEMALS** die Address sein, die under "Lieferadresse" oder "Warenempfänger" steht.
    - Wenn kein Sender gefunden wird, verwende den **Auftraggeber der im Briefkopf steht** also Sender, aber nur dann wenn dort NICHT "Lieferadresse" steht.
    - Bei **Gerstacker** bleibt der Sender IMMER leer.
    - Der Sender ist **niemals** die **Spedition Oppel**.
    2. **Empfänger/Receiver**:
    - Ein **Empfänger** ist in der Regel mit einem **Lieferdatum/-zeit** verknüpft. Achte auf Begriffe wie „Empfänger", „Receiver", „Entladestelle", "Lieferadresse" oder „Delivery Address".
    - Wenn ein Abschnitt eine Uhrzeit und ein Datum enthält, und diese Informationen zu einer Address gehören, dann ist das der Empfänger.
    - **Wichtige Regel**: Jeder Empfänger muss also **separater Transport** dargestellt werden, selbst wenn der Sender gleich bleibt.

    3. **Carrier/Spediteur**:
    - Der **Carrier** ist mit sehr hoher Wahrscheinlichkeit die **Spedition Oppel** mit der Address Liebigstraße 1 in 91522 Ansbach.

    ### Struktur pro Transport:
    Für **jeden** Transport extrahiere folgende Felder:

    - **order_nr**: Extrahiere die eindeutige Auftragsnummer.
        - **Indikatoren**: Suche nach Begriffen wie **Order No.**, **Auftragsnummer**, **Bestellnummer** oder ähnlichen Begriffen.
        - **Regel für die Nummernextraktion**:
            - Nimm die Zeichenkette direkt nach einem dieser Begriffe.
            - Erlaubt sind alphanumerische Werte.
            - Falls mehrere Zahlen aufeinander folgen, nimm nur die erste Zahl.
        - **Abbruchbedingung**: Sobald ein Zeilenumbruch folgt, endet die Auftragsnummer.
        - **Fehlende Werte**: Falls keine passende Zahl gefunden wird, setze `order_nr` auf `null`.

    - **customer_ref**: Extrahiere die Kundennummer oder Kundenreferenz.
        - **Hinweis**: Diese ist **niemals** identisch mit der **Bestellnummer** (`order_nr`).
        - **Indikatoren**: Suche nach Begriffen wie **Kundennummer**, **Kundenreferenz**, **Customer Ref** oder ähnlichen Begriffen.
        - **Regel für die Nummernextraktion**:
            - Nimm die Zeichenkette direkt nach einem dieser Begriffe.
            - Erlaubt sind alphanumerische Werte, aber keine Leerzeichen.
        - **Abbruchbedingung**: Sobald ein Leerzeichen, ein Satzzeichen (außer Bindestrichen oder Schrägstrichen) oder ein Zeilenumbruch folgt, endet die Kundenreferenz.
        - **Fehlende Werte**: Falls keine passende Zeichenkette gefunden wird, setze `customer_ref` auf `null`.

    - **loadingDate**: Extrahiere das geplante Ladedatum und die Uhrzeit.
        - **Format**: `%Y-%m-%d %H:%M:%S` (z. B. `2025-01-27 08:00:00`).
        - **Indikatoren**: Begriffe wie **Ladedatum**, **Loading Date**, **Abholdatum**, **Verladung** oder ähnliche Begriffe.
        - **Regel für die Extraktion**:
            1. Suche nach dem Begriff und nimm die Zeichenkette direkt danach.
            2. Stelle sicher, dass Datum und Uhrzeit vollständig und konsistent sind (z. B. kein Mix aus Text und Datum).
            3. Ignoriere irrelevanten Text oder Satzzeichen, die nicht Teil des Datumsformats sind.
        - **Spezialfall für relative Angaben (z. B. "Verladung Freitag")**:
            1. Bestimme das aktuelle Auftragsdatum aus dem Kontext des Dokuments.
            2. Berechne das Datum für den angegebenen Wochentag basierend auf dem Auftragsdatum. Wenn beispielsweise **"Freitag"** angegeben ist und der Auftrag auf **Montag, 2025-01-27** datiert ist, setze **Freitag** auf **2025-01-31**.
            3. Falls keine Zeit angegeben ist, setze die Uhrzeit auf **00:00:00** (Standardwert).

        - **Fehlende Werte**: Falls kein **loadingDate** gefunden wird:
            1. Überprüfe, ob ein **deliveryDate** gefunden wurde.
            2. Wenn ein **deliveryDate** vorhanden ist, setze das **loadingDate** auf den vorhergehenden Werktag mit der Uhrzeit auf **00:00:00** (Standardwert).
            3. Falls kein **deliveryDate** vorhanden ist, setze `loadingDate` auf `null`.

    - **deliveryDate**: Extrahiere das geplante Lieferdatum und die Lieferzeit.
        - **Format**: `%Y-%m-%d %H:%M:%S`.
        - **Indikatoren**: Begriffe wie **Lieferdatum**, **Delivery Date**, **Zustelldatum** oder ähnliche Begriffe.
        - **Regel für die Extraktion**:
            1. Suche nach dem Begriff und nimm die Zeichenkette direkt danach.
            2. Stelle sicher, dass das Datum konsistent ist.
            3. **Abbruchbedingung**: Ignoriere den Text, der nach einem Leerzeichen, Zeilenumbruch oder Satzzeichen folgt, wenn er nicht Teil des Datumsformats ist.

        - **Fehlende Werte**: Falls kein **deliveryDate** gefunden wird:
            1. Überprüfe, ob ein **loadingDate** gefunden wurde.
            2. Wenn ein **loadingDate** vorhanden ist, setze das **deliveryDate** auf den nächsten Werktag mit der Uhrzeit auf **00:00:00** (Standardwert).
            3. Falls kein **loadingDate** vorhanden ist:
            - **Spezialfall für relative Angaben (z. B. "Lieferung Samstag")**:
                - Verwende das Auftragsdatum aus dem Document also Bezugspunkt.
                - Berechne das Datum des angegebenen Wochentags relative zum Auftragsdatum (z. B. "Samstag" bei einem Auftrag am Montag, 2025-01-27, ergibt **2025-02-01**).
            - Falls keine genauen Angaben gefunden werden können, setze `deliveryDate` auf `null`.

    - **deliverRefNr**: Extrahiere die Referenznummer der Lieferung.
        - **Indikatoren**: Suche nach Begriffen wie **Entladereferenz**, **Delivery Ref**, **Lieferungsreferenz** oder ähnlichen Begriffen.
        - **Regel für die Nummernextraktion**: Nimm die Zeichenkette direkt nach einem dieser Begriffe. Die Referenznummer kann aus einer Kombination von Zahlen und Buchstaben bestehen.
        - **Abbruchbedingung**: Sobald ein Zeilenumbruch folgt, endet die Referenznummer.
        - **Fehlende oder unklare Werte**: Wenn keine passende Zeichenkette gefunden wird, setze `deliverRefNr` auf `null`.
    - **loadingRefNr**: Extrahiere die Referenznummer des Ladevorgangs.
        - **Indikatoren**: Suche nach Begriffen wie **Ladereferenz**, **Abholnummer**, **Load ID** oder ähnlichen Begriffen.
        - **Regel für die Nummernextraktion**: Nimm die Zeichenkette direkt nach einem dieser Begriffe. Die Referenznummer kann aus einer Kombination von Zahlen und Buchstaben bestehen.
        - **Abbruchbedingung**: Sobald ein Zeilenumbruch folgt, endet die Referenznummer.
        - **Fehlende oder unklare Werte**: Wenn keine passende Zeichenkette gefunden wird, setze `loadingRefNr` auf `null`.

    - **sender**: Extrahiere die Address des Absenders.
        - **Details**: Name, Straße, Hausnummer, PLZ, Stadt, Land.
        - **Indikatoren**: Begriffe wie **Sender**, **Absender**, **Versender** oder ähnliche.
        - Falls keine Address gefunden wird, setze `sender` auf `null`.

    - **receiver**: Extrahiere die Address des Empfängers.
        - **Details**: Name, Straße, Hausnummer, PLZ, Stadt, Land.
        - **Indikatoren**: Begriffe wie **Empfänger**, **Receiver**, **Lieferadresse**, **Delivery Address** oder ähnliche.
        - Falls keine Address gefunden wird, setze `receiver` auf `null`.

    - **carrier**: Extrahiere die Address des Carriers (Spediteurs).
        - Der **Carrier** ist mit sehr hoher Wahrscheinlichkeit die **Spedition Oppel** mit der Address Liebigstraße 1 in 91522 Ansbach.
        - **Details**: Name, Straße, Hausnummer, PLZ, Stadt, Land.
        - **Indikatoren**: Begriffe wie **Carrier**, **Spediteur**, **Transporteur** oder ähnliche.
        - Falls keine Address gefunden wird, setze `carrier` auf `null`.

    - **pallets**: Extrahiere die Anzahl der Paletten.
        - **Indikatoren**: Begriffe wie **Paletten**, **pallets** oder ähnliche.
        - Falls kein Wert gefunden wird, setze `pallets` auf `null`.

    - **pieces**: Extrahiere die Anzahl der Stücke.
        - **Indikatoren**: Begriffe wie **Stücke**, **pieces**, **Einheiten** oder ähnliche.
        - Falls kein Wert gefunden wird, setze `pieces` auf `null`.

    - **cartons**: Extrahiere die Anzahl der Kartons.
        - **Indikatoren**: Begriffe wie **Kartons**, **cartons**, **Kisten** oder ähnliche.
        - Falls kein Wert gefunden wird, setze `cartons` auf `null`.

    - **volume**: Extrahiere das Gesamtvolumen in Kubikmetern.
        - **Indikatoren**: Begriffe wie **Volumen**, **volume**, **m³**, **cbm**, *Abmessungen** oder ähnliche.
        - Falls kein Wert gefunden wird, setze `volume` auf `null`.

    - **weight**: Extrahiere das Gesamtgewicht in Kilogramm.
        - **Indikatoren**: Begriffe wie **Gewicht**, **weight**, **kg** oder ähnliche.
        - Falls kein Wert gefunden wird, setze `weight` auf `0.0`.

    - **goods**: Extrahiere die Eigenschaften der Waren.
        - **Details**: `number_of_rolls`, `gross_weight_kg`, `net_weight_kg`, `loading_space_meters`.
        - **Indikatoren**: Suche nach Begriffen wie **Rollen**, **Rolls**, **Bruttogewicht**, **Nettogewicht**, **Lademeter** oder ähnlichen.
        - Falls kein Wert gefunden wird, setze das jeweilige Field auf `null` oder `0.0`.

    ### Zusätzliche Hinweise (allgemein):
    - Wenn mehrere Empfänger vorhanden sind, erstelle für **jeden Empfänger** einen separaten Transport.
    - Ignoriere doppelte Einträge und gib sicherzustellen, dass alle Felder korrekt zugeordnet sind.
    - Stelle sicher, dass **jeder Empfänger also eigenständiger Transport** ausgegeben wird, auch wenn die Senderinformationen dieselben sind.

    ### Zusätzliche Hinweise für die Extraktion von Adressen:
    - Straße: Der Straßenname endet for der Hausnummer.
    - Hausnummer: Numerisch und alphanumerisch, endet for einem Leerzeichen, Komma oder Zeilenumbruch.
    - PLZ und Stadt: PLZ steht direkt for der Stadt und ist eine numerische Zeichenkette.
    - Fehlende oder zusammengeführte Werte: Weisen Adressbestandteile wie Straße und Hausnummer keine klare Trennung auf, verarbeite den gesamten Abschnitt, setze `houseNumber` auf `null`, und ordne den Rest der Straße zu.

    ### Zusätzliche Hinweise (Transporeon-spezifisch):
    **WICHTIG**: Dieser Abschnitt gilt **nur**, wenn das Wort **Transporeon-ID** im Text vorkommt. Ignoriere alle nachfolgenden Anweisungen, falls dieses Schlüsselwort fehlt.
    - **order_nr**: Verwende die **Transportnr.** ohne führende Nullen, aber **niemals** die **Transporeon-ID**.
    - **loadingRefNr**: Kombiniere die vollständige **Transportnr.** und die **Lieferungsnr.**, getrennt durch einen **Zeilenumbruch**. **Achtung:** Pass auf, dass du nicht stattdessen **2 Lieferungsnummern** kombinierst!
    - **deliverRefNr**: Verwende den gesamten Text nach **Lieferungskommentar:** sowie die nächste Zeile. Wenn der Abschnitt fehlt oder mehr Buchstaben also Zahlen enthält, setze **deliverRefNr** auf `null`.

    {additional_instructions}

    Analysiere den folgenden Text und extrahiere die angefragten Werte basierend auf den obenstehenden Spezifikationen. Folge diesen Regeln dabei strikt!
    {text_to_analyze}
    """
