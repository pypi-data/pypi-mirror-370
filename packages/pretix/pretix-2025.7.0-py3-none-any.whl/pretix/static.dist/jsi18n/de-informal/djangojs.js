

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n != 1;
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "(one more date)": [
      "(ein weiterer Termin)",
      "({num} weitere Termine)"
    ],
    "=": "=",
    "Add condition": "Bedingung hinzuf\u00fcgen",
    "Additional information required": "Zus\u00e4tzliche Informationen ben\u00f6tigt",
    "All": "Alle",
    "All of the conditions below (AND)": "Alle der folgenden Bedingungen (UND)",
    "An error has occurred.": "Ein Fehler ist aufgetreten.",
    "An error of type {code} occurred.": "Ein Fehler vom Typ {code} ist aufgetreten.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "Freigabe ausstehend",
    "April": "April",
    "At least one of the conditions below (OR)": "Mindestens eine der folgenden Bedingungen (ODER)",
    "August": "August",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "QR-Code-Bereich",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Berechne Standardpreis\u2026",
    "Cancel": "Abbrechen",
    "Canceled": "storniert",
    "Cart expired": "Warenkorb abgelaufen",
    "Check-in QR": "Check-in-QR-Code",
    "Checked-in Tickets": "Eingecheckte Tickets",
    "Click to close": "Klicken zum Schlie\u00dfen",
    "Close message": "Schlie\u00dfen",
    "Comment:": "Kommentar:",
    "Confirmed": "Best\u00e4tigt",
    "Confirming your payment \u2026": "Zahlung wird best\u00e4tigt \u2026",
    "Contacting Stripe \u2026": "Kontaktiere Stripe \u2026",
    "Contacting your bank \u2026": "Kontaktiere deine Bank \u2026",
    "Continue": "Fortfahren",
    "Copied!": "Kopiert!",
    "Count": "Anzahl",
    "Credit Card": "Kreditkarte",
    "Current date and time": "Aktueller Zeitpunkt",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Aktueller Wochentag (1 = Montag, 7 = Sonntag)",
    "Current entry status": "Aktueller Zutrittsstatus",
    "Currently inside": "Derzeit anwesend",
    "December": "Dezember",
    "Do you really want to leave the editor without saving your changes?": "M\u00f6chtest du den Editor wirklich schlie\u00dfen ohne Ihre \u00c4nderungen zu speichern?",
    "Do you want to renew the reservation period?": "M\u00f6chtest du die Reservierung verl\u00e4ngern?",
    "Duplicate": "Duplizieren",
    "Enter page number between 1 and %(max)s.": "Gib eine Seitenzahl zwischen 1 und %(max)s ein.",
    "Entry": "Eingang",
    "Entry not allowed": "Eingang nicht erlaubt",
    "Error while uploading your PDF file, please try again.": "Es gab ein Problem beim Hochladen der PDF-Datei, bitte erneut versuchen.",
    "Event admission": "Einlass",
    "Event end": "Veranstaltungsende",
    "Event start": "Veranstaltungsbeginn",
    "Exit": "Ausgang",
    "Exit recorded": "Ausgang gespeichert",
    "February": "Februar",
    "Fr": "Fr",
    "Friday": "Freitag",
    "Gate": "Station",
    "Generating messages \u2026": "Generiere Nachrichten\u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Gruppe von Objekten",
    "If this takes longer than a few minutes, please contact us.": "Wenn dies l\u00e4nger als einige Minuten dauert, kontaktieren Sie uns bitte.",
    "Image area": "Bildbereich",
    "Information required": "Infos ben\u00f6tigt",
    "Invalid page number.": "Ung\u00fcltige Seitenzahl.",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Januar",
    "July": "Juli",
    "June": "Juni",
    "Load more": "Mehr laden",
    "March": "M\u00e4rz",
    "Marked as paid": "Als bezahlt markiert",
    "Maxima": "Maxima",
    "May": "Mai",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minuten seit erstem Zutritt (-1 bei erstem Zutritt)",
    "Minutes since last entry (-1 on first entry)": "Minuten seit vorherigem Zutritt (-1 beim erstem Zutritt)",
    "Mo": "Mo",
    "Monday": "Montag",
    "MyBank": "MyBank",
    "No": "Nein",
    "No active check-in lists found.": "Keine aktive Check-In Liste gefunden.",
    "No results": "Keine Ergebnisse",
    "No tickets found": "Keine Tickets gefunden",
    "None": "Keine",
    "November": "November",
    "Number of days with a previous entry": "Anzahl an Tagen mit vorherigem Eintritt",
    "Number of days with a previous entry before": "Anzahl an Tagen mit vorherigem Eintritt vor",
    "Number of days with a previous entry since": "Anzahl an Tagen mit vorherigem Eintritt seit",
    "Number of previous entries": "Anzahl bisheriger Eintritte",
    "Number of previous entries before": "Anzahl bisheriger Eintritte vor",
    "Number of previous entries since": "Anzahl bisheriger Eintritte seit",
    "Number of previous entries since midnight": "Anzahl bisheriger Eintritte seit Mitternacht",
    "OXXO": "OXXO",
    "Object": "Objekt",
    "October": "Oktober",
    "Order canceled": "Bestellung storniert",
    "Order not approved": "Bestellung nicht freigegeben",
    "Others": "Sonstige",
    "Paid orders": "Bezahlte Bestellungen",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Kredit",
    "PayPal Pay Later": "PayPal Sp\u00e4ter Zahlen",
    "PayU": "PayU",
    "Payment method unavailable": "Zahlungsmethode nicht verf\u00fcgbar",
    "Placed orders": "Get\u00e4tigte Bestellungen",
    "Please enter the amount the organizer can keep.": "Bitte gib den Betrag ein, den der Veranstalter einbehalten darf.",
    "Powered by pretix": "Event-Ticketshop von pretix",
    "Press Ctrl-C to copy!": "Dr\u00fccke Strg+C zum kopieren!",
    "Product": "Produkt",
    "Product variation": "Variante",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Eingel\u00f6st",
    "Renew reservation": "Reservierung verl\u00e4ngern",
    "Result": "Ergebnis",
    "SEPA Direct Debit": "SEPA-Lastschrift",
    "SOFORT": "SOFORT",
    "Sa": "Sa",
    "Saturday": "Samstag",
    "Saving failed.": "Speichern fehlgeschlagen.",
    "Scan a ticket or search and press return\u2026": "Ticket scannen oder suchen und mit Enter best\u00e4tigen\u2026",
    "Search query": "Suchbegriff",
    "Search results": "Suchergebnisse",
    "Select a check-in list": "W\u00e4hle eine Check-In Liste",
    "Selected only": "Nur ausgew\u00e4hlte",
    "September": "September",
    "Su": "So",
    "Sunday": "Sonntag",
    "Switch check-in list": "Check-In Liste wechseln",
    "Switch direction": "Richtung wechseln",
    "Text box": "Textbox",
    "Text object (deprecated)": "Text-Objekt (veraltet)",
    "Th": "Do",
    "The PDF background file could not be loaded for the following reason:": "Die Hintergrund-PDF-Datei konnte nicht geladen werden:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they're available.": "Die Produkte in deinem Warenkorb sind nicht mehr f\u00fcr dich reserviert. Du kannst die Bestellung trotzdem abschlie\u00dfen, solange die Produkte noch verf\u00fcgbar sind.",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Die Produkte in deinem Warenkorb sind nicht mehr f\u00fcr dich reserviert. Du kannst die Bestellung trotzdem abschlie\u00dfen, solange die Produkte noch verf\u00fcgbar sind.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Die Produkte in deinem Warenkorb sind noch eine Minute f\u00fcr dich reserviert.",
      "Die Produkte in deinem Warenkorb sind noch {num} Minuten f\u00fcr dich reserviert."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Der Veranstalter beh\u00e4lt %(currency)s %(amount)s ein",
    "The request took too long. Please try again.": "Diese Anfrage hat zu lange gedauert. Bitte erneut versuchen.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Dieses Ticket ist noch nicht bezahlt. M\u00f6chtest du dennoch fortfahren?",
    "This ticket requires special attention": "Dieses Ticket ben\u00f6tigt besondere Aufmerksamkeit",
    "Thursday": "Donnerstag",
    "Ticket already used": "Ticket bereits eingel\u00f6st",
    "Ticket blocked": "Ticket gesperrt",
    "Ticket code is ambiguous on list": "Ticket-Code ist nicht eindeutig auf der Liste",
    "Ticket code revoked/changed": "Ticket-Code gesperrt/ge\u00e4ndert",
    "Ticket design": "Ticket-Design",
    "Ticket not paid": "Ticket nicht bezahlt",
    "Ticket not valid at this time": "Ticket aktuell nicht g\u00fcltig",
    "Ticket type not allowed here": "Ticketart hier nicht erlaubt",
    "Tolerance (minutes)": "Toleranz (Minuten)",
    "Total": "Gesamt",
    "Total revenue": "Gesamtumsatz",
    "Trustly": "Trustly",
    "Tu": "Di",
    "Tuesday": "Dienstag",
    "Unknown error.": "Unbekannter Fehler.",
    "Unknown ticket": "Unbekanntes Ticket",
    "Unpaid": "Unbezahlt",
    "Use a different name internally": "Intern einen anderen Namen verwenden",
    "Valid": "G\u00fcltig",
    "Valid Tickets": "G\u00fcltige Tickets",
    "Valid ticket": "G\u00fcltiges Ticket",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Mi",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Deine Anfrage wird an den Server gesendet. Wenn dies l\u00e4nger als eine Minute dauert, pr\u00fcfe bitte deine Internetverbindung. Danach kannst du diese Seite neu laden und es erneut versuchen.",
    "We are processing your request \u2026": "Wir verarbeiten deine Anfrage \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Wir k\u00f6nnen den Server aktuell nicht erreichen, versuchen es aber weiter. Letzter Fehlercode: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Wir k\u00f6nnen den Server aktuell nicht erreichen. Bitte versuche es noch einmal. Fehlercode: {code}",
    "WeChat Pay": "WeChat Pay",
    "Wednesday": "Mittwoch",
    "Yes": "Ja",
    "You get %(currency)s %(amount)s back": "Du erh\u00e4ltst %(currency)s %(amount)s zur\u00fcck",
    "You have unsaved changes!": "Du hast ungespeicherte \u00c4nderungen!",
    "Your cart has expired.": "Dein Warenkorb ist abgelaufen.",
    "Your cart is about to expire.": "Dein Warenkorb l\u00e4uft gleich ab.",
    "Your color has decent contrast and is sufficient for minimum accessibility requirements.": "Diese Farbe hat einen ausreichenden Kontrast und gen\u00fcgt den Mindestanforderungen der Barrierefreiheit.",
    "Your color has great contrast and will provide excellent accessibility.": "Diese Farbe hat einen sehr guten Kontrast und tr\u00e4gt zur Barrierefreiheit bei!",
    "Your color has insufficient contrast to white. Accessibility of your site will be impacted.": "Diese Farbe hat keinen ausreichenden Kontrast zu wei\u00df. Die Barrierefreiheit der Seite ist eingeschr\u00e4nkt.",
    "Your local time:": "Deine lokale Zeit:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Deine Anfrage ist auf dem Server angekommen, aber wurde dort noch nicht verarbeitet. Wenn dies l\u00e4nger als zwei Minuten dauert, kontaktiere uns bitte oder gehe in deinem Browser einen Schritt zur\u00fcck und versuche es erneut.",
    "Your request has been queued on the server and will soon be processed.": "Deine Anfrage befindet sich beim Server in der Warteschlange und wird bald verarbeitet.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Deine Anfrage wird nun verarbeitet. Je nach Gr\u00f6\u00dfe der Veranstaltung kann dies einige Minuten dauern.",
    "Zimpler": "Zimpler",
    "close": "schlie\u00dfen",
    "custom date and time": "Fester Zeitpunkt",
    "custom time": "Feste Uhrzeit",
    "entry_status\u0004absent": "abwesend",
    "entry_status\u0004present": "anwesend",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "ist nach",
    "is before": "ist vor",
    "is one of": "ist eines von",
    "minutes": "Minuten",
    "required": "erforderlich",
    "widget\u0004Back": "Zur\u00fcck",
    "widget\u0004Buy": "In den Warenkorb",
    "widget\u0004Checkout": "Buchung",
    "widget\u0004Choose a different date": "Anderen Termin ausw\u00e4hlen",
    "widget\u0004Choose a different event": "Andere Veranstaltung ausw\u00e4hlen",
    "widget\u0004Close": "Schlie\u00dfen",
    "widget\u0004Close checkout": "Kauf schlie\u00dfen",
    "widget\u0004Close ticket shop": "Ticketshop schlie\u00dfen",
    "widget\u0004Continue": "Fortfahren",
    "widget\u0004Currently not available": "Aktuell nicht verf\u00fcgbar",
    "widget\u0004Decrease quantity": "Menge reduzieren",
    "widget\u0004FREE": "GRATIS",
    "widget\u0004Filter": "Filtern",
    "widget\u0004Filter events by": "Veranstaltungen filtern nach",
    "widget\u0004Hide variants": "Varianten verstecken",
    "widget\u0004Image of %s": "Bild von %s",
    "widget\u0004Increase quantity": "Menge erh\u00f6hen",
    "widget\u0004Load more": "Mehr laden",
    "widget\u0004New price: %s": "Neuer Preis: %s",
    "widget\u0004Next month": "N\u00e4chster Monat",
    "widget\u0004Next week": "N\u00e4chste Woche",
    "widget\u0004Not available anymore": "Nicht mehr verf\u00fcgbar",
    "widget\u0004Not yet available": "Noch nicht verf\u00fcgbar",
    "widget\u0004Only available with a voucher": "Nur mit Gutschein verf\u00fcgbar",
    "widget\u0004Open seat selection": "Sitzplan \u00f6ffnen",
    "widget\u0004Open ticket shop": "Ticketshop \u00f6ffnen",
    "widget\u0004Original price: %s": "Originalpreis: %s",
    "widget\u0004Previous month": "Vorheriger Monat",
    "widget\u0004Previous week": "Vorherige Woche",
    "widget\u0004Price": "Preis",
    "widget\u0004Quantity": "Menge",
    "widget\u0004Redeem": "Einl\u00f6sen",
    "widget\u0004Redeem a voucher": "Gutschein einl\u00f6sen",
    "widget\u0004Register": "Anmelden",
    "widget\u0004Reserved": "Reserviert",
    "widget\u0004Resume checkout": "Kauf fortsetzen",
    "widget\u0004Select": "Ausw\u00e4hlen",
    "widget\u0004Select %s": "%s ausw\u00e4hlen",
    "widget\u0004Select variant %s": "Variante %s ausw\u00e4hlen",
    "widget\u0004Show variants": "Varianten zeigen",
    "widget\u0004Sold out": "Ausverkauft",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Manche oder alle Ticketkategorien sind derzeit ausverkauft. Wenn du m\u00f6chtest, kannst du dich in die Warteliste eintragen. Wir benachrichtigen dich dann, wenn die gew\u00fcnschten Pl\u00e4tze wieder verf\u00fcgbar sind.",
    "widget\u0004The cart could not be created. Please try again later": "Der Warenkorb konnte nicht erstellt werden. Bitte erneut versuchen.",
    "widget\u0004The ticket shop could not be loaded.": "Der Ticketshop konnte nicht geladen werden.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Es sind derzeit sehr viele Benutzer in diesem Ticketshop. Bitte \u00f6ffne diesen Ticketshop in einem neuen Tab um fortzufahren.",
    "widget\u0004Voucher code": "Gutscheincode",
    "widget\u0004Waiting list": "Warteliste",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Wir konnten deinen Warenkorb nicht erstellen, da derzeit zu viele Nutzer in diesem Ticketshop sind. Bitte klicke \"Weiter\" um es in einem neuen Tab erneut zu versuchen.",
    "widget\u0004You cannot cancel this operation. Please wait for loading to finish.": "Du kannst diese Aktion nicht abbrechen. Bitte warte, bis der Ladevorgang abgeschlossen ist.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Du hast einen aktiven Warenkorb f\u00fcr diese Veranstaltung. Wenn du mehr Produkte ausw\u00e4hlst, werden diese zu deinem Warenkorb hinzugef\u00fcgt.",
    "widget\u0004currently available: %s": "aktuell verf\u00fcgbar: %s",
    "widget\u0004from %(currency)s %(price)s": "ab %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "inkl. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "inkl. Steuern",
    "widget\u0004minimum amount to order: %s": "minimale Bestellmenge: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "zzgl. %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "zzgl. Steuern"
  };
  for (const key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      const value = django.catalog[msgid];
      if (typeof value === 'undefined') {
        return msgid;
      } else {
        return (typeof value === 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      const value = django.catalog[singular];
      if (typeof value === 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      let value = django.gettext(context + '\x04' + msgid);
      if (value.includes('\x04')) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      let value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.includes('\x04')) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "j. F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. F Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y H:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      const value = django.formats[format_type];
      if (typeof value === 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }
};

