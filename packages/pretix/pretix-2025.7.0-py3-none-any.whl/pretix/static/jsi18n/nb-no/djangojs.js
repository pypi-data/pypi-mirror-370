

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
      "(en mer dato)",
      "({num} flere datoer)"
    ],
    "Add condition": "Legg til betingelse",
    "Additional information required": "pretix account invitation",
    "All": "Alle",
    "All of the conditions below (AND)": "Alle betingelsene nedenfor (AND)",
    "An error has occurred.": "En feil har oppst\u00e5tt.",
    "An error of type {code} occurred.": "En feil av type {code} oppsto.",
    "Apple Pay": "Apple Pay",
    "April": "April",
    "At least one of the conditions below (OR)": "Minst en av betingelsene nedenfor (OR)",
    "August": "August",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "Strekkodeomr\u00e5de",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Regner ut standardpris\u2026",
    "Cancel": "Avbryt",
    "Canceled": "Avlyst",
    "Cart expired": "Handlevognen har utl\u00f8pt",
    "Check-in QR": "Sjekk-in QR",
    "Checked-in Tickets": "Innsjekkede billetter",
    "Click to close": "Klikk for \u00e5 lukke",
    "Close message": "Lukk melding",
    "Comment:": "Kommentar:",
    "Confirming your payment \u2026": "Bekrefter betalingen din\u2026",
    "Contacting Stripe \u2026": "Kontakter Stripe\u2026",
    "Contacting your bank \u2026": "Kontakter banken din\u2026",
    "Continue": "Fortsett",
    "Copied!": "Kopiert!",
    "Count": "Tell",
    "Credit Card": "Kredittkort",
    "Current date and time": "N\u00e5v\u00e6rende dato og tid",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Gjeldene ukedag (1 = Mandag, 7 = S\u00f8ndag)",
    "Currently inside": "Inne n\u00e5",
    "December": "Desember",
    "Do you really want to leave the editor without saving your changes?": "Vil du avslutte editoren uten \u00e5 lagre endringene?",
    "Duplicate": "Duplikat",
    "Entry": "Inngang",
    "Entry not allowed": "Inngang ikke tillatt",
    "Error while uploading your PDF file, please try again.": "Feil ved opplasting av PDF fil, pr\u00f8v p\u00e5 nytt.",
    "Event admission": "Event inngang",
    "Event end": "Event slutt",
    "Event start": "Event start",
    "Exit": "Avslutt",
    "Exit recorded": "Utgang registrert",
    "February": "Februar",
    "Fr": "Fr",
    "Gate": "Port",
    "Generating messages \u2026": "Genererer meldinger\u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Gruppe med objekter",
    "Image area": "Bildeomr\u00e5de",
    "Information required": "Informasjon p\u00e5krevd",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Januar",
    "July": "Juli",
    "June": "Juni",
    "Load more": "Last mer",
    "March": "Mars",
    "Marked as paid": "Merkert som betalt",
    "Maxima": "Maxima",
    "May": "Mai",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minutter siden f\u00f8rste oppf\u00f8ring (-1 p\u00e5 f\u00f8rste oppf\u00f8ring)",
    "Minutes since last entry (-1 on first entry)": "Minutter siden siste oppf\u00f8ring (-1 p\u00e5 f\u00f8rste oppf\u00f8ring)",
    "Mo": "Ma",
    "MyBank": "MyBank",
    "No": "Nei",
    "No active check-in lists found.": "Ingen aktive innsjekkingslister funnet.",
    "No tickets found": "Fant ingen billetter",
    "None": "Ingen",
    "November": "November",
    "Number of days with a previous entry": "Antall dager med en tidligere oppf\u00f8ring",
    "Number of previous entries": "Antall tidligere oppf\u00f8ringer",
    "Number of previous entries before": "Antall tidligere oppf\u00f8ringer f\u00f8r",
    "Number of previous entries since": "Antall tidligere oppf\u00f8ringer siden",
    "Number of previous entries since midnight": "Antall tidligere oppf\u00f8ringer siden midnatt",
    "OXXO": "OXXO",
    "Object": "Objekt",
    "October": "Oktober",
    "Order canceled": "Ordre kansellert",
    "Order not approved": "Ordre ikke godkjent",
    "Others": "Andre",
    "Paid orders": "Betalte ordre",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "Betalingsmetode ikke tilgjengelig",
    "Placed orders": "Ordre",
    "Please enter the amount the organizer can keep.": "Vennligst skriv inn bel\u00f8pet arrang\u00f8ren kan beholde.",
    "Powered by pretix": "Drevet av pretix",
    "Press Ctrl-C to copy!": "Trykk Ctrl-C to copy!",
    "Product": "Produkt",
    "Product variation": "Produkt variasjon",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Innl\u00f8st",
    "Result": "Resultat",
    "SEPA Direct Debit": "SEPA Direct Debit",
    "SOFORT": "SOFORT",
    "Sa": "L\u00f8",
    "Saving failed.": "Lagring feilet.",
    "Scan a ticket or search and press return\u2026": "Skann en bilett eller trykk s\u00f8k og trykk tilbake\u2026",
    "Search query": "S\u00f8keord",
    "Search results": "S\u00f8keresultater",
    "Select a check-in list": "Velg en innsjekkingsliste",
    "Selected only": "Kun valgte",
    "September": "September",
    "Su": "S\u00f8",
    "Switch check-in list": "Bytt innsjekkingsliste",
    "Switch direction": "Bytt retning",
    "Th": "To",
    "The PDF background file could not be loaded for the following reason:": "PDF bakgrunnsfilen kunne ikke lastes av f\u00f8lgende \u00e5rsak:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Varene i handlekurven din er ikke lenger reservert for deg. Du kan fortsatt fullf\u00f8re bestillingen din s\u00e5 lenge de er tilgjengelige.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Varene i handlekurven din er reservert for deg i ett minutt.",
      "Varene i handlekurven din er reservert for deg i {num} minutter."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Arrang\u00f8ren beholder %(currency)s %(bel\u00f8p)",
    "The request took too long. Please try again.": "Foresp\u00f8rselen tok for lang tid. Pr\u00f8v igjen.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Denne billetten er ikke betalt. Vil du fortsette likevel?",
    "This ticket requires special attention": "Denne billetten krever ettersyn",
    "Ticket already used": "Billetten er allerede brukt.",
    "Ticket blocked": "Billett blokkert",
    "Ticket code is ambiguous on list": "Billettkoden er tvetydig p\u00e5 listen",
    "Ticket code revoked/changed": "Billettkode tilbakekalt/endret",
    "Ticket design": "Billett design",
    "Ticket not paid": "Billetten er ikke betalt.",
    "Ticket not valid at this time": "Billetten er ikke gyldig p\u00e5 dette tidspunktet",
    "Ticket type not allowed here": "Denne Billettypen er ikke lov ikke her",
    "Tolerance (minutes)": "Toleranse (minutter)",
    "Total": "Totalt",
    "Total revenue": "Total inntekt",
    "Trustly": "Trustly",
    "Tu": "Ti",
    "Unknown error.": "Ukjent feil.",
    "Unknown ticket": "Ukjent billett",
    "Unpaid": "Ubetalt",
    "Use a different name internally": "Bruk et annet navn internt",
    "Valid": "Gyldig",
    "Valid Tickets": "Gydlige billetter",
    "Valid ticket": "Gyldig billett",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "On",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Vi sender foresp\u00f8rslene dine til serveren. Hvis dette tar langre tid en ett minutt, sjekk internett koblingen din og deretter last siden og pr\u00f8v p\u00e5 nytt.",
    "We are processing your request \u2026": "Vi gjennomf\u00f8rer foresp\u00f8rselen din\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Vi kan ikke n\u00e5 serveren akkurat n\u00e5, men vi fortsetter \u00e5 pr\u00f8ve. Siste feilkode: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Vi kan ikke n\u00e5 serveren akkurat n\u00e5. Vennligst pr\u00f8v igjen. Feilkode: {code}",
    "WeChat Pay": "WeChat Pay",
    "Yes": "Ja",
    "You get %(currency)s %(amount)s back": "Du mottar %(currency)s %(amount)s tilbake",
    "You have unsaved changes!": "Du har ikke-lagrede endringer!",
    "Your local time:": "Din lokale tid:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Foresp\u00f8rselen din kom til serveren, men vi venter fortsatt p\u00e5 at den skal behandles. Hvis dette tar lengre tid enn to minutter, kan du kontakte oss eller g\u00e5 tilbake i nettleseren din og pr\u00f8ve p\u00e5 nytt.",
    "Your request has been queued on the server and will soon be processed.": "Foresp\u00f8rrselen din er i k\u00f8 p\u00e5 serveren og vil bli gjennomf\u00f8rt snart.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Din foresp\u00f8rsel blir prosessert. Dette kan ta minutter, men varierer ut fra hvor stort arrangementet er.",
    "Zimpler": "Zimpler",
    "close": "lukk",
    "custom date and time": "egendefinert dato og klokkeslett",
    "custom time": "egendefinert tid",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "er etter",
    "is before": "er f\u00f8r",
    "is one of": "er en av",
    "minutes": "minutter",
    "required": "n\u00f8dvendig",
    "widget\u0004Back": "Tilbake",
    "widget\u0004Buy": "Kj\u00f8p",
    "widget\u0004Choose a different date": "Velg en annen dato",
    "widget\u0004Choose a different event": "Velg et annet arrangement",
    "widget\u0004Close": "Lukk",
    "widget\u0004Close ticket shop": "Steng billettbutikken",
    "widget\u0004Continue": "Fortsett",
    "widget\u0004Decrease quantity": "Begrenset antall",
    "widget\u0004FREE": "GRATIS",
    "widget\u0004Increase quantity": "\u00d8k antall",
    "widget\u0004Load more": "Last mer",
    "widget\u0004Next month": "Neste m\u00e5ned",
    "widget\u0004Next week": "Neste uke",
    "widget\u0004Only available with a voucher": "Kun tilgjengelig med kupong",
    "widget\u0004Open seat selection": "\u00c5pne setevalg",
    "widget\u0004Open ticket shop": "\u00c5pne billettbutikk",
    "widget\u0004Previous month": "Forrige m\u00e5ned",
    "widget\u0004Previous week": "Forrige uke",
    "widget\u0004Price": "Pris",
    "widget\u0004Quantity": "Antall",
    "widget\u0004Redeem": "L\u00f8s inn",
    "widget\u0004Redeem a voucher": "L\u00f8s inn en kupong",
    "widget\u0004Register": "Registrer",
    "widget\u0004Reserved": "Reservert",
    "widget\u0004Resume checkout": "Gjenoppta kassen",
    "widget\u0004Select": "Velg",
    "widget\u0004Select %s": "Velg%s",
    "widget\u0004Sold out": "Utsolgt",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Noen eller alle billettkategorier er for \u00f8yeblikket utsolgt. Hvis du \u00f8nsker, kan du legge deg til p\u00e5 ventelisten. Vi vil da gi deg beskjed hvis det blir ledige seter igjen.",
    "widget\u0004The cart could not be created. Please try again later": "Handlekurven kunne ikke opprettes. Vennligst pr\u00f8v igjen senere",
    "widget\u0004The ticket shop could not be loaded.": "Billettbutikken kunne ikke lastes.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Det er for tiden mange brukere i denne billettbutikken. \u00c5pne butikken i en ny fane for \u00e5 fortsette.",
    "widget\u0004Voucher code": "Kupongkode",
    "widget\u0004Waiting list": "Venteliste",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Vi kunne ikke opprette din handlekurv, p\u00e5 grunn av for mange brukere i billettshopen. Vennligst klikk \u00abFortsett\u00bb for \u00e5 pr\u00f8ve p\u00e5 nytt i en ny fane.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Du har allerede en aktiv handlekurv for dette arrangementet. Hvis du velger flere produkter, vil disse bli lagt til i den eksisterende handlekurven.",
    "widget\u0004currently available: %s": "tilgjengelig for \u00f8yeblikket: %s",
    "widget\u0004from %(currency)s %(price)s": "fra %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "inkl. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "Inkl. skatt",
    "widget\u0004minimum amount to order: %s": "minimumsbel\u00f8p for bestilling: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "pluss %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "pluss skatt"
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
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%d.%m.%y %H:%M:%S",
      "%d.%m.%y %H:%M:%S.%f",
      "%d.%m.%y %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. F Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%d.%m.%Y",
      "%d.%m.%y"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y H:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": "\u00a0",
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

