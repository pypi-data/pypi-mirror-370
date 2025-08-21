

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = (n == 1) ? 0 : ((n == 2) ? 1 : ((n > 10 && n % 10 == 0) ? 2 : 3));
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "Additional information required": "\u05de\u05d9\u05d3\u05e2 \u05e0\u05d5\u05e1\u05e3",
    "An error of type {code} occurred.": "\u05e9\u05d2\u05d9\u05d0\u05d4 {code} \u05d4\u05ea\u05e8\u05d7\u05e9\u05d4.",
    "Cancel": "\u05d1\u05d8\u05dc",
    "Canceled": "\u05d1\u05d5\u05d8\u05dc",
    "Comment:": "\u05ea\u05d2\u05d5\u05d1\u05d4:",
    "Confirming your payment \u2026": "\u05de\u05d0\u05de\u05ea \u05d0\u05ea \u05d4\u05ea\u05e9\u05dc\u05d5\u05dd \u05e9\u05dc\u05da\u2026",
    "Contacting your bank \u2026": "\u05d9\u05d5\u05e6\u05e8 \u05e7\u05e9\u05e8 \u05e2\u05dd \u05d4\u05d1\u05e0\u05e7 \u05e9\u05dc\u05da\u2026",
    "Continue": "\u05d4\u05de\u05e9\u05da",
    "Entry": "\u05db\u05e0\u05d9\u05e1\u05d4",
    "Exit": "\u05d9\u05e6\u05d9\u05d0\u05d4",
    "Load more": "\u05d8\u05e2\u05df \u05e2\u05d5\u05d3",
    "Marked as paid": "\u05e1\u05d5\u05de\u05df \u05db\u05e9\u05d5\u05dc\u05dd",
    "No tickets found": "\u05dc\u05d0 \u05e0\u05de\u05e6\u05d0\u05d5 \u05db\u05e8\u05d8\u05d9\u05e1\u05d9\u05dd",
    "Order canceled": "\u05d4\u05d6\u05de\u05e0\u05d4 \u05d1\u05d5\u05d8\u05dc\u05d4",
    "Paid orders": "\u05d4\u05d6\u05de\u05e0\u05d5\u05ea \u05e9\u05e9\u05d5\u05dc\u05de\u05d5",
    "Placed orders": "\u05d4\u05d6\u05de\u05e0\u05d5\u05ea \u05e9\u05d1\u05d5\u05e6\u05e2\u05d5",
    "Result": "\u05ea\u05d5\u05e6\u05d0\u05d5\u05ea",
    "Scan a ticket or search and press return\u2026": "\u05e1\u05e8\u05d5\u05e7 \u05db\u05e8\u05d8\u05d9\u05e1 \u05d0\u05d5 \u05d7\u05e4\u05e9\u2026",
    "Search results": "\u05d7\u05d9\u05e4\u05d5\u05e9",
    "The request took too long. Please try again.": "\u05d4\u05d1\u05e7\u05e9\u05d4 \u05dc\u05e7\u05d7\u05d4 \u05d9\u05d5\u05ea\u05e8 \u05de\u05d9\u05d3\u05d9 \u05d6\u05de\u05df. \u05e0\u05e1\u05d4 \u05e9\u05e0\u05d9\u05ea.",
    "This ticket is not yet paid. Do you want to continue anyways?": "\u05d4\u05db\u05e8\u05d8\u05d9\u05e1 \u05e2\u05d3\u05d9\u05d9\u05df \u05dc\u05d0 \u05e9\u05d5\u05dc\u05dd. \u05e8\u05d5\u05e6\u05d4 \u05dc\u05d4\u05de\u05e9\u05d9\u05da \u05d1\u05db\u05dc \u05d6\u05d0\u05ea?",
    "Ticket not paid": "\u05db\u05e8\u05d8\u05d9\u05e1 \u05dc\u05d0 \u05e9\u05d5\u05dc\u05dd",
    "Total": "\u05e1\u05d4\"\u05db",
    "Total revenue": "\u05d4\u05db\u05e0\u05e1\u05d4 \u05db\u05d5\u05dc\u05dc\u05ea",
    "Unknown ticket": "\u05db\u05e8\u05d8\u05d9\u05e1 \u05dc\u05d0 \u05de\u05d6\u05d5\u05d4\u05d4",
    "Unpaid": "\u05dc\u05d0 \u05e9\u05d5\u05dc\u05dd",
    "Valid": "\u05ea\u05e7\u05e3",
    "Valid Tickets": "\u05db\u05e8\u05d8\u05d9\u05e1\u05d9\u05dd \u05ea\u05e7\u05e4\u05d9\u05dd",
    "Valid ticket": "\u05db\u05e8\u05d8\u05d9\u05e1 \u05ea\u05e7\u05e3",
    "We are processing your request \u2026": "\u05d4\u05d1\u05e7\u05e9\u05d4 \u05e9\u05dc\u05da \u05de\u05ea\u05d1\u05e6\u05e2\u05ea\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "\u05d0\u05e0\u05d7\u05e0\u05d5 \u05dc\u05d0 \u05de\u05e6\u05dc\u05d9\u05d7\u05d9\u05dd \u05dc\u05d2\u05e9\u05ea \u05dc\u05e9\u05e8\u05ea, \u05d0\u05d1\u05dc \u05de\u05de\u05e9\u05d9\u05db\u05d9\u05dd \u05dc\u05e0\u05e1\u05d5\u05ea. \u05e9\u05d2\u05d9\u05d0\u05d4 \u05d0\u05d7\u05e8\u05d5\u05e0\u05d4: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "\u05d0\u05d9\u05e8\u05e2\u05d4 \u05e9\u05d2\u05d9\u05d0\u05d4. \u05d0\u05e0\u05d0 \u05e0\u05e1\u05d4 \u05e9\u05e0\u05d9\u05ea. \u05e9\u05d2\u05d9\u05d0\u05d4: {code}",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "\u05d4\u05d1\u05e7\u05e9\u05d4 \u05e9\u05dc\u05da \u05d4\u05d2\u05d9\u05e2\u05d4 \u05dc\u05e9\u05e8\u05ea \u05d0\u05d1\u05dc \u05e2\u05d3\u05d9\u05d9\u05df \u05dc\u05d0 \u05d4\u05ea\u05d7\u05d9\u05dc\u05d4. \u05d0\u05dd \u05d6\u05d4 \u05dc\u05d5\u05e7\u05d7 \u05d9\u05d5\u05ea\u05e8 \u05de\u05e9\u05ea\u05d9 \u05d3\u05e7\u05d5\u05ea, \u05d0\u05e0\u05d0 \u05e6\u05d5\u05e8 \u05d0\u05d9\u05ea\u05e0\u05d5 \u05e7\u05e9\u05e8 \u05d0\u05d5 \u05e0\u05e1\u05d4 \u05e9\u05e0\u05d9\u05ea.",
    "Your request has been queued on the server and will soon be processed.": "\u05d4\u05d1\u05e7\u05e9\u05d4 \u05e9\u05dc\u05da \u05ea\u05d1\u05d5\u05e6\u05e2 \u05d1\u05d4\u05e7\u05d3\u05dd.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "\u05d4\u05d1\u05e7\u05e9\u05d4 \u05e9\u05dc\u05da \u05de\u05ea\u05d1\u05e6\u05e2\u05ea \u05d5\u05d9\u05db\u05d5\u05dc\u05d4 \u05dc\u05e7\u05d7\u05ea \u05db\u05de\u05d4 \u05d3\u05e7\u05d5\u05ea \u05d1\u05d4\u05ea\u05d0\u05dd \u05dc\u05d2\u05d5\u05d3\u05dc \u05d4\u05d0\u05d9\u05e8\u05d5\u05e2."
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
    "DATETIME_FORMAT": "j \u05d1F Y H:i",
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
    "DATE_FORMAT": "j \u05d1F Y",
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
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "j \u05d1F",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "d/m/Y H:i",
    "SHORT_DATE_FORMAT": "d/m/Y",
    "THOUSAND_SEPARATOR": ",",
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

