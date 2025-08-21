

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
      "(en dato mere)",
      "({num} datoer mere)"
    ],
    "All": "Alle",
    "An error has occurred.": "Der er sket en fejl.",
    "An error of type {code} occurred.": "Der er sket en fejl ({code}).",
    "Apple Pay": "Apple Pay",
    "April": "April",
    "August": "August",
    "Bancontact": "Bancontact",
    "Barcode area": "QR-kode-omr\u00e5de",
    "Canceled": "Annulleret",
    "Cart expired": "Kurv udl\u00f8bet",
    "Check-in QR": "Check-in QR",
    "Click to close": "Klik for at lukke",
    "Close message": "Luk besked",
    "Comment:": "Kommentar:",
    "Confirming your payment \u2026": "Bekr\u00e6fter din betaling \u2026",
    "Contacting Stripe \u2026": "Kontakter Stripe \u2026",
    "Contacting your bank \u2026": "Kontakter din bank \u2026",
    "Copied!": "Kopieret!",
    "Count": "Antal",
    "Credit Card": "Kreditkort",
    "Current date and time": "Aktuel dato og klokkesl\u00e6t",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Aktuel ugedag (1 = mandag, 7 = s\u00f8ndag)",
    "Currently inside": "Inde i \u00f8jeblikket",
    "December": "December",
    "Do you really want to leave the editor without saving your changes?": "Er du sikker p\u00e5 at du vil forlade editoren uden at gemme dine \u00e6ndringer?",
    "Entry": "Indgang",
    "Entry not allowed": "Adgang ikke tilladt",
    "Error while uploading your PDF file, please try again.": "Fejl under upload af pdf. Pr\u00f8v venligt igen.",
    "Event admission": "Adgang til arrangementet",
    "Exit": "Udgang",
    "February": "Februar",
    "Fr": "Fre",
    "Gate": "Indgang",
    "Generating messages \u2026": "Opretter beskeder \u2026",
    "Group of objects": "Gruppe af objekter",
    "Information required": "Kr\u00e6ver information",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Januar",
    "July": "Juli",
    "June": "Juni",
    "Load more": "Hent flere",
    "March": "Marts",
    "Marked as paid": "Markeret som betalt",
    "May": "Maj",
    "Mo": "Man",
    "MyBank": "MyBank",
    "No": "Nej",
    "No active check-in lists found.": "Der blev ikke fundet nogen aktive check-in lister.",
    "No tickets found": "Ingen billetter fundet",
    "None": "Ingen",
    "November": "November",
    "Number of previous entries": "Antal tidligere poster",
    "Object": "Objekt",
    "October": "Oktober",
    "Order canceled": "Bestilling annulleret",
    "Order not approved": "Bestilling ikke godkendt",
    "Others": "Andre",
    "Paid orders": "Betalte bestillinger",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Pay Later",
    "Payment method unavailable": "Betalingsmetode er ikke tilg\u00e6ngelig",
    "Placed orders": "Afgivne bestillinger",
    "Powered by pretix": "Drevet af pretix",
    "Press Ctrl-C to copy!": "Tryk Ctrl-C eller \u2318-C for at kopiere!",
    "Product": "Produkt",
    "Product variation": "Produktvariation",
    "Przelewy24": "Przelewy24",
    "Result": "Resultat",
    "SEPA Direct Debit": "SEPA Direct Debit",
    "SOFORT": "SOFORT",
    "Sa": "L\u00f8r",
    "Saving failed.": "Gem fejlede.",
    "Scan a ticket or search and press return\u2026": "Scan en billet eller s\u00f8g og tryk p\u00e5 retur\u2026",
    "Search results": "S\u00f8geresultater",
    "Select a check-in list": "V\u00e6lg en check-in liste",
    "September": "September",
    "Su": "S\u00f8n",
    "Switch check-in list": "Skift check-in liste",
    "Switch direction": "Skift retning",
    "Th": "Tors",
    "The PDF background file could not be loaded for the following reason:": "Baggrunds-pdf'en kunne ikke hentes af f\u00f8lgende grund:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Varerne i din indk\u00f8bskurv er ikke l\u00e6ngere reserverede til dig. Du kan stadig f\u00e6rdigg\u00f8re din ordre, s\u00e5 l\u00e6nge der er ledige billetter.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Varerne i din kurv er reserveret for dig i et minut.",
      "Varerne i din kurv er reserveret for dig i {num} minutter."
    ],
    "The request took too long. Please try again.": "Foresp\u00f8rgslen tog for lang tid. Pr\u00f8v igen.",
    "This ticket requires special attention": "Denne billet kr\u00e6ver s\u00e6rlig opm\u00e6rksomhed",
    "Ticket already used": "Billet allerede i brug",
    "Ticket blocked": "Billet blokeret",
    "Ticket code is ambiguous on list": "Billetkoden er flertydig p\u00e5 listen",
    "Ticket code revoked/changed": "Billetkode trukket tilbage/\u00e6ndret",
    "Ticket design": "Billetdesign",
    "Ticket not paid": "Billet ikke betalt",
    "Ticket not valid at this time": "Billetten er ikke gyldig p\u00e5 dette tidspunkt",
    "Ticket type not allowed here": "Billettype er ikke tilladt her",
    "Total": "Total",
    "Total revenue": "Oms\u00e6tning i alt",
    "Tu": "Tirs",
    "Unknown error.": "Ukendt fejl.",
    "Unknown ticket": "Ukendt billet",
    "Unpaid": "Ubetalt",
    "Valid": "Gyldig",
    "Valid Tickets": "Gyldige billetter",
    "Valid ticket": "Gyldig billet",
    "Venmo": "Venmo",
    "We": "Ons",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Din foresp\u00f8rgsel bliver sendt til serveren. Hvis det tager mere end et minut, s\u00e5 tjek din internetforbindelse, genindl\u00e6s siden og pr\u00f8v igen.",
    "We are processing your request \u2026": "Vi behandler din bestilling \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Vi kan ikke komme i kontakt med serveren, men pr\u00f8ver igen. Seneste fejlkode: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Vi kan i \u00f8jeblikket ikke komme i kontakt med serveren. Pr\u00f8v igen. Fejlkode: {code}",
    "Yes": "Ja",
    "You have unsaved changes!": "Du har \u00e6ndringer, der ikke er gemt!",
    "Your local time:": "Din lokaltid:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Din foresp\u00f8rgsel er under behandling. Hvis der g\u00e5r mere end to minutter, s\u00e5 kontakt os eller g\u00e5 tilbage og pr\u00f8v igen.",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "er efter",
    "is before": "er f\u00f8r",
    "is one of": "er en af",
    "widget\u0004Back": "Tilbage",
    "widget\u0004Buy": "L\u00e6g i kurv",
    "widget\u0004Choose a different date": "V\u00e6lg en anden dato",
    "widget\u0004Choose a different event": "V\u00e6lg et andet arrangement",
    "widget\u0004Close": "Luk",
    "widget\u0004Close ticket shop": "Luk billetbutik",
    "widget\u0004Continue": "Forts\u00e6t",
    "widget\u0004FREE": "GRATIS",
    "widget\u0004Load more": "Hent flere",
    "widget\u0004Next month": "N\u00e6ste m\u00e5ned",
    "widget\u0004Next week": "N\u00e6ste uge",
    "widget\u0004Only available with a voucher": "Kun tilg\u00e6ngelig med en rabatkode",
    "widget\u0004Open seat selection": "\u00c5bn s\u00e6devalg",
    "widget\u0004Previous month": "Forrige m\u00e5ned",
    "widget\u0004Redeem": "Indl\u00f8s",
    "widget\u0004Redeem a voucher": "Indl\u00f8s rabatkode",
    "widget\u0004Register": "Book nu",
    "widget\u0004Reserved": "Reserveret",
    "widget\u0004Resume checkout": "Forts\u00e6t booking",
    "widget\u0004Sold out": "Udsolgt",
    "widget\u0004The cart could not be created. Please try again later": "Kurven kunne ikke oprettes. Pr\u00f8v igen senere",
    "widget\u0004The ticket shop could not be loaded.": "Billetbutikken kunne ikke hentes.",
    "widget\u0004Voucher code": "Rabatkode",
    "widget\u0004Waiting list": "Venteliste",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Du har allerede en aktiv booking i gang for dette arrangement. Hvis du v\u00e6lger flere produkter, s\u00e5 vil de blive tilf\u00f8jet din eksisterende booking.",
    "widget\u0004currently available: %s": "tilg\u00e6ngelig: %s",
    "widget\u0004from %(currency)s %(price)s": "fra %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "inkl. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "inkl. moms",
    "widget\u0004minimum amount to order: %s": "minimumsantal: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "plus moms"
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

