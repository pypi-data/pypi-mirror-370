

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
    "(one more date)": [
      "(jeden dal\u0161\u00ed term\u00edn)",
      "({num} dal\u0161\u00ed term\u00edny)",
      "({num} dal\u0161\u00edch term\u00edn\u016f)"
    ],
    "=": "=",
    "Add condition": "P\u0159idat podm\u00ednku",
    "Additional information required": "Pot\u0159ebn\u00e9 dal\u0161\u00ed informace",
    "All": "V\u0161echny",
    "All of the conditions below (AND)": "V\u0161echny n\u00e1sleduj\u00edc\u00ed podm\u00ednky (AND)",
    "An error has occurred.": "Vyskytla se chyba.",
    "An error of type {code} occurred.": "Vyskytla se chyba {code}.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "\u010cek\u00e1 na schv\u00e1len\u00ed",
    "April": "Duben",
    "At least one of the conditions below (OR)": "Alespo\u0148 jedna z n\u00e1sleduj\u00edc\u00edch podm\u00ednek (OR)",
    "August": "Srpen",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "Oblast s QR k\u00f3dem",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "V\u00fdpo\u010det standardn\u00ed ceny\u2026",
    "Cancel": "Zru\u0161it",
    "Canceled": "Zru\u0161eno",
    "Cart expired": "N\u00e1kupn\u00ed ko\u0161\u00edk vypr\u0161el",
    "Check-in QR": "Check-in QR k\u00f3d",
    "Checked-in Tickets": "Vy\u0159\u00edzen\u00e9 vstupenky",
    "Click to close": "Kliknut\u00edm zav\u0159ete",
    "Close message": "Zav\u0159\u00edt zpr\u00e1vu",
    "Comment:": "Koment\u00e1\u0159:",
    "Confirmed": "Potvrzeno",
    "Confirming your payment \u2026": "Potvrzuji va\u0161i platbu \u2026",
    "Contacting Stripe \u2026": "Kontaktuji Stripe \u2026",
    "Contacting your bank \u2026": "Kontaktuji va\u0161i banku \u2026",
    "Continue": "Pokra\u010dovat",
    "Copied!": "Zkop\u00edrov\u00e1no!",
    "Count": "Po\u010det",
    "Credit Card": "Kreditn\u00ed karta",
    "Current date and time": "Sou\u010dasn\u00fd \u010das",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Aktu\u00e1ln\u00ed den t\u00fddne (1 = pond\u011bl\u00ed, 7 = ned\u011ble)",
    "Currently inside": "Aktu\u00e1ln\u011b uvnit\u0159",
    "December": "Prosinec",
    "Do you really want to leave the editor without saving your changes?": "Opravdu chcete opustit editor bez ulo\u017een\u00ed zm\u011bn?",
    "Duplicate": "Duplik\u00e1t",
    "Entry": "Vstup",
    "Entry not allowed": "Vstup nen\u00ed povolen",
    "Error while uploading your PDF file, please try again.": "P\u0159i nahr\u00e1v\u00e1n\u00ed souboru PDF do\u0161lo k probl\u00e9mu, zkuste to pros\u00edm znovu.",
    "Event admission": "Vstup na akci",
    "Event end": "Konec akce",
    "Event start": "Za\u010d\u00e1tek akce",
    "Exit": "V\u00fdstup",
    "Exit recorded": "Opustit nahr\u00e1van\u00e9",
    "February": "\u00danor",
    "Fr": "P\u00e1",
    "Friday": "P\u00e1tek",
    "Gate": "Br\u00e1na",
    "Generating messages \u2026": "Vytv\u00e1\u0159en\u00ed zpr\u00e1v\u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Skupina objekt\u016f",
    "Image area": "Oblast obrazu",
    "Information required": "Informace vy\u017eadov\u00e1na",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Leden",
    "July": "\u010cervenec",
    "June": "\u010derven",
    "Load more": "Na\u010d\u00edst v\u00edce",
    "March": "B\u0159ezen",
    "Marked as paid": "Ozna\u010deno jako zaplacen\u00e9",
    "Maxima": "Maxima",
    "May": "Kv\u011bten",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minuty od prvn\u00edho vstupu (-1 pro prvn\u00ed vstup)",
    "Minutes since last entry (-1 on first entry)": "Minuty od p\u0159edchoz\u00edho vstupu (-1 pro prvn\u00ed vstup)",
    "Mo": "Po",
    "Monday": "Pond\u011bl\u00ed",
    "MyBank": "MyBank",
    "No": "Ne",
    "No active check-in lists found.": "\u017d\u00e1dn\u00e9 aktivn\u00ed check-in listy.",
    "No results": "\u017d\u00e1dn\u00e9 v\u00fdsledky",
    "No tickets found": "Nenalezeny \u017e\u00e1dn\u00e9 l\u00edstky",
    "None": "\u017d\u00e1dn\u00fd",
    "November": "Listopad",
    "Number of days with a previous entry": "Po\u010det dn\u00ed bez \u00faprav",
    "Number of previous entries": "Po\u010det p\u0159edchoz\u00edch z\u00e1znam\u016f",
    "Number of previous entries since midnight": "Po\u010det z\u00e1znam\u016f od p\u016flnoci",
    "OXXO": "OXXO",
    "Object": "Objekt",
    "October": "\u0158\u00edjen",
    "Order canceled": "Objedn\u00e1vka zru\u0161ena",
    "Order not approved": "Objedn\u00e1vka nebyla potvrzena",
    "Others": "Dal\u0161\u00ed",
    "Paid orders": "Zaplacen\u00e9 objedn\u00e1vky",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "Zp\u016fsob platby nen\u00ed k dispozici",
    "Placed orders": "Zadan\u00e9 objedn\u00e1vky",
    "Please enter the amount the organizer can keep.": "Zadejte \u010d\u00e1stku, kterou si organiz\u00e1tor m\u016f\u017ee ponechat.",
    "Powered by pretix": "Poh\u00e1n\u011bno spole\u010dnost\u00ed pretix",
    "Press Ctrl-C to copy!": "Stiskn\u011bte Ctrl-C pro zkop\u00edrov\u00e1n\u00ed!",
    "Product": "Produkt",
    "Product variation": "Varianta produktu",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Uplatn\u011bno",
    "Result": "V\u00fdsledek",
    "SEPA Direct Debit": "Inkasn\u00ed p\u0159\u00edkaz SEPA",
    "SOFORT": "SOFORT",
    "Sa": "So",
    "Saturday": "Sobota",
    "Saving failed.": "Ulo\u017een\u00ed se nepoda\u0159ilo.",
    "Scan a ticket or search and press return\u2026": "Naskenujte vstupenku, nebo ji vyhledejte a zm\u00e1\u010dkn\u011bte zp\u011bt\u2026",
    "Search query": "Hledan\u00fd v\u00fdraz",
    "Search results": "Vyhledat v\u00fdsledky",
    "Select a check-in list": "Zvolte check-in list",
    "Selected only": "Pouze vybran\u00e9",
    "September": "Z\u00e1\u0159\u00ed",
    "Su": "Ne",
    "Sunday": "Ned\u011ble",
    "Switch check-in list": "Zm\u011bnit check-in list",
    "Switch direction": "Zm\u011bnit sm\u011br",
    "Th": "\u010ct",
    "The PDF background file could not be loaded for the following reason:": "Pozad\u00ed PDF nemohl b\u00fdt na\u010dten:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Produkty v n\u00e1kupn\u00edm ko\u0161\u00edku ji\u017e nejsou pro v\u00e1s rezervov\u00e1ny. Pokud je l\u00edstek st\u00e1le dostupn\u00fd, m\u016f\u017eete objedn\u00e1vku dokon\u010dit.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Produkty v n\u00e1kupn\u00edm ko\u0161\u00edku jsou pro v\u00e1s rezervov\u00e1ny na jednu minutu.",
      "Produkty v n\u00e1kupn\u00edm ko\u0161\u00edku jsou pro v\u00e1s rezervov\u00e1ny na {num} minuty.",
      "Produkty v n\u00e1kupn\u00edm ko\u0161\u00edku jsou pro v\u00e1s rezervov\u00e1ny na dal\u0161\u00edch {num} minut."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Organiz\u00e1tor si ponech\u00e1v\u00e1 %(currency)s %(amount)s",
    "The request took too long. Please try again.": "Zpracov\u00e1n\u00ed po\u017eadavku trv\u00e1 p\u0159\u00edli\u0161 dlouho. Pros\u00edm zkuste to znovu.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Vstupenka nebyla zaplacena. Chcete i p\u0159esto pokra\u010dovat?",
    "This ticket requires special attention": "Tato vstupenka vy\u017eaduje speci\u00e1ln\u00ed pozornost",
    "Thursday": "\u010ctvrtek",
    "Ticket already used": "Vstupenka ji\u017e byla pou\u017eita",
    "Ticket blocked": "Vstupenka zablokov\u00e1na",
    "Ticket code is ambiguous on list": "K\u00f3d vstupenky je v seznamu nejednozna\u010dn\u00fd",
    "Ticket code revoked/changed": "K\u00f3d vstupenky zm\u011bn\u011bn",
    "Ticket design": "Design vstupenky",
    "Ticket not paid": "Vstupenka nen\u00ed zaplacena",
    "Ticket not valid at this time": "Vstupenka je v tuto chv\u00edli neplatn\u00e1",
    "Ticket type not allowed here": "Typ vstupenky zde nen\u00ed povolen",
    "Tolerance (minutes)": "Tolerance (v minut\u00e1ch)",
    "Total": "Celkem",
    "Total revenue": "Celkov\u00e9 p\u0159\u00edjmy",
    "Trustly": "Trustly",
    "Tu": "\u00dat",
    "Tuesday": "\u00dater\u00fd",
    "Unknown error.": "Nezn\u00e1m\u00e1 chyba.",
    "Unknown ticket": "Nezn\u00e1m\u00e1 vstupenka",
    "Unpaid": "Nezaplaceno",
    "Use a different name internally": "Intern\u011b pou\u017e\u00edvat jin\u00fd n\u00e1zev",
    "Valid": "Potrvzeno",
    "Valid Tickets": "Platn\u00e9 vstupenky",
    "Valid ticket": "Platn\u00e1 vstupenka",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "St",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Pr\u00e1v\u011b odes\u00edl\u00e1me v\u00e1\u0161 po\u017eadavek na server. Pokud to trv\u00e1 d\u00e9le ne\u017e minutu, pros\u00edm zkontrolujte sv\u00e9 internetov\u00e9 p\u0159ipojen\u00ed a znovu na\u010dt\u011bte str\u00e1nku a zkuste to znovu.",
    "We are processing your request \u2026": "Zpracov\u00e1v\u00e1me v\u00e1\u0161 po\u017eadavek \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Moment\u00e1ln\u011b nem\u016f\u017eeme kontaktovat server, ale st\u00e1le se o to pokou\u0161\u00edme. Posledn\u00ed chybov\u00fd k\u00f3d: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Moment\u00e1ln\u011b nem\u016f\u017eeme kontaktovat server. Pros\u00edm zkuste to znovu. Chybov\u00fd k\u00f3d: {code}",
    "WeChat Pay": "WeChat Pay",
    "Wednesday": "St\u0159eda",
    "Yes": "Ano",
    "You get %(currency)s %(amount)s back": "Dostanete %(currency)s %(amount)s zp\u011bt",
    "You have unsaved changes!": "M\u00e1te neulo\u017een\u00e9 zm\u011bny!",
    "Your local time:": "M\u00edstn\u00ed \u010das:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "V\u00e1\u0161 po\u017eadavek byl p\u0159ijat na server, ale st\u00e1le \u010dek\u00e1me na jeho zpracov\u00e1n\u00ed. Pokud to trv\u00e1 v\u00edce jak dv\u011b minuty, pros\u00edm kontaktuje n\u00e1s nebo se vra\u0165te do va\u0161eho prohl\u00ed\u017ee\u010de a zkuste to znovu.",
    "Your request has been queued on the server and will soon be processed.": "V\u00e1\u0161 po\u017eadavek byl vlo\u017eem do fronty serveru a brzy bude zpracov\u00e1n.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "V\u00e1\u0161 po\u017eadavek je pr\u00e1v\u011b zpracov\u00e1v\u00e1n. V z\u00e1vislosti na velikosti va\u0161\u00ed udalosti, to m\u016f\u017ee trvat n\u011bkolik minut.",
    "Zimpler": "Zimpler",
    "close": "zav\u0159\u00edt",
    "custom date and time": "Pevn\u00fd term\u00edn",
    "custom time": "Pevn\u00e1 doba",
    "entry_status\u0004absent": "nep\u0159\u00edtomen",
    "entry_status\u0004present": "p\u0159\u00edtomen",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "je po",
    "is before": "je p\u0159ed",
    "is one of": "je jedn\u00edm z",
    "minutes": "minuty",
    "required": "povinn\u00fd",
    "widget\u0004Back": "Zp\u011bt",
    "widget\u0004Buy": "Koupit",
    "widget\u0004Checkout": "Checkout",
    "widget\u0004Choose a different date": "Vybrat jin\u00fd datum",
    "widget\u0004Choose a different event": "Vybrat jinou ud\u00e1lost",
    "widget\u0004Close": "Zav\u0159\u00edt",
    "widget\u0004Close ticket shop": "Zav\u0159\u00edt obchod",
    "widget\u0004Continue": "Pokra\u010dovat",
    "widget\u0004Currently not available": "Moment\u00e1ln\u011b nen\u00ed k dispozici.",
    "widget\u0004Decrease quantity": "Sn\u00ed\u017eit po\u010det",
    "widget\u0004FREE": "ZDARMA",
    "widget\u0004Hide variants": "Skr\u00fdt mo\u017enosti",
    "widget\u0004Image of %s": "Obr\u00e1zek%s",
    "widget\u0004Increase quantity": "Zv\u00fd\u0161it po\u010det",
    "widget\u0004Load more": "Na\u010d\u00edst v\u00edce",
    "widget\u0004New price: %s": "Nov\u00e1 cena: %s",
    "widget\u0004Next month": "N\u00e1sleduj\u00edc\u00ed m\u011bs\u00edc",
    "widget\u0004Next week": "P\u0159\u00ed\u0161t\u00ed t\u00fdden",
    "widget\u0004Not available anymore": "Ji\u017e nen\u00ed k dispozici",
    "widget\u0004Not yet available": "Zat\u00edm nen\u00ed k dispozici",
    "widget\u0004Only available with a voucher": "K dispozici pouze s poukazem",
    "widget\u0004Open seat selection": "Otev\u0159ete v\u00fdb\u011br sedadla",
    "widget\u0004Open ticket shop": "Obchod vstupenek otev\u0159it",
    "widget\u0004Original price: %s": "P\u016fvodn\u00ed cena: %s",
    "widget\u0004Previous month": "P\u0159edchoz\u00ed m\u011bs\u00edc",
    "widget\u0004Previous week": "P\u0159edchoz\u00ed t\u00fdden",
    "widget\u0004Price": "Cena",
    "widget\u0004Quantity": "Po\u010det",
    "widget\u0004Redeem": "Uplatnit",
    "widget\u0004Redeem a voucher": "Uplatnit pouk\u00e1zku",
    "widget\u0004Register": "Zaregistrovat",
    "widget\u0004Reserved": "Rezervov\u00e1no",
    "widget\u0004Resume checkout": "Obnovit checkout",
    "widget\u0004Select": "Vybrat",
    "widget\u0004Select %s": "Vybrat %s",
    "widget\u0004Select variant %s": "Vybrat variantu %s",
    "widget\u0004Show variants": "Zobrazit mo\u017enosti",
    "widget\u0004Sold out": "Vyprod\u00e1no",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "N\u011bkter\u00e9 nebo v\u0161echny kategorie vstupenek jsou v sou\u010dasn\u00e9 dob\u011b vyprod\u00e1ny. Pokud chcete, m\u016f\u017eete se p\u0159idat na \u010dekac\u00ed listinu. Pot\u00e9 v\u00e1s budeme informovat, pokud budou m\u00edsta op\u011bt voln\u00e1.",
    "widget\u0004The cart could not be created. Please try again later": "N\u00e1kupn\u00ed ko\u0161\u00edk se nepoda\u0159ilo vytvo\u0159it. Zkuste to pros\u00edm znovu",
    "widget\u0004The ticket shop could not be loaded.": "Obchod vstupenek nemohl b\u00fdt na\u010dten.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "V sou\u010dasn\u00e9 dob\u011b je v tomto obchod\u011b s vstupenkami mnoho u\u017eivatel\u016f. Otev\u0159ete pros\u00edm obchod v nov\u00e9 kart\u011b.",
    "widget\u0004Voucher code": "K\u00f3d pouk\u00e1zky",
    "widget\u0004Waiting list": "\u010cekac\u00ed listina",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "V\u00e1\u0161 ko\u0161\u00edk se nepoda\u0159ilo vytvo\u0159it, proto\u017ee v tomto obchod\u011b je v sou\u010dasn\u00e9 dob\u011b mnoho u\u017eivatel\u016f. Klikn\u011bte pros\u00edm na \"Pokra\u010dovat\" a zkuste to znovu na nov\u00e9 kart\u011b.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "V sou\u010dasn\u00e9 dob\u011b m\u00e1te aktivn\u00ed ko\u0161\u00edk pro tuto ud\u00e1lost. Pokud vyberete dal\u0161\u00ed produkty, budou p\u0159id\u00e1ny do va\u0161eho ko\u0161\u00edku.",
    "widget\u0004currently available: %s": "aktu\u00e1ln\u011b k dispozici: %s",
    "widget\u0004from %(currency)s %(price)s": "od %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "v\u010detn\u011b %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "v\u010detn\u011b dan\u00ed",
    "widget\u0004minimum amount to order: %s": "minim\u00e1ln\u00ed mno\u017estv\u00ed pro objedn\u00e1vku: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "plus dan\u011b"
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
    "DATETIME_FORMAT": "j. E Y G:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H.%M",
      "%d.%m.%Y %H:%M",
      "%d. %m. %Y %H:%M:%S",
      "%d. %m. %Y %H:%M:%S.%f",
      "%d. %m. %Y %H.%M",
      "%d. %m. %Y %H:%M",
      "%Y-%m-%d %H.%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. E Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%d. %m. %Y",
      "%d. %m. %y",
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
      "%H.%M",
      "%H:%M",
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

