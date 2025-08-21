

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = 0;
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
      "(\u4e00\u4e2a\u4ee5\u4e0a\u65e5\u671f)"
    ],
    "Additional information required": "\u9700\u8981\u63d0\u4f9b\u66f4\u591a\u4fe1\u606f",
    "All": "\u6240\u6709",
    "An error has occurred.": "\u53d1\u751f\u4e00\u4e2a\u9519\u8bef\u3002",
    "An error of type {code} occurred.": "\u53d1\u751f\u7c7b\u578b\u4e3a{code}\u7684\u9519\u8bef\u3002",
    "April": "\u56db\u6708",
    "August": "\u516b\u6708",
    "Barcode area": "\u6761\u7801\u533a",
    "Cancel": "\u53d6\u6d88",
    "Canceled": "\u5df2\u88ab\u53d6\u6d88",
    "Cart expired": "\u8d2d\u7269\u8f66\u5df2\u8fc7\u671f",
    "Check-in QR": "\u7b7e\u5230QR\u7801",
    "Checked-in Tickets": "\u5df2\u7b7e\u5230\u7684\u7968",
    "Click to close": "\u70b9\u6b64\u5173\u95ed",
    "Close message": "\u5173\u95ed\u6d88\u606f",
    "Comment:": "\u6ce8\u91ca:",
    "Confirming your payment \u2026": "\u6b63\u5728\u786e\u8ba4\u60a8\u7684\u4ed8\u6b3e\u2026",
    "Contacting Stripe \u2026": "\u6b63\u5728\u8054\u7cfbStripe \u2026",
    "Contacting your bank \u2026": "\u6b63\u5728\u8054\u7cfb\u60a8\u7684\u94f6\u884c \u2026",
    "Copied!": "\u5df2\u590d\u5236!",
    "Count": "\u6570\u91cf",
    "December": "\u5341\u4e8c\u6708",
    "Do you really want to leave the editor without saving your changes?": "\u4f60\u771f\u7684\u60f3\u79bb\u5f00\u7f16\u8f91\u5668\u800c\u4e0d\u4fdd\u5b58\u4f60\u7684\u66f4\u6539\u5417?",
    "Error while uploading your PDF file, please try again.": "\u4e0a\u4f20PDF\u6587\u4ef6\u65f6\u51fa\u9519\uff0c\u8bf7\u91cd\u8bd5\u3002",
    "February": "\u4e8c\u6708",
    "Fr": "\u5468\u4e94",
    "Generating messages \u2026": "\u751f\u6210\u6d88\u606f\u2026",
    "Group of objects": "\u5bf9\u8c61\u7ec4",
    "January": "\u4e00\u6708",
    "July": "\u4e03\u6708",
    "June": "\u516d\u6708",
    "Load more": "\u52a0\u8f7d\u66f4\u591a",
    "March": "\u4e09\u6708",
    "Marked as paid": "\u6807\u4e3a\u5df2\u4ed8\u6b3e",
    "May": "\u4e94\u6708",
    "Mo": "\u5468\u4e00",
    "No": "\u5426",
    "No active check-in lists found.": "\u672a\u627e\u5230\u6d3b\u52a8\u7684\u7b7e\u5230\u5217\u8868\u3002",
    "No tickets found": "\u627e\u4e0d\u5230\u7968",
    "None": "\u65e0",
    "November": "\u5341\u4e00\u6708",
    "Object": "\u5bf9\u8c61",
    "October": "\u5341\u6708",
    "Order canceled": "\u8ba2\u5355\u5df2\u7ecf\u53d6\u6d88",
    "Others": "\u5176\u4ed6",
    "Paid orders": "\u5df2\u4ed8\u6b3e\u8ba2\u5355",
    "Placed orders": "\u63d0\u4ea4\u7684\u8ba2\u5355",
    "Powered by pretix": "\u7531pretix\u9a71\u52a8",
    "Press Ctrl-C to copy!": "\u6309Ctrl-C\u590d\u5236!",
    "Product variation": "\u4ea7\u54c1\u53d8\u5316",
    "Result": "\u7ed3\u679c",
    "Sa": "\u5468\u516d",
    "Saving failed.": "\u4fdd\u5b58\u5931\u8d25.",
    "Scan a ticket or search and press return\u2026": "\u626b\u63cf\u4e00\u5f20\u7968\u6216\u641c\u7d22\u7136\u540e\u6309\u8fd4\u56de\u2026",
    "Search results": "\u641c\u7d22\u7ed3\u679c",
    "September": "\u4e5d\u6708",
    "Su": "\u5468\u5929",
    "Switch check-in list": "\u5207\u6362\u7b7e\u5230\u5217\u8868",
    "Th": "\u5468\u56db",
    "The PDF background file could not be loaded for the following reason:": "\u7531\u4e8e\u4ee5\u4e0b\u539f\u56e0\u65e0\u6cd5\u52a0\u8f7dPDF\u80cc\u666f\u6587\u4ef6:",
    "This ticket is not yet paid. Do you want to continue anyways?": "\u8fd9\u5f20\u7968\u5c1a\u672a\u652f\u4ed8\u3002\u65e0\u8bba\u5982\u4f55\u4f60\u90fd\u8981\u7ee7\u7eed\u5417\uff1f",
    "This ticket requires special attention": "\u8fd9\u5f20\u7968\u9700\u8981\u7279\u522b\u6ce8\u610f",
    "Ticket already used": "\u7968\u5df2\u7ecf\u88ab\u4f7f\u7528\u8fc7",
    "Ticket design": "\u95e8\u7968\u8bbe\u8ba1",
    "Ticket not paid": "\u7968\u672a\u652f\u4ed8",
    "Ticket type not allowed here": "\u4e0d\u5141\u8bb8\u7684\u7968\u7c7b\u578b",
    "Total": "\u603b\u8ba1",
    "Total revenue": "\u603b\u6536\u5165",
    "Tu": "\u5468\u4e8c",
    "Unknown error.": "\u672a\u77e5\u9519\u8bef\u3002",
    "Unknown ticket": "\u672a\u77e5\u7684\u7968\u3002",
    "Unpaid": "\u672a\u652f\u4ed8",
    "Use a different name internally": "\u5728\u5185\u90e8\u4f7f\u7528\u4e00\u4e2a\u4e0d\u540c\u7684\u540d\u79f0",
    "Valid Tickets": "\u6709\u6548\u7684\u7968",
    "Valid ticket": "\u6709\u6548\u7684\u7968",
    "We": "\u5468\u4e09",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "\u6211\u4eec\u6b63\u5728\u5c06\u60a8\u7684\u8bf7\u6c42\u53d1\u9001\u5230\u670d\u52a1\u5668\u3002\u5982\u679c\u8d85\u8fc7\u4e00\u5206\u949f\uff0c\u8bf7\u68c0\u67e5\u60a8\u7684\u4e92\u8054\u7f51\u8fde\u63a5\uff0c\u7136\u540e\u5237\u65b0\u6b64\u9875\u9762\uff0c\u5e76\u91cd\u8bd5\u3002",
    "We are processing your request \u2026": "\u6211\u4eec\u6b63\u5728\u5904\u7406\u4f60\u7684\u8bf7\u6c42\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "\u6211\u4eec\u76ee\u524d\u65e0\u6cd5\u8fde\u63a5\u5230\u670d\u52a1\u5668\uff0c\u4f46\u6211\u4eec\u4e00\u76f4\u5728\u5c1d\u8bd5\u3002\u6700\u540e\u7684\u9519\u8bef\u4ee3\u7801\u4e3a:{code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "\u6211\u4eec\u76ee\u524d\u65e0\u6cd5\u8fde\u63a5\u5230\u670d\u52a1\u5668\u3002\u8bf7\u518d\u8bd5\u4e00\u6b21\u3002\u9519\u8bef\u4ee3\u7801\u4e3a:{code}",
    "Yes": "\u662f",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "\u60a8\u7684\u8bf7\u6c42\u5df2\u63d0\u4ea4\u5230\u670d\u52a1\u5668\uff0c\u4f46\u4ecd\u5728\u7b49\u5f85\u5904\u7406\u3002\u5982\u679c\u7b49\u5f85\u8d85\u8fc7\u4e24\u5206\u949f\uff0c\u8bf7\u4e0e\u6211\u4eec\u8054\u7cfb\u6216\u8fd4\u56de\u60a8\u7684\u6d4f\u89c8\u5668\u518d\u8bd5\u4e00\u6b21\u3002",
    "Your request has been queued on the server and will soon be processed.": "\u60a8\u7684\u8bf7\u6c42\u5df2\u7ecf\u5728\u670d\u52a1\u5668\u4e0a\u6392\u961f\uff0c\u5f88\u5feb\u4f1a\u88ab\u5904\u7406\u3002",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "\u60a8\u7684\u8bf7\u6c42\u5f53\u524d\u6b63\u5728\u5904\u7406\u4e2d\u3002\u6839\u636e\u6d3b\u52a8\u89c4\u6a21\uff0c\u8fd9\u53ef\u80fd\u9700\u8981\u51e0\u5206\u949f\u7684\u65f6\u95f4\u3002",
    "widget\u0004Back": "\u540e\u9000",
    "widget\u0004Buy": "\u8d2d\u4e70",
    "widget\u0004Choose a different event": "\u9009\u62e9\u4e00\u4e2a\u4e0d\u540c\u7684\u6d3b\u52a8",
    "widget\u0004Close": "\u5173\u95ed",
    "widget\u0004Close ticket shop": "\u5173\u95ed\u552e\u7968",
    "widget\u0004Continue": "\u7ee7\u7eed",
    "widget\u0004FREE": "\u514d\u8d39",
    "widget\u0004Next month": "\u4e0b\u4e2a\u6708",
    "widget\u0004Only available with a voucher": "\u53ea\u80fd\u51ed\u5238\u8d2d\u4e70",
    "widget\u0004Previous month": "\u4e0a\u4e2a\u6708",
    "widget\u0004Redeem": "\u5151\u6362",
    "widget\u0004Redeem a voucher": "\u5151\u6362\u4f18\u60e0\u5238",
    "widget\u0004Reserved": "\u4fdd\u7559",
    "widget\u0004Resume checkout": "\u7ee7\u7eed\u7ed3\u8d26",
    "widget\u0004Sold out": "\u5df2\u552e\u7a7a",
    "widget\u0004The cart could not be created. Please try again later": "\u65e0\u6cd5\u521b\u5efa\u8d2d\u7269\u8f66\u3002\u8bf7\u7a0d\u540e\u518d\u8bd5",
    "widget\u0004The ticket shop could not be loaded.": "\u65e0\u6cd5\u52a0\u8f7d\u552e\u7968\u5385\u3002",
    "widget\u0004Voucher code": "\u4f18\u60e0\u5238\u4ee3\u7801",
    "widget\u0004Waiting list": "\u5019\u8865\u5217\u8868",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "\u60a8\u5f53\u524d\u6709\u4e00\u4e2a\u672c\u6b21\u6d3b\u52a8\u7684\u8d2d\u7269\u8f66\u3002\u5982\u679c\u60a8\u9009\u62e9\u66f4\u591a\u7684\u4ea7\u54c1\uff0c\u5b83\u4eec\u5c06\u88ab\u6dfb\u52a0\u5230\u60a8\u73b0\u6709\u7684\u8d2d\u7269\u8f66\u4e2d\u3002",
    "widget\u0004currently available: %s": "\u5f53\u524d\u53ef\u7528: %s",
    "widget\u0004from %(currency)s %(price)s": "\u7531 %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "\u5305\u542b %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "\u5305\u542b\u7a0e",
    "widget\u0004minimum amount to order: %s": "\u6700\u4f4e\u8ba2\u8d2d\u91cf: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "\u53e6\u52a0 %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "\u7a0e"
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
    "DATETIME_FORMAT": "Y\u5e74n\u6708j\u65e5 H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y/%m/%d %H:%M",
      "%Y-%m-%d %H:%M",
      "%Y\u5e74%n\u6708%j\u65e5 %H:%M",
      "%Y/%m/%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S",
      "%Y\u5e74%n\u6708%j\u65e5 %H:%M:%S",
      "%Y/%m/%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y\u5e74%n\u6708%j\u65e5 %H:%n:%S.%f",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "Y\u5e74n\u6708j\u65e5",
    "DATE_INPUT_FORMATS": [
      "%Y/%m/%d",
      "%Y-%m-%d",
      "%Y\u5e74%n\u6708%j\u65e5"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "m\u6708j\u65e5",
    "NUMBER_GROUPING": 4,
    "SHORT_DATETIME_FORMAT": "Y\u5e74n\u6708j\u65e5 H:i",
    "SHORT_DATE_FORMAT": "Y\u5e74n\u6708j\u65e5",
    "THOUSAND_SEPARATOR": "",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M",
      "%H:%M:%S",
      "%H:%M:%S.%f"
    ],
    "YEAR_MONTH_FORMAT": "Y\u5e74n\u6708"
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

