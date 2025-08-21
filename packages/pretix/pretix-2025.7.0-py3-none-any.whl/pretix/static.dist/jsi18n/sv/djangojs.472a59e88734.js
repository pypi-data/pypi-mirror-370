

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
      "(ytterligare ett datum)",
      "({num} fler datum)"
    ],
    "Add condition": "L\u00e4gg till villkor",
    "Additional information required": "Ytterligare information kr\u00e4vs",
    "All": "Alla",
    "All of the conditions below (AND)": "Alla villkor nedan (AND)",
    "An error has occurred.": "Ett fel har uppst\u00e5tt.",
    "An error of type {code} occurred.": "Ett fel av typ {code} har h\u00e4nt.",
    "Apple Pay": "Apple Pay",
    "April": "April",
    "At least one of the conditions below (OR)": "Minst ett av villkoren nedan (OR)",
    "August": "Augusti",
    "Bancontact": "Bancontact",
    "Barcode area": "QR-kod-omr\u00e5de",
    "Calculating default price\u2026": "Kalkylerar standardpris\u2026",
    "Cancel": "Avbryt",
    "Canceled": "Avbokad",
    "Cart expired": "Varukorgen har g\u00e5tt ut",
    "Check-in QR": "QR-kod f\u00f6r att Checka in",
    "Checked-in Tickets": "Incheckade biljetter",
    "Click to close": "Klicka f\u00f6r att st\u00e4nga",
    "Close message": "St\u00e4ng meddelande",
    "Comment:": "Kommentar:",
    "Confirming your payment \u2026": "Bekr\u00e4ftar din betalning \u2026",
    "Contacting Stripe \u2026": "Kontaktar Stripe \u2026",
    "Contacting your bank \u2026": "Kontaktar din bank \u2026",
    "Continue": "Forts\u00e4tt",
    "Copied!": "Kopierat!",
    "Count": "Antal",
    "Credit Card": "Kreditkort",
    "Current date and time": "Aktuellt datum och tid",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Aktuell veckodag (1 = M\u00e5ndag, 7 = S\u00f6ndag)",
    "Current entry status": "Aktuell intr\u00e4desstatus",
    "Currently inside": "F\u00f6r tillf\u00e4llet n\u00e4rvarande",
    "December": "December",
    "Do you really want to leave the editor without saving your changes?": "Vill du verkligen l\u00e4mna editorn utan att spara dina \u00e4ndringar?",
    "Duplicate": "Duplicera",
    "Enter page number between 1 and %(max)s.": "Ange sidnummer mellan 1 och %(max)s.",
    "Entry": "Ing\u00e5ng",
    "Entry not allowed": "Intr\u00e4de \u00e4r inte till\u00e5tet",
    "Error while uploading your PDF file, please try again.": "Ett fel uppstod n\u00e4r du laddade upp din PDF-fil, v\u00e4nligen f\u00f6rs\u00f6k igen.",
    "Event admission": "Tilltr\u00e4de till evenemang",
    "Event end": "Evenemanget slutar",
    "Event start": "Evenemanget b\u00f6rjar",
    "Exit": "Utg\u00e5ng",
    "Exit recorded": "Utg\u00e5ng har registrerats",
    "February": "Februari",
    "Fr": "Fr",
    "Gate": "Port",
    "Generating messages \u2026": "Skapar meddelanden \u2026",
    "Group of objects": "Grupp av objekt",
    "Image area": "Bildomr\u00e5de",
    "Information required": "Information kr\u00e4vs",
    "Invalid page number.": "Ogiltigt sidnummer.",
    "January": "Januari",
    "July": "Juli",
    "June": "Juni",
    "Load more": "Ladda mer",
    "March": "Mars",
    "Marked as paid": "Markera som betald",
    "May": "Maj",
    "Minutes since first entry (-1 on first entry)": "Minuter sedan senaste posten (-1 vid f\u00f6rsta posten)",
    "Minutes since last entry (-1 on first entry)": "Minuter sedan senaste posten (-1 vid f\u00f6rsta posten)",
    "Mo": "M\u00e5",
    "MyBank": "MyBank",
    "No": "Nej",
    "No active check-in lists found.": "Inga aktiva incheckningslistor hittades.",
    "No tickets found": "Inga biljetter hittades",
    "None": "Ingen",
    "November": "November",
    "Number of days with a previous entry": "Antal dagar med en tidigare postning",
    "Number of previous entries": "Antal tidigare poster",
    "Number of previous entries since midnight": "Antal tidigare poster sedan midnatt",
    "Object": "Objekt",
    "October": "Oktober",
    "Order canceled": "Best\u00e4llningen har avbokats",
    "Order not approved": "Best\u00e4llning ej godk\u00e4nd",
    "Others": "\u00d6vriga",
    "Paid orders": "Betalade best\u00e4llningar",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal kredit",
    "PayPal Pay Later": "PayPal betala senare",
    "Payment method unavailable": "Betalningsmetod ej tillg\u00e4nglig",
    "Placed orders": "Lagda best\u00e4llningar",
    "Please enter the amount the organizer can keep.": "V\u00e4nligen ange det belopp som arrang\u00f6ren kan beh\u00e5lla.",
    "Powered by pretix": "Drivs av pretix",
    "Press Ctrl-C to copy!": "Tryck Ctrl-C f\u00f6r att kopiera!",
    "Product": "Produkt",
    "Product variation": "Produktvarianter",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Inl\u00f6st",
    "Result": "Resultat",
    "SEPA Direct Debit": "SEPA autogiro",
    "SOFORT": "SOFORT",
    "Sa": "L\u00f6",
    "Saving failed.": "Misslyckades att spara.",
    "Scan a ticket or search and press return\u2026": "Skanna en biljett eller s\u00f6k och tryck p\u00e5 enter\u2026",
    "Search query": "S\u00f6kterm",
    "Search results": "S\u00f6kresultat",
    "Select a check-in list": "V\u00e4lj en incheckningslista",
    "Selected only": "Endast valda",
    "September": "September",
    "Su": "S\u00f6",
    "Switch check-in list": "Byt incheckningslista",
    "Switch direction": "Byt riktning",
    "Th": "To",
    "The PDF background file could not be loaded for the following reason:": "Bakgrunds-filen till PDFen kunde inte laddas av f\u00f6ljande orsak:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Varorna i din varukorg \u00e4r inte l\u00e4ngre reserverade f\u00f6r dig. Du kan dock genomf\u00f6ra din order s\u00e5 l\u00e4nge varorna fortfarande \u00e4r tillg\u00e4ngliga.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Produkterna i din bokning \u00e4r reserverade f\u00f6r dig i en minut.",
      "Produkterna i din bokning \u00e4r reserverade f\u00f6r dig i {num} minuter."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Arrang\u00f6ren beh\u00e5ller %(amount)s %(currency)s",
    "The request took too long. Please try again.": "F\u00f6rfr\u00e5gan tog f\u00f6r l\u00e5ng tid. V\u00e4nligen f\u00f6rs\u00f6k igen.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Biljetten \u00e4r \u00e4nnu inte betald. Vill du \u00e4nd\u00e5 forts\u00e4tta?",
    "This ticket requires special attention": "Denna biljett kr\u00e4ver s\u00e4rskild uppm\u00e4rksamhet",
    "Ticket already used": "Biljetten har redan anv\u00e4nts",
    "Ticket code revoked/changed": "Biljettkoden har sp\u00e4rrats/\u00e4ndrats",
    "Ticket design": "Biljettdesign",
    "Ticket not paid": "Biljetten \u00e4r inte betald",
    "Ticket type not allowed here": "Biljettypen g\u00e4ller ej h\u00e4r",
    "Tolerance (minutes)": "Tolerans (minuter)",
    "Total": "Totalt",
    "Total revenue": "Totalt",
    "Tu": "Ti",
    "Unknown error.": "Ok\u00e4nt fel.",
    "Unknown ticket": "Ok\u00e4nd biljett",
    "Unpaid": "Obetald",
    "Use a different name internally": "Anv\u00e4nd ett annat namn internt",
    "Valid": "Giltig",
    "Valid Tickets": "Giltiga biljetter",
    "Valid ticket": "Giltig biljett",
    "Venmo": "Venmo",
    "We": "On",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Vi skickar din f\u00f6rfr\u00e5gan till servern. Om det tar mer \u00e4n en minut, kontrollera din internetanslutning och ladda sedan den h\u00e4r sidan och f\u00f6rs\u00f6k igen.",
    "We are processing your request \u2026": "Vi behandlar din f\u00f6rfr\u00e5gan \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Just nu kan vi inte n\u00e5 servern, men vi forts\u00e4tter att f\u00f6rs\u00f6ka. Senaste felkoden var: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Just nu kan vi inte n\u00e5 servern. V\u00e4nligen f\u00f6rs\u00f6k igen. Felkod: {code}",
    "WeChat Pay": "WeChat Pay",
    "Yes": "Ja",
    "You get %(currency)s %(amount)s back": "Du f\u00e5r %(amount)s %(currency)s tillbaka",
    "You have unsaved changes!": "Du har osparade \u00e4ndringar!",
    "Your local time:": "Din lokala tid:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Din f\u00f6rfr\u00e5gan har n\u00e5tt servern, men vi v\u00e4ntar fortfarande p\u00e5 att den ska behandlas. Om det tar mer \u00e4n tv\u00e5 minuter, v\u00e4nligen kontakta oss eller g\u00e5 tillbaka i din webbl\u00e4sare och f\u00f6rs\u00f6k igen.",
    "Your request has been queued on the server and will soon be processed.": "Din beg\u00e4ran har k\u00f6ats p\u00e5 servern och kommer snart att behandlas.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Din beg\u00e4ran behandlas f\u00f6r n\u00e4rvarande. Beroende p\u00e5 storleken p\u00e5 ditt event kan det ta upp till n\u00e5gra minuter.",
    "close": "st\u00e4ng",
    "custom date and time": "anpassat datum och tid",
    "custom time": "anpassad tid",
    "entry_status\u0004absent": "Fr\u00e5nvarande",
    "entry_status\u0004present": "N\u00e4rvarande",
    "giropay": "giropay",
    "is after": "\u00e4r efter",
    "is before": "\u00e4r f\u00f6re",
    "is one of": "\u00e4r en av",
    "minutes": "minuter",
    "required": "obligatorisk",
    "widget\u0004Back": "Tillbaka",
    "widget\u0004Buy": "K\u00f6p",
    "widget\u0004Choose a different date": "V\u00e4lj ett annat datum",
    "widget\u0004Choose a different event": "V\u00e4lj ett annat event",
    "widget\u0004Close": "St\u00e4ng",
    "widget\u0004Close ticket shop": "St\u00e4ng biljettshop",
    "widget\u0004Continue": "Forts\u00e4tt",
    "widget\u0004Decrease quantity": "Minska m\u00e4ngden",
    "widget\u0004FREE": "ANTAL",
    "widget\u0004Increase quantity": "\u00d6ka m\u00e4ngden",
    "widget\u0004Load more": "Ladda mer",
    "widget\u0004Next month": "N\u00e4sta m\u00e5nad",
    "widget\u0004Next week": "N\u00e4sta vecka",
    "widget\u0004Not available anymore": "Inte l\u00e4ngre tillg\u00e4nglig",
    "widget\u0004Only available with a voucher": "Bara tillg\u00e4nglig med en kupong",
    "widget\u0004Open seat selection": "Ingen platsbokning",
    "widget\u0004Open ticket shop": "\u00d6ppna biljettbutik",
    "widget\u0004Previous month": "F\u00f6reg\u00e5ende m\u00e5nad",
    "widget\u0004Previous week": "F\u00f6reg\u00e5ende vecka",
    "widget\u0004Price": "Pris",
    "widget\u0004Quantity": "Kvantitet",
    "widget\u0004Redeem": "L\u00f6s in",
    "widget\u0004Redeem a voucher": "L\u00f6s in kupong",
    "widget\u0004Register": "BOKA",
    "widget\u0004Reserved": "Reserverad",
    "widget\u0004Resume checkout": "Forts\u00e4tt med ditt bokningen",
    "widget\u0004Sold out": "Sluts\u00e5lt",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Vissa eller alla biljettkategorier \u00e4r f\u00f6r n\u00e4rvarande sluts\u00e5lda. Om du vill kan du l\u00e4gga till dig sj\u00e4lv p\u00e5 v\u00e4ntelistan. Vi meddelar d\u00e5 om platser finns tillg\u00e4ngliga igen.",
    "widget\u0004The cart could not be created. Please try again later": "Bokningen kunde inte skapas. V\u00e4nligen f\u00f6rs\u00f6k senare.",
    "widget\u0004The ticket shop could not be loaded.": "Biljettshoppen kunde inte laddas.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Biljettbutiken anv\u00e4nds just nu av m\u00e5nga. V\u00e4nligen \u00f6ppna butiken i en ny flik f\u00f6r att forts\u00e4tta.",
    "widget\u0004Voucher code": "Kupongkod",
    "widget\u0004Waiting list": "V\u00e4ntelista",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Vi kunde inte skapa din bokning, d\u00e5 det just nu \u00e4r m\u00e5nga anv\u00e4ndare i den h\u00e4r biljettbutiken. Klicka p\u00e5 \"Forts\u00e4tt\" f\u00f6r att f\u00f6rs\u00f6ka p\u00e5 nytt i en ny flik.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Du har f\u00f6r tillf\u00e4llet en p\u00e5g\u00e5ende bokning f\u00f6r den h\u00e4r eventet. Om du v\u00e4ljer fler produkter, kommer de att l\u00e4ggas till din befintliga bokning.",
    "widget\u0004currently available: %s": "nu tillg\u00e4ngliga: %s",
    "widget\u0004from %(currency)s %(price)s": "fr\u00e5n %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "inkl. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "inkl. skatter",
    "widget\u0004minimum amount to order: %s": "min. antal f\u00f6r att best\u00e4lla: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "exkl. %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "exkl. skatter"
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
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "Y-m-d H:i",
    "SHORT_DATE_FORMAT": "Y-m-d",
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

