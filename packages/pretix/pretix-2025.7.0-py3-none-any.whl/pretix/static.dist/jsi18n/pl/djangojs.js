

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
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
      "(jedna data wi\u0119cej)",
      "({num} daty wi\u0119cej)",
      "({num} dat wi\u0119cej)"
    ],
    "=": "=",
    "Add condition": "Dodaj warunek",
    "Additional information required": "Wymagane dodatkowe informacje",
    "All": "Zaznacz wszystko",
    "All of the conditions below (AND)": "Wszystkie poni\u017csze warunki (AND)",
    "An error has occurred.": "Wyst\u0105pi\u0142 b\u0142\u0105d.",
    "An error of type {code} occurred.": "Wyst\u0105pi\u0142 b\u0142\u0105d typu {code}.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "Zatwierdzenie w toku",
    "April": "Kwiecie\u0144",
    "At least one of the conditions below (OR)": "Co najmniej jeden z poni\u017cszych warunk\u00f3w (OR)",
    "August": "Sierpie\u0144",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "Miejsce na kod kreskowy",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Liczenie domy\u015blnej ceny\u2026",
    "Cancel": "Anuluj",
    "Canceled": "Anulowany",
    "Cart expired": "Koszyk wygas\u0142",
    "Check-in QR": "QR zameldowania",
    "Checked-in Tickets": "Zameldowane bilety",
    "Click to close": "Zamknij",
    "Close message": "Zamkni\u0119cie wiadomo\u015bci",
    "Comment:": "Komentarz:",
    "Confirmed": "Potwierdzono",
    "Confirming your payment \u2026": "Potwierdzanie p\u0142atno\u015bci\u2026",
    "Contacting Stripe \u2026": "Kontaktowanie Stripe\u2026",
    "Contacting your bank \u2026": "\u0141\u0105czenie z bankiem\u2026",
    "Continue": "Kontynuuj",
    "Copied!": "Skopiowano!",
    "Count": "Ilo\u015b\u0107",
    "Credit Card": "Karta kredytowa",
    "Current date and time": "Obecna data i godzina",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Bie\u017c\u0105cy dzie\u0144 tygodnia (1 = Poniedzia\u0142ek, 7 = Niedziela)",
    "Current entry status": "Bie\u017c\u0105cy status wpisu",
    "Currently inside": "Obecnie w \u015brodku",
    "December": "Grudzie\u0144",
    "Do you really want to leave the editor without saving your changes?": "Czy na pewno opu\u015bci\u0107 edytor bez zapisania zmian?",
    "Duplicate": "Duplikuj",
    "Enter page number between 1 and %(max)s.": "Wprowad\u017a numer strony mi\u0119dzy 1 a %(max)s.",
    "Entry": "Wej\u015bcie",
    "Entry not allowed": "Wej\u015bcie niedozwolone",
    "Error while uploading your PDF file, please try again.": "B\u0142\u0105d uploadu pliku PDF, prosimy spr\u00f3bowa\u0107 ponownie.",
    "Event admission": "Wst\u0119p na wydarzenie",
    "Event end": "Koniec wydarzenia",
    "Event start": "Rozpocz\u0119cie wydarzenia",
    "Exit": "Wyj\u015bcie",
    "Exit recorded": "Wyj\u015bcie zarejestrowane",
    "February": "Luty",
    "Fr": "Pt",
    "Gate": "Bramka",
    "Generating messages \u2026": "Generowanie wiadomo\u015bci\u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Grupa obiekt\u00f3w",
    "Image area": "Obszar obrazu",
    "Information required": "Wymagane informacje",
    "Invalid page number.": "Niepoprawny numer strony.",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Stycze\u0144",
    "July": "Lipiec",
    "June": "Czerwiec",
    "Load more": "Za\u0142aduj wi\u0119cej",
    "March": "Marzec",
    "Marked as paid": "Oznaczono jako zap\u0142acone",
    "Maxima": "Maxima",
    "May": "Maj",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minuty od pierwszego wej\u015bcia (-1 przy pierwszym wej\u015bciu)",
    "Minutes since last entry (-1 on first entry)": "Minuty od ostatniego wej\u015bcia (-1 przy pierwszym wej\u015bciu)",
    "Mo": "Pn",
    "MyBank": "MyBank",
    "No": "Nie",
    "No active check-in lists found.": "Nie znaleziono aktywnych list odpraw.",
    "No results": "Brak wynik\u00f3w",
    "No tickets found": "Nie znaleziono bilet\u00f3w",
    "None": "Odznacz wszystko",
    "November": "Listopad",
    "Number of days with a previous entry": "Liczba dni z poprzednimi wej\u015bciami",
    "Number of days with a previous entry before": "Liczba dni z poprzednimi wej\u015bciami przed",
    "Number of days with a previous entry since": "Liczba dni z poprzednimi wej\u015bciami od",
    "Number of previous entries": "Liczba poprzednich wej\u015b\u0107",
    "Number of previous entries before": "Liczba poprzednich wej\u015b\u0107 po",
    "Number of previous entries since": "Liczba poprzednich wej\u015b\u0107 od",
    "Number of previous entries since midnight": "Liczba poprzednich wej\u015b\u0107 od p\u00f3\u0142nocy",
    "OXXO": "OXXO",
    "Object": "Obiekt",
    "October": "Pa\u017adziernik",
    "Order canceled": "Zam\u00f3wienie anulowane",
    "Order not approved": "Zam\u00f3wienie niezaakceptowane",
    "Others": "Inne",
    "Paid orders": "Op\u0142acone zam\u00f3wienia",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Zap\u0142a\u0107 P\u00f3\u017aniej",
    "PayU": "PayU",
    "Payment method unavailable": "Metoda p\u0142atno\u015bci niedost\u0119pna",
    "Placed orders": "Z\u0142o\u017cone zam\u00f3wienia",
    "Please enter the amount the organizer can keep.": "Wprowad\u017a kwot\u0119, kt\u00f3r\u0105 organizator mo\u017ce zachowa\u0107.",
    "Powered by pretix": "Wygenerowane przez pretix",
    "Press Ctrl-C to copy!": "Wci\u015bnij Ctrl-C \u017ceby skopiowa\u0107!",
    "Product": "Produkt",
    "Product variation": "Wariant produktu",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Wykorzystany",
    "Result": "Wynik",
    "SEPA Direct Debit": "SEPA Direct Debit",
    "SOFORT": "SOFORT",
    "Sa": "So",
    "Saving failed.": "B\u0142\u0105d zapisu.",
    "Scan a ticket or search and press return\u2026": "Zeskanuj bilet lub wyszukaj i naci\u015bnij powr\u00f3t\u2026",
    "Search query": "Wyszukiwana fraza",
    "Search results": "Wyniki wyszukiwania",
    "Select a check-in list": "Wybierz list\u0119 odprawy",
    "Selected only": "Tylko wybrane",
    "September": "Wrzesie\u0144",
    "Su": "Nd",
    "Switch check-in list": "Wymie\u0144 list\u0119 odpraw",
    "Switch direction": "Kierunek zmiany",
    "Text box": "Pole tekstowe",
    "Text object (deprecated)": "Obiekt tekstowy (przestarza\u0142y)",
    "Th": "Cz",
    "The PDF background file could not be loaded for the following reason:": "B\u0142\u0105d \u0142adowania pliku PDF t\u0142a:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Przedmioty w koszyku nie s\u0105 ju\u017c zarezerwowane. Nadal mo\u017cesz doko\u0144czy\u0107 zam\u00f3wienie, je\u017celi produkty s\u0105 jeszcze dost\u0119pne.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Przedmioty w koszyku s\u0105 zarezerwowane na jedn\u0105\u00a0minut\u0119.",
      "Przedmioty w koszyku s\u0105 zarezerwowane na {num}\u00a0minuty.",
      "Przedmioty w koszyku s\u0105 zarezerwowane na {num}\u00a0minut."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Organizator zatrzymuje %(amount)s %(currency)s",
    "The request took too long. Please try again.": "Procesowanie \u017c\u0105dania trwa\u0142o zbyt d\u0142ugo. Prosz\u0119 spr\u00f3buj ponownie.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Ten bilet nie jest jeszcze op\u0142acony. Czy chcesz kontynuowa\u0107 pomimo tego?",
    "This ticket requires special attention": "Ten bilet wymaga szczeg\u00f3lnej uwagi",
    "Ticket already used": "Bilet ju\u017c u\u017cyty",
    "Ticket blocked": "Bilet zablokowany",
    "Ticket code is ambiguous on list": "Kod biletu jest niejednoznaczny na li\u015bcie",
    "Ticket code revoked/changed": "Kod biletu cofni\u0119ty/zmieniony",
    "Ticket design": "Projekt biletu",
    "Ticket not paid": "Bilet nieop\u0142acony",
    "Ticket not valid at this time": "Bilet nie jest obecnie wa\u017cny",
    "Ticket type not allowed here": "Typ biletu niedozwolony tutaj",
    "Tolerance (minutes)": "Tolerancja (minuty)",
    "Total": "Razem",
    "Total revenue": "Ca\u0142kowity doch\u00f3d",
    "Trustly": "Trustly",
    "Tu": "Wt",
    "Unknown error.": "Nieznany b\u0142\u0105d.",
    "Unknown ticket": "Bilet nieznany",
    "Unpaid": "Niezap\u0142acony",
    "Use a different name internally": "U\u017cyj innej nazwy wewn\u0119trznie",
    "Valid": "Wa\u017cny",
    "Valid Tickets": "Wa\u017cne bilety",
    "Valid ticket": "Wa\u017cny bilet",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "\u015ar",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Zapytanie jest przesy\u0142ane do serwera. W przypadku czasu oczekiwania d\u0142u\u017cszego ni\u017c minuta prosimy o sprawdzenie \u0142\u0105czno\u015bci z Internetem a nast\u0119pnie o prze\u0142adowanie strony i ponowienie\u00a0pr\u00f3by.",
    "We are processing your request \u2026": "Zapytanie jest przetwarzane\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "B\u0142\u0105d komunikacji z serwerem, aplikacja ponowi pr\u00f3b\u0119. Ostatni kod b\u0142\u0119du: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "B\u0142\u0105d komunikacji z serwerem. Prosimy spr\u00f3bowa\u0107\u00a0ponownie. Kod b\u0142\u0119du: {code}",
    "WeChat Pay": "WeChat Pay",
    "Yes": "Tak",
    "You get %(currency)s %(amount)s back": "Otrzymasz %(amount)s %(currency)s z powrotem",
    "You have unsaved changes!": "Masz niezapisane zmiany!",
    "Your local time:": "Tw\u00f3j czas lokalny:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Zapytanie zosta\u0142o dotar\u0142o do serwera ale jest wci\u0105\u017c\u00a0przetwarzane. W przypadku czasu oczekiwania d\u0142u\u017cszego ni\u017c dwie minuty prosimy o kontakt lub o cofni\u0119cie si\u0119 w przegl\u0105darce i ponowienie pr\u00f3by.",
    "Your request has been queued on the server and will soon be processed.": "Twoje \u017c\u0105danie zosta\u0142o ustawione w kolejce na serwerze i wkr\u00f3tce zostanie przetworzone.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Twoje \u017c\u0105danie jest obecnie przetwarzane. W zale\u017cno\u015bci od wielko\u015bci wydarzenia, mo\u017ce to potrwa\u0107 do kilku minut.",
    "Zimpler": "Zimpler",
    "close": "zamkn\u0105\u0107",
    "custom date and time": "Niestandardowa data i godzina",
    "custom time": "czas niestandardowy",
    "entry_status\u0004absent": "nieobecny",
    "entry_status\u0004present": "obecny",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "jest p\u00f3\u017aniej",
    "is before": "jest wcze\u015bniej",
    "is one of": "jest jednym z",
    "minutes": "minut",
    "required": "wymagane",
    "widget\u0004Back": "Wstecz",
    "widget\u0004Buy": "Kup",
    "widget\u0004Choose a different date": "Wybierz inn\u0105 dat\u0119",
    "widget\u0004Choose a different event": "Wybierz inne wydarzenie",
    "widget\u0004Close": "Zamkn\u0105\u0107",
    "widget\u0004Close ticket shop": "Zamkni\u0119cie sklepu biletowego",
    "widget\u0004Continue": "Dalej",
    "widget\u0004Currently not available": "Obecnie niedost\u0119pne",
    "widget\u0004Decrease quantity": "Zmniejszy\u0107 ilo\u015b\u0107",
    "widget\u0004FREE": "DARMOWE",
    "widget\u0004Hide variants": "Ukryj warianty",
    "widget\u0004Image of %s": "Obrazek %s",
    "widget\u0004Increase quantity": "Zwi\u0119kszy\u0107 ilo\u015b\u0107",
    "widget\u0004Load more": "Za\u0142aduj wi\u0119cej",
    "widget\u0004New price: %s": "Nowa cena: %s",
    "widget\u0004Next month": "Przysz\u0142y miesi\u0105c",
    "widget\u0004Next week": "W przysz\u0142ym tygodniu",
    "widget\u0004Not available anymore": "Ju\u017c niedost\u0119pny",
    "widget\u0004Not yet available": "Jeszcze niedost\u0119pne",
    "widget\u0004Only available with a voucher": "Dost\u0119pne tylko z voucherem",
    "widget\u0004Open seat selection": "Otw\u00f3rz wyb\u00f3r miejsca",
    "widget\u0004Open ticket shop": "Otwarty sklep z biletami",
    "widget\u0004Original price: %s": "Oryginalna cena: %s",
    "widget\u0004Previous month": "Zesz\u0142y miesi\u0105c",
    "widget\u0004Previous week": "Poprzedni tydzie\u0144",
    "widget\u0004Price": "Cena",
    "widget\u0004Quantity": "Ilo\u015b\u0107",
    "widget\u0004Redeem": "U\u017cyj",
    "widget\u0004Redeem a voucher": "U\u017cyj vouchera",
    "widget\u0004Register": "Rejestracja",
    "widget\u0004Reserved": "Zarezerwowane",
    "widget\u0004Resume checkout": "Powr\u00f3t do kasy",
    "widget\u0004Select": "Wybierz",
    "widget\u0004Select %s": "Wybierz %s",
    "widget\u0004Select variant %s": "Wybierz wariant %s",
    "widget\u0004Show variants": "Poka\u017c warianty",
    "widget\u0004Sold out": "Wyprzedane",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Niekt\u00f3re lub wszystkie kategorie bilet\u00f3w s\u0105 obecnie wyprzedane. Je\u015bli chcesz to mo\u017cesz doda\u0107 si\u0119 do listy oczekuj\u0105cych. Powiadomimy Ci\u0119 gdy miejsca b\u0119d\u0105 dost\u0119pne ponownie.",
    "widget\u0004The cart could not be created. Please try again later": "B\u0142\u0105d tworzenia koszyka. Prosimy\u00a0spr\u00f3bowa\u0107\u00a0ponownie p\u00f3\u017aniej",
    "widget\u0004The ticket shop could not be loaded.": "B\u0142\u0105d \u0142\u0105dowania sklepu biletowego.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Obecnie w tym sklepie biletowym jest wielu u\u017cytkownik\u00f3w. Otw\u00f3rz sklep w nowej zak\u0142adce by kontynuowa\u0107.",
    "widget\u0004Voucher code": "Kod vouchera",
    "widget\u0004Waiting list": "Lista oczekiwania",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Nie mogli\u015bmy stworzy\u0107 twojego koszyka, poniewa\u017c obecnie jest zbyt wielu u\u017cytkownik\u00f3w w tym sklepie. Kliknij \"Kontynuuj\", aby spr\u00f3bowa\u0107\u00a0ponownie w nowej karcie.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Istnieje aktywny w\u00f3zek dla tego wydarzenia. Wyb\u00f3r kolejnych produkt\u00f3w spowoduje dodanie ich do istniej\u0105cego w\u00f3zka.",
    "widget\u0004currently available: %s": "obecnie dost\u0119pne: %s",
    "widget\u0004from %(currency)s %(price)s": "od %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "w tym %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "w tym podatki",
    "widget\u0004minimum amount to order: %s": "minimalna ilo\u015b\u0107 zam\u00f3wienia: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "netto"
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
    "DATETIME_FORMAT": "j E Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j E Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j E",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d-m-Y  H:i",
    "SHORT_DATE_FORMAT": "d-m-Y",
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

