

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = (n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "Check-in QR": "QR na odbavenie",
    "Checked-in Tickets": "Odbaven\u00e9 vstupenky",
    "December": "December",
    "Exit": "Odchod",
    "March": "Marec",
    "May": "M\u00e1j",
    "No active check-in lists found.": "Nena\u0161li sa \u017eiadne akt\u00edvne zoznamy na odbavenie.",
    "November": "November",
    "Paid orders": "Zaplaten\u00e9 objedn\u00e1vky",
    "Please enter the amount the organizer can keep.": "Zadajte sumu, ktor\u00fa si organiz\u00e1tor m\u00f4\u017ee ponecha\u0165.",
    "Select a check-in list": "Vyberte zoznam na odbavenie",
    "September": "September",
    "Switch check-in list": "Prepn\u00fa\u0165 zoznam odbaven\u00ed",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Vstupenky v ko\u0161\u00edku u\u017e nie s\u00fa pre V\u00e1s rezervovan\u00e9. Objedn\u00e1vku m\u00f4\u017eete dokon\u010di\u0165, ak s\u00fa st\u00e1le k dispoz\u00edcii.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Vstupenky v ko\u0161\u00edku s\u00fa pre V\u00e1s rezervovan\u00e9 jednu min\u00fatu.",
      "Vstupenky v ko\u0161\u00edku s\u00fa pre V\u00e1s rezervovan\u00e9 {num} min\u00faty.",
      "Vstupenky v ko\u0161\u00edku s\u00fa pre V\u00e1s rezervovan\u00e9 {num} min\u00fat."
    ],
    "Ticket already used": "U\u017e pou\u017eit\u00e1 vstupenka",
    "Unknown ticket": "Nezn\u00e1ma vstupenka",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Moment\u00e1lne odosielame va\u0161u po\u017eiadavku na server. Ak to trv\u00e1 dlh\u0161ie ako jednu min\u00fatu, skontrolujte svoje internetov\u00e9 pripojenie a potom znovu na\u010d\u00edtajte t\u00fato str\u00e1nku a sk\u00faste to znova.",
    "We are processing your request \u2026": "Va\u0161u \u017eiados\u0165 spracov\u00e1vame\u2026",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Va\u0161a po\u017eiadavka pri\u0161la na server, ale st\u00e1le \u010dak\u00e1me na jej spracovanie. Ak to trv\u00e1 dlh\u0161ie ako dve min\u00faty, kontaktujte n\u00e1s alebo sa vr\u00e1\u0165te sp\u00e4\u0165 v prehliada\u010di a sk\u00faste to znova.",
    "Your request has been queued on the server and will soon be processed.": "Va\u0161a po\u017eiadavka bola zaraden\u00e1 do fronty na serveri a \u010doskoro bude spracovan\u00e1.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Va\u0161a \u017eiados\u0165 sa pr\u00e1ve spracov\u00e1va. V z\u00e1vislosti od ve\u013ekosti va\u0161ej udalosti to m\u00f4\u017ee trva\u0165 a\u017e nieko\u013eko min\u00fat.",
    "widget\u0004Back": "Sp\u00e4\u0165",
    "widget\u0004Buy": "K\u00fapi\u0165",
    "widget\u0004Choose a different date": "Vybra\u0165 in\u00fd d\u00e1tum",
    "widget\u0004Choose a different event": "Vybra\u0165 in\u00e9 podujatie",
    "widget\u0004Close": "Zatvori\u0165",
    "widget\u0004Close ticket shop": "Zatvori\u0165 obchod so vstupenkami",
    "widget\u0004Continue": "Pokra\u010dova\u0165",
    "widget\u0004Currently not available": "Moment\u00e1lne nie je k dispoz\u00edcii",
    "widget\u0004Decrease quantity": "Zn\u00ed\u017ei\u0165 po\u010det",
    "widget\u0004FREE": "ZADARMO",
    "widget\u0004Hide variants": "Skry\u0165 varianty",
    "widget\u0004Increase quantity": "Zv\u00fd\u0161i\u0165 po\u010det",
    "widget\u0004Load more": "Na\u010d\u00edta\u0165 viac",
    "widget\u0004Next month": "Nasleduj\u00faci mesiac",
    "widget\u0004Next week": "Nasleduj\u00faci t\u00fd\u017ede\u0148",
    "widget\u0004Not available anymore": "U\u017e nie je k dispoz\u00edcii",
    "widget\u0004Not yet available": "Zatia\u013e nedostupn\u00e9",
    "widget\u0004Only available with a voucher": "K dispoz\u00edcii len s pouk\u00e1\u017ekou",
    "widget\u0004Open seat selection": "Zobrazi\u0165 v\u00fdber sedadiel",
    "widget\u0004Open ticket shop": "Otvori\u0165 obchod so vstupenkami",
    "widget\u0004Previous month": "Predch\u00e1dzaj\u00faci mesiac",
    "widget\u0004Previous week": "Predch\u00e1dzaj\u00faci t\u00fd\u017ede\u0148",
    "widget\u0004Price": "Cena",
    "widget\u0004Quantity": "Po\u010det",
    "widget\u0004Redeem": "Uplatni\u0165",
    "widget\u0004Redeem a voucher": "Uplatnenie pouk\u00e1\u017eky",
    "widget\u0004Register": "Registrova\u0165 sa",
    "widget\u0004Reserved": "Rezervovan\u00e9",
    "widget\u0004Resume checkout": "Pokra\u010dova\u0165 v objedn\u00e1vke",
    "widget\u0004Select": "Vybra\u0165",
    "widget\u0004Select %s": "Vybra\u0165 %s",
    "widget\u0004Select variant %s": "Vybra\u0165 variantu %s",
    "widget\u0004Show variants": "Zobrazi\u0165 varianty",
    "widget\u0004Sold out": "Vypredan\u00e9",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Niektor\u00e9 alebo v\u0161etky kateg\u00f3rie vstupeniek s\u00fa v s\u00fa\u010dasnosti vypredan\u00e9. Ak chcete, m\u00f4\u017eete sa prida\u0165 na zoznam \u010dakate\u013eov. Budeme v\u00e1s informova\u0165, ak sa miesta uvo\u013enia.",
    "widget\u0004The cart could not be created. Please try again later": "N\u00e1kupn\u00fd ko\u0161\u00edk sa nepodarilo vytvori\u0165. Sk\u00faste to pros\u00edm nesk\u00f4r",
    "widget\u0004The ticket shop could not be loaded.": "Obchod so vstupenkami sa nepodarilo na\u010d\u00edta\u0165.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "V s\u00fa\u010dasnosti je v tomto obchode so vstupenkami ve\u013ea pou\u017e\u00edvate\u013eov. Ak chcete pokra\u010dova\u0165, otvorte obchod v novej karte.",
    "widget\u0004Voucher code": "K\u00f3d pouk\u00e1\u017eky",
    "widget\u0004Waiting list": "\u010cakac\u00ed zoznam",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Nepodarilo sa n\u00e1m vytvori\u0165 V\u00e1\u0161 n\u00e1kupn\u00fd ko\u0161\u00edk, preto\u017ee v tomto obchode je moment\u00e1lne pr\u00edli\u0161 ve\u013ea pou\u017e\u00edvate\u013eov. Kliknut\u00edm na tla\u010didlo \u201ePokra\u010dova\u0165\u201c to sk\u00faste znova v novej karte.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "V s\u00fa\u010dasnosti m\u00e1te akt\u00edvny n\u00e1kupn\u00fd ko\u0161\u00edk pre toto podujatie. Ak si vyberiete \u010fal\u0161ie vstupenky, pridaj\u00fa sa do v\u00e1\u0161ho existuj\u00faceho ko\u0161\u00edka.",
    "widget\u0004currently available: %s": "aktu\u00e1lne k dispoz\u00edcii: %s",
    "widget\u0004from %(currency)s %(price)s": "z %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "vr\u00e1tane %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "vr\u00e1tane dane",
    "widget\u0004minimum amount to order: %s": "minim\u00e1lna suma na objedn\u00e1vku: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "plus da\u0148"
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
    "DATETIME_FORMAT": "j. F Y G:i",
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
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y G:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": "\u00a0",
    "TIME_FORMAT": "G:i",
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

