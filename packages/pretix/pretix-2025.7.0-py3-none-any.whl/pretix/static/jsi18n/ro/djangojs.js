

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2;
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
      "(o dat\u0103 \u00een plus)",
      "({num} date \u00een plus)",
      "({num} date \u00een plus)"
    ],
    "Add condition": "Adaug\u0103 condi\u021bie",
    "Additional information required": "Sunt necesare mai multe informa\u021bii",
    "All": "Toate",
    "All of the conditions below (AND)": "Toate condi\u021biile de mai jos (\u0218I)",
    "An error has occurred.": "S-a produs o eroare.",
    "An error of type {code} occurred.": "A avut loc o eroare de tipul {code}.",
    "Apple Pay": "Apple Pay",
    "April": "Aprilie",
    "At least one of the conditions below (OR)": "Cel pu\u021bin una dintre condi\u021biile de mai jos (SAU)",
    "August": "August",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "Zon\u0103 de Cod de bare",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Se calculeaz\u0103 pre\u021bul implicit\u2026",
    "Cancel": "Anuleaz\u0103",
    "Canceled": "Anulat",
    "Cart expired": "Co\u0219ul a expirat",
    "Check-in QR": "QR Check-in",
    "Checked-in Tickets": "Bilete Scanate",
    "Click to close": "Click pentru a \u00eenchide",
    "Close message": "\u00cenchide mesajul",
    "Comment:": "Comentariu:",
    "Confirming your payment \u2026": "Se confirm\u0103 plata\u2026",
    "Contacting Stripe \u2026": "Se conecteaz\u0103 Stripe\u2026",
    "Contacting your bank \u2026": "Se contacteaz\u0103 banca \u2026",
    "Continue": "Continu\u0103",
    "Copied!": "Copiat!",
    "Count": "Num\u0103r",
    "Credit Card": "Card bancar",
    "Current date and time": "Data \u0219i ora curent\u0103",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Ziua curent\u0103 a s\u0103pt\u0103m\u00e2nii (1 = Luni, 7 = Duminic\u0103)",
    "Currently inside": "Aflat \u00een interior",
    "December": "Decembrie",
    "Do you really want to leave the editor without saving your changes?": "E\u0219ti sigur c\u0103 dore\u0219ti s\u0103 p\u0103r\u0103se\u0219ti editorul f\u0103r\u0103 a salva schimb\u0103rile efectuate?",
    "Entry": "Intrare",
    "Entry not allowed": "Intrarea nu este permis\u0103",
    "Error while uploading your PDF file, please try again.": "Eroare la \u00eenc\u0103rcarea fi\u0219ierului PDF, te rug\u0103m s\u0103 re\u00eencerci.",
    "Event admission": "Participarea la eveniment",
    "Event end": "Evenimentul se termin\u0103",
    "Event start": "Evenimentul \u00eencepe",
    "Exit": "Ie\u0219ire",
    "Exit recorded": "Ie\u0219ire \u00eenregistrat\u0103",
    "February": "Februarie",
    "Fr": "Vi",
    "Generating messages \u2026": "Se genereaz\u0103 mesajele \u2026",
    "Group of objects": "Grup de obiecte",
    "Image area": "Zon\u0103 de Imagine",
    "Information required": "Informa\u021bii necesare",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Ianuarie",
    "July": "Iulie",
    "June": "Iunie",
    "Load more": "Mai mult",
    "March": "Martie",
    "Marked as paid": "Marcat ca pl\u0103tit",
    "Maxima": "Maxima",
    "May": "Mai",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minute de la prima intrare (-1 la prima intrare)",
    "Minutes since last entry (-1 on first entry)": "Minute de la ultima intrare (-1 la prima intrare)",
    "Mo": "Lu",
    "MyBank": "MyBank",
    "No": "Nu",
    "No active check-in lists found.": "Nicio list\u0103 de check-in g\u0103sit\u0103.",
    "No tickets found": "Niciun bilet g\u0103sit",
    "None": "Niciunul",
    "November": "Noiembrie",
    "Number of days with a previous entry": "Num\u0103rul de zile cu o intrare anterioar\u0103",
    "Number of previous entries": "Num\u0103rul intr\u0103rilor anterioare",
    "Number of previous entries since midnight": "Num\u0103rul intr\u0103rilor ulterioare p\u00e2n\u0103 la sf\u00e2r\u0219itul zilei",
    "OXXO": "OXXO",
    "Object": "Obiect",
    "October": "Octombrie",
    "Order canceled": "Comand\u0103 anulat\u0103",
    "Others": "Altele",
    "Paid orders": "Comenzi pl\u0103tite",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal - Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "Metod\u0103 de plat\u0103 indisponibil\u0103",
    "Placed orders": "Comenzi plasate",
    "Please enter the amount the organizer can keep.": "Introdu valoarea pe care o poate p\u0103stra organizatorul.",
    "Powered by pretix": "Dezvoltat de pretix",
    "Press Ctrl-C to copy!": "Apas\u0103 Ctrl+C pentru a copia!",
    "Product": "Produs",
    "Product variation": "Varia\u021bii produs",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Revendicat",
    "Result": "Rezultat",
    "SEPA Direct Debit": "SEPA Direct Debit",
    "SOFORT": "SOFORT",
    "Sa": "S\u00e2",
    "Saving failed.": "Salvarea a e\u0219uat.",
    "Scan a ticket or search and press return\u2026": "Scaneaz\u0103 sau caut\u0103 un bilet \u0219i apas\u0103 Enter\u2026",
    "Search query": "Caut\u0103 sintaxa",
    "Search results": "Rezultatele c\u0103ut\u0103rii",
    "Select a check-in list": "Selecteaz\u0103 o list\u0103 de check-in",
    "Selected only": "Doar selec\u021bia",
    "September": "Septembrie",
    "Su": "Du",
    "Switch check-in list": "Schimb\u0103 lista de check-in",
    "Switch direction": "Schimb\u0103 direc\u021bia",
    "Th": "Jo",
    "The PDF background file could not be loaded for the following reason:": "Fi\u0219ierul de fundal al PDF-ului nu a putut fi \u00eenc\u0103rcat din aceast\u0103 cauz\u0103:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Articolele din co\u0219ul t\u0103u nu mai sunt rezervate. Mai po\u021bi \u00eenc\u0103 finaliza comanda at\u00e2t timp c\u00e2t acestea mai apar disponibile.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Articolele din co\u0219 mai sunt rezervate pentru \u00eenc\u0103 un\u00a0minut.",
      "Articolele din co\u0219 mai sunt rezervate pentru \u00eenc\u0103 {num}\u00a0minute.",
      "Articolele din co\u0219 mai sunt rezervate pentru \u00eenc\u0103 {num}\u00a0minute."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Organizatorul p\u0103streaz\u0103 %(currency)s %(amount)s",
    "The request took too long. Please try again.": "Solicitarea a durat cam mult. Te rug\u0103m s\u0103 re\u00eencerci.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Acest bilet nu este \u00eenc\u0103 pl\u0103tit. Vrei totu\u0219i s\u0103 continui?",
    "This ticket requires special attention": "Acest bilet necesit\u0103 aten\u021bie special\u0103",
    "Ticket already used": "Bilet deja utilizat",
    "Ticket code revoked/changed": "Codul biletului a fost anulat/modificat",
    "Ticket design": "Design bilet",
    "Ticket not paid": "Bilet nepl\u0103tit",
    "Ticket type not allowed here": "Tipul de bilet nu este permis aici",
    "Tolerance (minutes)": "Toleran\u021b\u0103 (minute)",
    "Total": "Total",
    "Total revenue": "Total \u00eencas\u0103ri",
    "Trustly": "Trustly",
    "Tu": "Ma",
    "Unknown error.": "Eroare necunoscut\u0103.",
    "Unknown ticket": "Bilet necunoscut",
    "Unpaid": "Nepl\u0103tit\u0103",
    "Use a different name internally": "Folose\u0219te un nume intern diferit",
    "Valid": "Valid",
    "Valid Tickets": "Bilete Valide",
    "Valid ticket": "Bilet valid",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Mi",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Trimitem solicitarea ta c\u0103tre server. Dac\u0103 acest proces dureaz\u0103 mai mult de un minut, te rug\u0103m s\u0103 verifici conexiunea la internet, s\u0103 re\u00eencarci aceast\u0103 pagin\u0103 \u0219i s\u0103 re\u00eencerci.",
    "We are processing your request \u2026": "Se proceseaz\u0103 solicitarea \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Momentan nu putem comunica cu serverul, dar re\u00eencerc\u0103m. Ultimul cod de eroare: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Momentan nu putem comunica cu serverul. Te rug\u0103m s\u0103 re\u00eencerci. Cod eroare: {code}",
    "WeChat Pay": "WeChat Pay",
    "Yes": "Da",
    "You get %(currency)s %(amount)s back": "Prime\u0219ti \u00eenapoi %(currency)s %(amount)s",
    "You have unsaved changes!": "Ai modific\u0103ri nesalvate!",
    "Your local time:": "Ora local\u0103:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Solicitarea ta a fost primit\u0103 de server, \u00eens\u0103 se a\u0219teapt\u0103 s\u0103 fie procesat\u0103. Dac\u0103 acest lucru dureaz\u0103 mai mult de dou\u0103 minute, te rug\u0103m s\u0103 ne contactezi sau s\u0103 revii \u00een browser \u0219i s\u0103 re\u00eencerci.",
    "Your request has been queued on the server and will soon be processed.": "Solicitarea ta a fost transmis\u0103 c\u0103tre server \u0219i va fi procesat\u0103 \u00een cur\u00e2nd.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Solicitarea ta este \u00een curs de procesare. \u00cen func\u021bie de amploarea evenimentului, aceasta poate dura c\u00e2teva minute.",
    "Zimpler": "Zimpler",
    "close": "\u00eenchide",
    "custom date and time": "dat\u0103 \u0219i timp personalizate",
    "custom time": "timp personalizat",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "e dup\u0103",
    "is before": "e \u00eenainte de",
    "is one of": "e unul dintre",
    "minutes": "minute",
    "required": "necesar",
    "widget\u0004Back": "\u00cenapoi",
    "widget\u0004Buy": "Cump\u0103r\u0103",
    "widget\u0004Choose a different date": "Alege o dat\u0103 diferit\u0103",
    "widget\u0004Choose a different event": "Alege un eveniment diferit",
    "widget\u0004Close": "\u00cenchide",
    "widget\u0004Close ticket shop": "\u00cenchide magazinul de bilete",
    "widget\u0004Continue": "Continu\u0103",
    "widget\u0004FREE": "GRATUIT",
    "widget\u0004Load more": "Mai mult",
    "widget\u0004Next month": "Luna viitoare",
    "widget\u0004Next week": "S\u0103pt\u0103m\u00e2na viitoare",
    "widget\u0004Only available with a voucher": "Disponibil doar cu un voucher",
    "widget\u0004Open seat selection": "Deschide selec\u021bia locurilor",
    "widget\u0004Open ticket shop": "Deschide magazinul de bilete",
    "widget\u0004Previous month": "Luna trecut\u0103",
    "widget\u0004Previous week": "S\u0103pt\u0103m\u00e2na trecut\u0103",
    "widget\u0004Redeem": "Revendic\u0103",
    "widget\u0004Redeem a voucher": "Revendic\u0103 un voucher",
    "widget\u0004Register": "\u00cenregistreaz\u0103-te",
    "widget\u0004Reserved": "Rezervat",
    "widget\u0004Resume checkout": "Continu\u0103 plata",
    "widget\u0004Sold out": "Epuizat",
    "widget\u0004The cart could not be created. Please try again later": "Co\u0219ul nu a putut fi creat. Te rug\u0103m s\u0103 re\u00eencerci mai t\u00e2rziu",
    "widget\u0004The ticket shop could not be loaded.": "Magazinul de bilete nu a putut fi \u00eenc\u0103rcat.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Momentan sunt o mul\u021bime de utilizatori \u00een acest shop. Deschide magazinul \u00eentr-un nou tab pentru a continua.",
    "widget\u0004Voucher code": "Cod voucher",
    "widget\u0004Waiting list": "List\u0103 de a\u0219teptare",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Nu am putut crea co\u0219ul t\u0103u fiindc\u0103 sunt prea mul\u021bi utilizatori \u00een acest magazin. Click pe \u201eContinu\u0103\u201d pentru a re\u00eencerca \u00eentr-un tab nou.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Momentan ai un co\u0219 activ la acest eveniment. Dac\u0103 selectezi mai multe produse, ele se vor ad\u0103uga co\u0219ului existent.",
    "widget\u0004currently available: %s": "disponibile momentan: %s",
    "widget\u0004from %(currency)s %(price)s": "de la %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "inclusiv %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "inclusiv taxele",
    "widget\u0004minimum amount to order: %s": "valoare minim\u0103 de comandat: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "plus taxele"
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
    "DATETIME_FORMAT": "j F Y, H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y, %H:%M",
      "%d.%m.%Y, %H:%M:%S",
      "%d.%B.%Y, %H:%M",
      "%d.%B.%Y, %H:%M:%S",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%b.%Y",
      "%d %B %Y",
      "%A, %d %B %Y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y, H:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M",
      "%H:%M:%S",
      "%H:%M:%S.%f"
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

