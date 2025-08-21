

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
    "Add condition": "Lis\u00e4\u00e4 ehto",
    "All": "Kaikki",
    "An error has occurred.": "Tapahtui virhe.",
    "An error of type {code} occurred.": "Tapahtui virhe. Virhekoodi: {code}.",
    "April": "Huhtikuu",
    "August": "Elokuu",
    "Barcode area": "Viivakoodialue",
    "Calculating default price\u2026": "Lasketaan oletushintaa\u2026",
    "Cart expired": "Ostoskori on vanhentunut",
    "Click to close": "Sulje klikkaamalla",
    "Close message": "Sulje viesti",
    "Comment:": "Kommentti:",
    "Confirming your payment \u2026": "Maksuasi vahvistetaan \u2026",
    "Copied!": "Kopioitu!",
    "Count": "M\u00e4\u00e4r\u00e4",
    "Current date and time": "Nykyinen p\u00e4iv\u00e4m\u00e4\u00e4r\u00e4 ja aika",
    "December": "Joulukuu",
    "Event end": "Tapahtuma p\u00e4\u00e4ttyy",
    "Event start": "Tapahtuma alkaa",
    "February": "Helmikuu",
    "Fr": "Pe",
    "January": "Tammikuu",
    "July": "Hein\u00e4kuu",
    "June": "Kes\u00e4kuu",
    "March": "Maaliskuu",
    "Marked as paid": "Merkitty maksetuksi",
    "May": "Toukokuu",
    "Mo": "Ma",
    "No": "Ei",
    "November": "Marraskuu",
    "October": "Lokakuu",
    "Others": "Muut",
    "Paid orders": "Maksetut tilaukset",
    "Press Ctrl-C to copy!": "Paina Ctrl-C kopioidaksesi!",
    "Product": "Tuote",
    "Product variation": "Tuotevariaatio",
    "Sa": "La",
    "Saving failed.": "Tallennus ep\u00e4onnistui.",
    "September": "Syyskuu",
    "Su": "Su",
    "Th": "To",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Ostoskorissasi olevat tuotteet eiv\u00e4t ole en\u00e4\u00e4 varattu sinulle. Voit silti suorittaa tilauksen loppuun niin kauan kuin tuotteita on saatavilla.",
    "The request took too long. Please try again.": "Pyynt\u00f6 aikakatkaistiin. Ole hyv\u00e4 ja yrit\u00e4 uudelleen.",
    "Ticket already used": "Lippu k\u00e4ytetty",
    "Ticket code revoked/changed": "Lippukoodi peruttu/muutettu",
    "Ticket not paid": "Lippu maksamatta",
    "Ticket type not allowed here": "Lipputyyppi ei sallittu",
    "Tolerance (minutes)": "Toleranssi (minuuttia)",
    "Total": "Summa",
    "Tu": "Ti",
    "Unknown error.": "Tuntematon virhe.",
    "Unknown ticket": "Tuntematon lippu",
    "Use a different name internally": "K\u00e4yt\u00e4 toista nime\u00e4 sis\u00e4isesti",
    "We": "Ke",
    "We are processing your request \u2026": "Pyynt\u00f6\u00e4si k\u00e4sitell\u00e4\u00e4n \u2026",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Palvelimeen ei juuri nyt saatu yhteytt\u00e4. Ole hyv\u00e4 ja yrit\u00e4 uudelleen. Virhekoodi: {code}",
    "Yes": "Kyll\u00e4",
    "You have unsaved changes!": "Sinulla on tallentamattomia muutoksia!",
    "custom time": "mukautettu aika",
    "widget\u0004Back": "Takaisin",
    "widget\u0004Buy": "Osta",
    "widget\u0004Choose a different date": "Valitse toinen p\u00e4iv\u00e4m\u00e4\u00e4r\u00e4",
    "widget\u0004Choose a different event": "Valitse toinen tapahtuma",
    "widget\u0004Close": "Sulje",
    "widget\u0004Close ticket shop": "Sulje lippukauppa",
    "widget\u0004Continue": "Jatka",
    "widget\u0004FREE": "ILMAINEN",
    "widget\u0004Next month": "Seuraava kuukausi",
    "widget\u0004Next week": "Seuraava viikko",
    "widget\u0004Only available with a voucher": "Saatavilla vain kupongilla",
    "widget\u0004Open seat selection": "Avaa paikkavalinta",
    "widget\u0004Previous month": "Edellinen kuukausi",
    "widget\u0004Previous week": "Edellinen viikko",
    "widget\u0004Redeem": "K\u00e4yt\u00e4",
    "widget\u0004Redeem a voucher": "K\u00e4yt\u00e4 kuponki",
    "widget\u0004Reserved": "Varattu",
    "widget\u0004Sold out": "Loppuunmyyty",
    "widget\u0004The cart could not be created. Please try again later": "Ostoskoria ei voitu luoda. Ole hyv\u00e4 ja yrit\u00e4 my\u00f6hemmin uudelleen",
    "widget\u0004The ticket shop could not be loaded.": "Lippukauppaa ei voitu ladata.",
    "widget\u0004Voucher code": "Kuponkikoodi",
    "widget\u0004Waiting list": "Jonotuslista",
    "widget\u0004currently available: %s": "nyt saatavilla: %s",
    "widget\u0004incl. taxes": "sis. verot"
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
    "DATETIME_FORMAT": "j. E Y \\k\\e\\l\\l\\o G.i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H.%M.%S",
      "%d.%m.%Y %H.%M.%S.%f",
      "%d.%m.%Y %H.%M",
      "%d.%m.%y %H.%M.%S",
      "%d.%m.%y %H.%M.%S.%f",
      "%d.%m.%y %H.%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. E Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j.n.Y G.i",
    "SHORT_DATE_FORMAT": "j.n.Y",
    "THOUSAND_SEPARATOR": "\u00a0",
    "TIME_FORMAT": "G.i",
    "TIME_INPUT_FORMATS": [
      "%H.%M.%S",
      "%H.%M.%S.%f",
      "%H.%M",
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

