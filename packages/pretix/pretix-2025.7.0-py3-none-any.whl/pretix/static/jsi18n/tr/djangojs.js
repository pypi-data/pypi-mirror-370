

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
      "Bir\n(Bir ba\u015fka tarih)",
      "Di\u011fer\n({num} daha fazla tarih)"
    ],
    "All": "Her\u015fey",
    "An error has occurred.": "Bir hata olu\u015ftu.",
    "An error of type {code} occurred.": "{Code} t\u00fcr\u00fcnde bir hata olu\u015ftu.",
    "Barcode area": "Barkod alan\u0131",
    "Cart expired": "Sepetinizin s\u00fcresi doldu",
    "Check-in QR": "Giri\u015f QR",
    "Close message": "Mesaj\u0131 kapat",
    "Comment:": "Yorum:",
    "Contacting Stripe \u2026": "\u0130leti\u015fim Hatt\u0131 \u2026",
    "Copied!": "Kopyalanan!",
    "Count": "Saymak",
    "Do you really want to leave the editor without saving your changes?": "De\u011fi\u015fiklikleri kaydetmeden edit\u00f6rden ger\u00e7ekten ayr\u0131lmak istiyor musunuz?",
    "Error while uploading your PDF file, please try again.": "PDF dosyan\u0131z\u0131 y\u00fcklerken hata olu\u015ftu, l\u00fctfen tekrar deneyin.",
    "Generating messages \u2026": "Mesaj olu\u015fturuluyor\u2026",
    "Group of objects": "Nesne grubu",
    "Marked as paid": "\u00d6denmi\u015f olarak i\u015faretlendi",
    "None": "Hi\u00e7biri",
    "Object": "Nesne",
    "Others": "Di\u011ferleri",
    "Paid orders": "\u00dccretli sipari\u015fler",
    "Placed orders": "Verilen sipari\u015fler",
    "Powered by pretix": "Pretix taraf\u0131ndan desteklenmektedir",
    "Press Ctrl-C to copy!": "Kopyalamak i\u00e7in Ctrl-C tu\u015flar\u0131na bas\u0131n!",
    "Przelewy24": "Przelewy24 (Polonya \u00d6deme Y\u00f6ntemi)",
    "Saving failed.": "Kaydetme ba\u015far\u0131s\u0131z oldu.",
    "The PDF background file could not be loaded for the following reason:": "PDF arka plan dosyas\u0131 a\u015fa\u011f\u0131daki nedenden dolay\u0131 y\u00fcklenemedi:",
    "Ticket design": "Bilet tasar\u0131m\u0131",
    "Ticket type not allowed here": "Burada bilet t\u00fcr\u00fcne izin verilmiyor",
    "Total": "Toplam",
    "Total revenue": "Toplam gelir",
    "Unknown error.": "Bilinmeyen hata.",
    "Use a different name internally": "Dahili olarak farkl\u0131 bir ad kullan",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "\u015eu anda iste\u011finizi sunucuya g\u00f6nderiyoruz. Bu i\u015flem bir dakikadan uzun s\u00fcrerse, l\u00fctfen \u0130nternet ba\u011flant\u0131n\u0131z\u0131 kontrol edin ve ard\u0131ndan bu sayfay\u0131 tekrar y\u00fckleyin ve tekrar deneyin.",
    "We are processing your request \u2026": "\u0130ste\u011finizi i\u015fliyoruz\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "\u015eu anda sunucuya ula\u015fam\u0131yoruz, ancak denemeye devam ediyoruz. Son hata kodu: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "\u015eu anda sunucuya ula\u015fam\u0131yoruz. L\u00fctfen tekrar deneyin. Hata kodu: {code}",
    "widget\u0004Buy": "Sat\u0131n al",
    "widget\u0004Close": "Kapal\u0131",
    "widget\u0004Close ticket shop": "Bilet d\u00fckkan\u0131n\u0131 kapat",
    "widget\u0004Continue": "Devam et",
    "widget\u0004FREE": "\u00dccretsiz",
    "widget\u0004Only available with a voucher": "Sadece bir kupon ile kullan\u0131labilir",
    "widget\u0004Redeem": "\u00d6demek",
    "widget\u0004Redeem a voucher": "Bir kupon kullan",
    "widget\u0004Reserved": "Ayr\u0131lm\u0131\u015f",
    "widget\u0004Resume checkout": "\u00d6deme i\u015flemine devam et",
    "widget\u0004Select variant %s": "%s varyant\u0131n\u0131 se\u00e7in",
    "widget\u0004Sold out": "Sat\u0131ld\u0131",
    "widget\u0004The cart could not be created. Please try again later": "Sepet olu\u015fturulamad\u0131. L\u00fctfen daha sonra tekrar deneyiniz",
    "widget\u0004The ticket shop could not be loaded.": "Bilet ma\u011fazas\u0131 y\u00fcklenemedi.",
    "widget\u0004Voucher code": "Kupon kodu",
    "widget\u0004Waiting list": "Bekleme listesi",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "\u015eu anda bu etkinlik i\u00e7in aktif bir sepetiniz var. Daha fazla \u00fcr\u00fcn se\u00e7erseniz, mevcut sepetinize eklenir.",
    "widget\u0004currently available: %s": "\u015fu anda mevcut: %s",
    "widget\u0004from %(currency)s %(price)s": "% (para birimi) s% (fiyat) s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "dahil %(rate)s% %(taxname)s",
    "widget\u0004minimum amount to order: %s": "sipari\u015f i\u00e7in minimum miktar: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "art\u0131 %(rate)s% %(taxname)s"
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
    "DATETIME_FORMAT": "d F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "d F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "d F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d M Y H:i",
    "SHORT_DATE_FORMAT": "d M Y",
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

