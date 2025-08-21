

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
    "=": "=",
    "Additional information required": "Beharrezko informazio gehigarria",
    "All": "Guztiak",
    "An error of type {code} occurred.": "{kode} motako errore bat gertatu da.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "Onartzeko zain",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Boleto": "Boleto",
    "Cancel": "Ezeztatu",
    "Canceled": "Ezeztatua",
    "Cart expired": "Saskia iraungita",
    "Checked-in Tickets": "Tiketak erosita",
    "Close message": "Mezua itxi",
    "Comment:": "Iruzkina:",
    "Confirmed": "Baieztatua",
    "Confirming your payment \u2026": "Ordainketa egiaztatzen \u2026",
    "Contacting Stripe \u2026": "Stripe-ekin kontaktatzen \u2026",
    "Contacting your bank \u2026": "Zure bankuarekin kontaktatzen \u2026",
    "Continue": "Jarraitu",
    "Copied!": "Kopiatuta!",
    "Credit Card": "Kreditu txartela",
    "Current date and time": "Uneko data eta ordua",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Asteko uneko eguna (1 = astelehena, 7 = igandea)",
    "Current entry status": "Egungo sarrera-egoera",
    "Currently inside": "Barruan orain bertan",
    "Entry": "Sarbidea",
    "Entry not allowed": "Ezin da sartu",
    "Event admission": "Ekitaldiaren onarpena",
    "Event end": "Ekitaldiaren amaiera",
    "Event start": "Ekitaldiaren hasiera",
    "Exit": "Irteera",
    "Exit recorded": "Irteera erregistratua",
    "Gate": "Atea",
    "Information required": "Beharrezko informazioa",
    "Ita\u00fa": "Ita\u00fa",
    "Load more": "Gehiago kargatu",
    "Marked as paid": "Ordaindutzat markatua",
    "Maxima": "Maxima",
    "Mercado Pago": "Mercado Pago",
    "MyBank": "MyBank",
    "No": "Ez",
    "No active check-in lists found.": "Ez da aurkitu erregistro-zerrenda aktiborik.",
    "No tickets found": "Ez da tiketik aurkitu",
    "Number of days with a previous entry": "Aurreko sarrera bat duten egunen kopurua",
    "Number of previous entries": "Aurreko sarreren kopurua",
    "Number of previous entries before": "Aurreko sarreren kopurua",
    "Number of previous entries since": "Aurreko sarrera-kopurua, orduz geroztik",
    "Number of previous entries since midnight": "Aurreko sarrera kopurua gauerditik aurrera",
    "OXXO": "OXXO",
    "Order canceled": "Eskaera ezeztatua",
    "Order not approved": "Ez da onartu eskaera",
    "Paid orders": "Ordaindutako eskaerak",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "Ordainketa-modu hau ez dago erabilgarri",
    "Placed orders": "Egindako eskaerak",
    "Press Ctrl-C to copy!": "Sakatu Ctrl-C kopiatzeko!",
    "Product": "Produktua",
    "Product variation": "Produktuen aniztasuna",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Berrerosia",
    "Result": "Emaitza",
    "SEPA Direct Debit": "SEPA Zuzeneko Zordunketa",
    "SOFORT": "SOFORT",
    "Scan a ticket or search and press return\u2026": "Eskaneatu tiket bat edo bilatu eta sakatu itzuli\u2026",
    "Search results": "Emaitzak bilatu",
    "Select a check-in list": "Hautatu erregistro-zerrenda bat",
    "Switch check-in list": "Erregistro-zerrenda aldatu",
    "Switch direction": "Helbidea aldatu",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Zure saskiko produktuak ez daude zuretzat erreserbatuta. Oraindik ere zure eskaera bete dezakezu, baldin eta eskuragarri badaude.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Zure saskiko produktuak minutu  -ez erreserbatuta daude zuretzat.",
      "Zure saskiko produktuak {num}  minutuz erreserbatuta daude zuretzat."
    ],
    "The request took too long. Please try again.": "Gehiegi luzatu da eskaera. Mesedez, saiatu berriro.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Tiket hori oraindik ordaindu gabe dago. Jarraitu nahi duzu, dena den?",
    "This ticket requires special attention": "Tiket honek arreta berezia eskatzen du",
    "Ticket already used": "Erabilitako tiketa",
    "Ticket blocked": "Tiketa blokeatuta",
    "Ticket code is ambiguous on list": "Tiketaren kodea anbiguoa da zerrendan",
    "Ticket code revoked/changed": "Baliogabetutako/aldatutako tiketaren kodea",
    "Ticket design": "Sarrera diseinua",
    "Ticket not paid": "Tiketa ordaindu gabe",
    "Ticket not valid at this time": "Tiketa ez dago erabilgarri momentu honetan",
    "Ticket type not allowed here": "Tiket mota hau ez da onartzen hemen",
    "Total": "Guztira",
    "Total revenue": "Diru-sarrerak guztira",
    "Trustly": "Trustly",
    "Unknown ticket": "Tiket ezezaguna",
    "Unpaid": "Ordaindu gabea",
    "Valid": "Baliozkoa",
    "Valid Tickets": "Baliozko tiketak",
    "Valid ticket": "Baliozko tiketa",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Une honetan zure eskaera zerbitzarira bidaltzen ari gara. Honek minutu bat baino gehiago irauten badu, mesedez, berrikusi zure Interneteko konexioa eta gero kargatu berriro orri hau eta saiatu berriro.",
    "We are processing your request \u2026": "Zure eskaera prozesatzen ari gara \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Orain bertan ezin gara zerbitzarira iritsi, baina saiatzen jarraitzen dugu. Azken errore-kodea: {kodea}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Une honetan ezin gara zerbitzarira iritsi. Mesedez, saiatu berriro. Errore-kodea: {kodea}",
    "WeChat Pay": "WeChat Pay",
    "Yes": "Bai",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Zure eskaera zerbitzarira iritsi da, baina oraindik prozesatzea espero dugu. Bi minutu baino gehiago irauten badu, mesedez, jarri gurekin harremanetan edo itzuli zure nabigatzailera eta saiatu berriro.",
    "Your request has been queued on the server and will soon be processed.": "Zure eskaera zerbitzarian gorde da eta laster prozesatuko da.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Zure eskaera prozesatzen ari dira. Gertaeraren tamainaren arabera, baliteke minutu batzuk behar izatea.",
    "Zimpler": "Zimpler",
    "close": "itxi",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "ondoren da",
    "is before": "lehenago da",
    "is one of": "-ko bat da",
    "minutes": "minutuak"
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
    "DATETIME_FORMAT": "Y\\k\\o N j\\a, H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M"
    ],
    "DATE_FORMAT": "Y\\k\\o N j\\a",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%b %d %Y",
      "%b %d, %Y",
      "%d %b %Y",
      "%d %b, %Y",
      "%B %d %Y",
      "%B %d, %Y",
      "%d %B %Y",
      "%d %B, %Y"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "F\\r\\e\\n j\\a",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "Y-m-d H:i",
    "SHORT_DATE_FORMAT": "Y-m-d",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "Y\\k\\o F"
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

