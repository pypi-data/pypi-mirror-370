

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
      "(\u00e9\u00e9n andere datum)",
      "({num} andere datums)"
    ],
    "=": "=",
    "Add condition": "Voorwaarde toevoegen",
    "Additional information required": "Extra informatie nodig",
    "All": "Alle",
    "All of the conditions below (AND)": "Alle volgende voorwaarden (EN)",
    "An error has occurred.": "Er is iets misgegaan.",
    "An error of type {code} occurred.": "Er is een fout opgetreden met code {code}.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "Goedkeuring in afwachting",
    "April": "April",
    "At least one of the conditions below (OR)": "Ten minste \u00e9\u00e9n van de volgende voorwaarden (OF)",
    "August": "Augustus",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "Barcodegebied",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Standaardprijs berekenen\u2026",
    "Cancel": "Annuleren",
    "Canceled": "Geannuleerd",
    "Cart expired": "Winkelwagen is verlopen",
    "Check-in QR": "QR-code voor check-in",
    "Checked-in Tickets": "Ingecheckte kaartjes",
    "Click to close": "Klik om te sluiten",
    "Close message": "Sluit bericht",
    "Comment:": "Opmerking:",
    "Confirmed": "Bevestigd",
    "Confirming your payment \u2026": "Betaling bevestigen \u2026",
    "Contacting Stripe \u2026": "Verbinding maken met Stripe \u2026",
    "Contacting your bank \u2026": "Verbinding maken met je bank \u2026",
    "Continue": "Doorgaan",
    "Copied!": "Gekopieerd!",
    "Count": "Aantal",
    "Credit Card": "Kredietkaart",
    "Current date and time": "Huidige datum en tijd",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Huidige dag van de week (1 = Maandag, 7 = Zondag)",
    "Current entry status": "Huidige toegangstatus",
    "Currently inside": "Op dit moment binnen",
    "December": "December",
    "Do you really want to leave the editor without saving your changes?": "Wil je de editor verlaten zonder je wijzigingen op te slaan?",
    "Do you want to renew the reservation period?": "Wilt u de reservererings periode vernieuwen?",
    "Duplicate": "duplicaat",
    "Enter page number between 1 and %(max)s.": "voer een pagina nummer tussen 1 en %(max)s in.",
    "Entry": "Binnenkomst",
    "Entry not allowed": "Binnenkomst niet toegestaan",
    "Error while uploading your PDF file, please try again.": "Probleem bij het uploaden van het PDF-bestand, probeer het opnieuw.",
    "Event admission": "Toegangstijd evenement",
    "Event end": "Einde van het evenement",
    "Event start": "Start van het evenement",
    "Exit": "Vertrek",
    "Exit recorded": "Vertrek opgeslagen",
    "February": "Februari",
    "Fr": "Vr",
    "Friday": "Vrijdag",
    "Gate": "Ingang",
    "Generating messages \u2026": "Bezig met het genereren van berichten \u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Groep van objecten",
    "If this takes longer than a few minutes, please contact us.": "Als dit langer dan een paar minuten duurt, neem dan alstublieft contact met ons op.",
    "Image area": "Afbeeldingsgebied",
    "Information required": "Informatie nodig",
    "Invalid page number.": "Ongeldig pagina nummer.",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Januari",
    "July": "Juli",
    "June": "Juni",
    "Load more": "Meer laden",
    "March": "Maart",
    "Marked as paid": "Gemarkeerd als betaald",
    "Maxima": "Maxima",
    "May": "Mei",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minuten sinds de eerste toegang (-1 bij eerste toegang)",
    "Minutes since last entry (-1 on first entry)": "Minuten sinds laatste toegang (-1 bij eerste toegang)",
    "Mo": "Ma",
    "Monday": "Maandag",
    "MyBank": "MyBank",
    "No": "Nee",
    "No active check-in lists found.": "Geen actieve inchecklijsten gevonden.",
    "No results": "Geen resultaten",
    "No tickets found": "Geen kaartjes gevonden",
    "None": "Geen",
    "November": "November",
    "Number of days with a previous entry": "Aantal dagen met een eerdere binnenkomst",
    "Number of days with a previous entry before": "Aantal dagen met een eerdere binnenkomst voor",
    "Number of days with a previous entry since": "Aantal dagen met een eerdere binnenkomst sinds",
    "Number of previous entries": "Aantal eerdere binnenkomsten",
    "Number of previous entries before": "Aantal eerdere binnenkomsten voor",
    "Number of previous entries since": "Aantal eerdere binnenkomsten sinds",
    "Number of previous entries since midnight": "Aantal eerdere binnenkomsten sinds middernacht",
    "OXXO": "OXXO",
    "Object": "Object",
    "October": "Oktober",
    "Order canceled": "Bestelling geannuleerd",
    "Order not approved": "Bestelling niet goedgekeurd",
    "Others": "Andere",
    "Paid orders": "Betaalde bestellingen",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal-krediet",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "Betaalmethode niet beschikbaar",
    "Placed orders": "Geplaatste bestellingen",
    "Please enter the amount the organizer can keep.": "Voer het bedrag in dat de organisator mag houden.",
    "Powered by pretix": "Mogelijk gemaakt door pretix",
    "Press Ctrl-C to copy!": "Gebruik Ctrl-C om te kopi\u00ebren!",
    "Product": "Product",
    "Product variation": "Productvariant",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Gebruikt",
    "Renew reservation": "Vernieuw reservering",
    "Result": "Resultaat",
    "SEPA Direct Debit": "SEPA Automatische Incasso",
    "SOFORT": "SOFORT",
    "Sa": "Za",
    "Saturday": "Zaterdag",
    "Saving failed.": "Opslaan mislukt.",
    "Scan a ticket or search and press return\u2026": "Scan een kaartje of voer een zoekterm in en druk op Enter\u2026",
    "Search query": "Zoekopdracht",
    "Search results": "Zoekresultaten",
    "Select a check-in list": "Kies een inchecklijst",
    "Selected only": "Alleen geselecteerde",
    "September": "September",
    "Su": "Zo",
    "Sunday": "Zondag",
    "Switch check-in list": "Andere inchecklijst kiezen",
    "Switch direction": "Richting veranderen",
    "Text box": "Tekstkader",
    "Text object (deprecated)": "Tekstobject (verouderd)",
    "Th": "Do",
    "The PDF background file could not be loaded for the following reason:": "Het PDF-achtergrondbestand kon niet geladen worden om de volgende reden:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they're available.": "De items in uw winkelwagen zijn niet meer voor u gereserveerd. U kunt uw bestelling nog afronden, zolang de producten nog beschikbaar zijn.",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "De items in uw winkelwagen zijn niet meer voor u gereserveerd. U kunt uw bestelling nog afronden, zolang de producten nog beschikbaar zijn.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "De items in uw winkelwagen zijn nog \u00e9\u00e9n minuut voor u gereserveerd.",
      "De items in uw winkelwagen zijn nog {num} minuten voor u gereserveerd."
    ],
    "The organizer keeps %(currency)s %(amount)s": "De organisator houdt %(currency)s %(amount)s",
    "The request took too long. Please try again.": "De aanvraag duurde te lang, probeer het alsjeblieft opnieuw.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Dit kaartje is nog niet betaald. Wil je toch doorgaan?",
    "This ticket requires special attention": "Dit kaartje heeft speciale aandacht nodig",
    "Thursday": "Donderdag",
    "Ticket already used": "Kaartje al gebruikt",
    "Ticket blocked": "Ticket geblokkeerd",
    "Ticket code is ambiguous on list": "Ticket-code op de lijst is niet eenduidig",
    "Ticket code revoked/changed": "Kaartjescode ingetrokken/veranderd",
    "Ticket design": "Kaartjesontwerp",
    "Ticket not paid": "Kaartje niet betaald",
    "Ticket not valid at this time": "Ticket is op dit moment niet geldig",
    "Ticket type not allowed here": "Kaartjestype hier niet toegestaan",
    "Tolerance (minutes)": "Speling (minuten)",
    "Total": "Totaal",
    "Total revenue": "Totaalomzet",
    "Trustly": "Trustly",
    "Tu": "Di",
    "Tuesday": "Dinsdag",
    "Unknown error.": "Onbekende fout.",
    "Unknown ticket": "Onbekend kaartje",
    "Unpaid": "Niet betaald",
    "Use a different name internally": "Gebruik intern een andere naam",
    "Valid": "Geldig",
    "Valid Tickets": "Geldige kaartjes",
    "Valid ticket": "Geldig kaartje",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Wo",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Je aanvraag wordt naar de server verstuurd. Controleer je internetverbinding en probeer het opnieuw als dit langer dan een minuut duurt.",
    "We are processing your request \u2026": "We verwerken je aanvraag\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "De server is op dit moment niet bereikbaar, we proberen het opnieuw. Laatste foutcode: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "De server is op dit moment niet bereikbaar, probeer het alsjeblieft opnieuw. Foutcode: {code}",
    "WeChat Pay": "WeChat Pay",
    "Wednesday": "Woensdag",
    "Yes": "Ja",
    "You get %(currency)s %(amount)s back": "Jij krijgt %(currency)s %(amount)s terug",
    "You have unsaved changes!": "Je hebt nog niet opgeslagen wijzigingen!",
    "Your cart has expired.": "Uw winkelwagen is verlopen.",
    "Your cart is about to expire.": "Uw winkelwagen staat op het punt om te verlopen.",
    "Your color has decent contrast and is sufficient for minimum accessibility requirements.": "Uw kleur heeft een redelijk contrast, en is voldoende voor de minimale toegankelijkheids eisen.",
    "Your color has great contrast and will provide excellent accessibility.": "Uw kleur heeft een goed contrast, en zal zorgen voor een uitstekende toegankelijkheid.",
    "Your color has insufficient contrast to white. Accessibility of your site will be impacted.": "Uw kleur heeft een te weinig contrast met wit. De toegankelijkheid van jouw site wordt be\u00efnvloed.",
    "Your local time:": "Je lokale tijd:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Je verzoek is aangekomen op de server, maar wordt nog niet verwerkt. Neem contact met ons op als dit langer dan twee minuten duurt, of ga terug in je browser en probeer het opnieuw.",
    "Your request has been queued on the server and will soon be processed.": "Je aanvraag zal binnenkort op de server in behandeling worden genomen.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Je aanvraag wordt binnenkort verwerkt. Afhankelijk van de grootte van het evenement kan dit enkele minuten duren.",
    "Zimpler": "Zimpler",
    "close": "sluiten",
    "custom date and time": "Aangepaste datum en tijd",
    "custom time": "aangepaste tijd",
    "entry_status\u0004absent": "afwezig",
    "entry_status\u0004present": "aanwezig",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "is na",
    "is before": "is voor",
    "is one of": "is een van",
    "minutes": "minuten",
    "required": "verplicht",
    "widget\u0004Back": "Terug",
    "widget\u0004Buy": "Kopen",
    "widget\u0004Checkout": "Afrekenen",
    "widget\u0004Choose a different date": "Andere datum kiezen",
    "widget\u0004Choose a different event": "Ander evenement kiezen",
    "widget\u0004Close": "Sluiten",
    "widget\u0004Close checkout": "Stoppen met afrekenen",
    "widget\u0004Close ticket shop": "Sluit kaartjeswinkel",
    "widget\u0004Continue": "Ga verder",
    "widget\u0004Currently not available": "Momenteel niet beschikbaar",
    "widget\u0004Decrease quantity": "Verlaag aantal",
    "widget\u0004FREE": "GRATIS",
    "widget\u0004Filter": "Filter",
    "widget\u0004Filter events by": "Filter evenementen op",
    "widget\u0004Hide variants": "Verberg varianten",
    "widget\u0004Image of %s": "Afbeelding van %s",
    "widget\u0004Increase quantity": "Verhoog aantal",
    "widget\u0004Load more": "Meer laden",
    "widget\u0004New price: %s": "Nieuwe prijs: %s",
    "widget\u0004Next month": "Volgende maand",
    "widget\u0004Next week": "Volgende week",
    "widget\u0004Not available anymore": "Niet langer beschikbaar",
    "widget\u0004Not yet available": "Nog niet beschikbaar",
    "widget\u0004Only available with a voucher": "Alleen beschikbaar met een voucher",
    "widget\u0004Open seat selection": "Open stoelkeuze",
    "widget\u0004Open ticket shop": "Open de kaartjeswinkel",
    "widget\u0004Original price: %s": "Originele prijs: %s",
    "widget\u0004Previous month": "Vorige maand",
    "widget\u0004Previous week": "Vorige week",
    "widget\u0004Price": "Prijs",
    "widget\u0004Quantity": "Aantal",
    "widget\u0004Redeem": "Verzilveren",
    "widget\u0004Redeem a voucher": "Verzilver een voucher",
    "widget\u0004Register": "Registreren",
    "widget\u0004Reserved": "Gereserveerd",
    "widget\u0004Resume checkout": "Doorgaan met afrekenen",
    "widget\u0004Select": "Selecteer",
    "widget\u0004Select %s": "Selecteer %s",
    "widget\u0004Select variant %s": "Selecteer variant %s",
    "widget\u0004Show variants": "Toon varianten",
    "widget\u0004Sold out": "Uitverkocht",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Sommige of alle tiketcategorie\u00ebn zijn op heden uitverkocht. Als je wilt, kun je jezelf toevoegen aan de wachtlijst. We zullen je informeren wanneer er weer plaatsen beschikbaar zijn.",
    "widget\u0004The cart could not be created. Please try again later": "De winkelwagen kon niet gemaakt worden. Probeer het later alsjeblieft opnieuw.",
    "widget\u0004The ticket shop could not be loaded.": "De kaartjeswinkel kon niet geladen worden.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Op dit moment zijn er veel gebruikers bezig in deze kaartjeswinkel. Open de winkel in een nieuw tabblad om verder te gaan.",
    "widget\u0004Voucher code": "Vouchercode",
    "widget\u0004Waiting list": "Wachtlijst",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Je winkelmandje kon niet worden aangemaakt omdat er op dit moment te veel gebruikers actief zijn in deze kaartjeswinkel. Klik op \"Doorgaan\" om dit opnieuw te proberen in een nieuw tabblad.",
    "widget\u0004You cannot cancel this operation. Please wait for loading to finish.": "U kan niet deze actie annuleren. Alstublieft wacht tot het laden is voltooid.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Je hebt momenteel een actieve winkelwagen voor dit evenement. Als je meer producten selecteert worden deze toegevoegd aan je bestaande winkelwagen.",
    "widget\u0004currently available: %s": "nu beschikbaar: %s",
    "widget\u0004from %(currency)s %(price)s": "vanaf %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "incl. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "incl. belasting",
    "widget\u0004minimum amount to order: %s": "minimale hoeveelheid om te bestellen: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "excl. belasting"
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
    "DATETIME_FORMAT": "j F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d-%m-%Y %H:%M:%S",
      "%d-%m-%y %H:%M:%S",
      "%Y-%m-%d %H:%M:%S",
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%y %H:%M:%S",
      "%Y/%m/%d %H:%M:%S",
      "%d-%m-%Y %H:%M:%S.%f",
      "%d-%m-%y %H:%M:%S.%f",
      "%Y-%m-%d %H:%M:%S.%f",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%y %H:%M:%S.%f",
      "%Y/%m/%d %H:%M:%S.%f",
      "%d-%m-%Y %H.%M:%S",
      "%d-%m-%y %H.%M:%S",
      "%d/%m/%Y %H.%M:%S",
      "%d/%m/%y %H.%M:%S",
      "%d-%m-%Y %H.%M:%S.%f",
      "%d-%m-%y %H.%M:%S.%f",
      "%d/%m/%Y %H.%M:%S.%f",
      "%d/%m/%y %H.%M:%S.%f",
      "%d-%m-%Y %H:%M",
      "%d-%m-%y %H:%M",
      "%Y-%m-%d %H:%M",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M",
      "%Y/%m/%d %H:%M",
      "%d-%m-%Y %H.%M",
      "%d-%m-%y %H.%M",
      "%d/%m/%Y %H.%M",
      "%d/%m/%y %H.%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d-%m-%Y",
      "%d-%m-%y",
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y/%m/%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j-n-Y H:i",
    "SHORT_DATE_FORMAT": "j-n-Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H.%M:%S",
      "%H.%M:%S.%f",
      "%H.%M",
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

