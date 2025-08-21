

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
      "(satu kencan lagi)"
    ],
    "Add condition": "Tambahkan kondisi",
    "Additional information required": "Informasi tambahan diperlukan",
    "All": "Semua",
    "All of the conditions below (AND)": "Semua kondisi di bawah (DAN)",
    "An error has occurred.": "Sebuah kesalahan telah terjadi.",
    "An error of type {code} occurred.": "Terjadi kesalahan jenis {code}.",
    "Apple Pay": "Apple Pay",
    "At least one of the conditions below (OR)": "Setidaknya salah satu kondisi di bawah ini (ATAU)",
    "August": "Agustus",
    "BLIK": "berkedip",
    "Bancontact": "Bancontact",
    "Barcode area": "Area kode batang",
    "Calculating default price\u2026": "Menghitung harga default\u2026",
    "Cancel": "Membatalkan",
    "Canceled": "Dibatalkan",
    "Cart expired": "Keranjang sudah habis masa berlakunya",
    "Check-in QR": "QR masuk",
    "Checked-in Tickets": "Tiket Check-in",
    "Click to close": "Klik untuk menutup",
    "Close message": "Tutup pesan",
    "Comment:": "Komentar:",
    "Confirming your payment \u2026": "Mengonfirmasi pembayaran Anda\u2026",
    "Contacting Stripe \u2026": "Menghubungi Stripe\u2026",
    "Contacting your bank \u2026": "Menghubungi bank Anda\u2026",
    "Continue": "Lanjutkan",
    "Copied!": "Disalin!",
    "Count": "Menghitung",
    "Credit Card": "Kartu Kredit",
    "Current date and time": "Tanggal dan waktu saat ini",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Hari saat ini dalam seminggu (1 = Senin, 7 = Minggu)",
    "Currently inside": "Saat ini di dalam",
    "December": "Desember",
    "Do you really want to leave the editor without saving your changes?": "Apakah Anda benar-benar ingin keluar dari editor tanpa menyimpan perubahan?",
    "Duplicate": "Duplikat",
    "Entry": "Pintu Masuk",
    "Entry not allowed": "Masuk tidak diperbolehkan",
    "Error while uploading your PDF file, please try again.": "Terjadi kesalahan saat mengunggah file PDF Anda, coba lagi.",
    "Event admission": "Tiket masuk acara",
    "Event end": "Acara berakhir",
    "Event start": "Acara dimulai",
    "Exit": "Pintu Keluar",
    "Exit recorded": "Keluar direkam",
    "February": "Februari",
    "Fr": "Pdt",
    "Generating messages \u2026": "Menghasilkan pesan\u2026",
    "Google Pay": "Google Bayar",
    "Group of objects": "Sekelompok objek",
    "Image area": "Daerah gambar",
    "Information required": "Informasi dibutuhkan",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Januari",
    "July": "Juli",
    "June": "Juni",
    "Load more": "Muat lebih banyak",
    "March": "Berbaris",
    "Marked as paid": "Sudah terbayar",
    "Maxima": "maksimal",
    "May": "Mungkin",
    "Mercado Pago": "Pasar Pago",
    "Minutes since first entry (-1 on first entry)": "Menit sejak entri pertama (-1 pada entri pertama)",
    "Minutes since last entry (-1 on first entry)": "Menit sejak entri terakhir (-1 pada entri pertama)",
    "No": "Tidak",
    "No active check-in lists found.": "Tidak ditemukan daftar check-in aktif.",
    "No tickets found": "Tidak ada tiket yang ditemukan",
    "None": "Tidak ada",
    "Number of days with a previous entry": "Jumlah hari dengan entri sebelumnya",
    "Number of previous entries": "Jumlah entri sebelumnya",
    "Number of previous entries since midnight": "Jumlah entri sebelumnya sejak tengah malam",
    "OXXO": "OKXO",
    "Object": "Obyek",
    "October": "Oktober",
    "Order canceled": "Pesanan dibatalkan",
    "Others": "Yang lain",
    "Paid orders": "Pesanan terbayar",
    "PayPal": "PayPal",
    "PayPal Credit": "Kredit PayPal",
    "PayPal Pay Later": "Pay Later PayPal",
    "PayU": "pembayaran",
    "Payment method unavailable": "Metode pembayaran tidak tersedia",
    "Placed orders": "Pesanan yang ditempatkan",
    "Please enter the amount the organizer can keep.": "Silakan masukkan jumlah yang dapat disimpan oleh penyelenggara.",
    "Powered by pretix": "Didukung oleh pretix",
    "Press Ctrl-C to copy!": "Tekan Ctrl-C untuk menyalin!",
    "Product": "Produk",
    "Product variation": "Variasi produk",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Ditebus",
    "Result": "Hasil",
    "SEPA Direct Debit": "Debit Langsung SEPA",
    "SOFORT": "SOFORT",
    "Saving failed.": "Gagal menyimpan.",
    "Scan a ticket or search and press return\u2026": "Pindai tiket atau cari dan tekan kembali\u2026",
    "Search query": "Permintaan pencarian",
    "Search results": "Hasil Pencarian",
    "Select a check-in list": "Pilih daftar check-in",
    "Selected only": "Hanya dipilih",
    "Switch check-in list": "Ganti daftar check-in",
    "Switch direction": "Beralih arah",
    "The PDF background file could not be loaded for the following reason:": "File latar belakang PDF tidak dapat dimuat karena alasan berikut:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Item di keranjang Anda tidak lagi disediakan untuk Anda. Anda masih dapat menyelesaikan pesanan Anda selama masih tersedia.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Item di keranjang Anda direservasi untuk Anda selama {num} menit."
    ],
    "The organizer keeps %(currency)s %(amount)s": "Penyelenggara menyimpan %(currency)s %(amount)s",
    "The request took too long. Please try again.": "Permintaan terlalu lama. Silakan coba lagi.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Tiket ini belum dibayar. Apakah Anda ingin melanjutkannya?",
    "This ticket requires special attention": "Tiket ini memerlukan perhatian khusus",
    "Ticket already used": "Tiket sudah digunakan",
    "Ticket blocked": "Tiket diblokir",
    "Ticket code is ambiguous on list": "Kode tiket dalam daftar tidak jelas",
    "Ticket code revoked/changed": "Kode tiket dicabut/diubah",
    "Ticket design": "Desain tiket",
    "Ticket not paid": "Tiket tidak dibayar",
    "Ticket not valid at this time": "Tiket tidak berlaku saat ini",
    "Ticket type not allowed here": "Jenis tiket tidak diperbolehkan di sini",
    "Tolerance (minutes)": "Toleransi (menit)",
    "Total": "Total",
    "Total revenue": "Total pendapatan",
    "Trustly": "Dapat dipercaya",
    "Tu": "kamu",
    "Unknown error.": "Kesalahan yang tidak diketahui.",
    "Unknown ticket": "Tiket tidak dikenal",
    "Unpaid": "Tidak dibayar",
    "Use a different name internally": "Gunakan nama yang berbeda secara internal",
    "Valid": "Sah",
    "Valid Tickets": "Tiket yang Sah",
    "Valid ticket": "Tiket sah",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Kami",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Kami sedang mengirimkan permintaan Anda ke server. Jika ini memakan waktu lebih dari satu menit, silakan periksa koneksi internet Anda lalu muat ulang halaman ini dan coba lagi.",
    "We are processing your request \u2026": "Kami sedang memproses permintaan Anda \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Saat ini kami tidak dapat menjangkau server, tetapi kami terus mencoba. Kode kesalahan terakhir: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Saat ini kami tidak dapat menjangkau server. Silakan coba lagi. Kode kesalahan: {code}",
    "WeChat Pay": "Pembayaran WeChat",
    "Yes": "Iya",
    "You get %(currency)s %(amount)s back": "Anda mendapatkan %(currency)s %(amount)s kembali",
    "You have unsaved changes!": "Anda memiliki perubahan yang belum disimpan!",
    "Your local time:": "Waktu setempat Anda:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Permintaan Anda sudah sampai di server tetapi kami masih menunggu untuk diproses. Jika proses ini memerlukan waktu lebih dari dua menit, harap hubungi kami atau kembali ke browser Anda dan coba lagi.",
    "Your request has been queued on the server and will soon be processed.": "Permintaan Anda telah dimasukkan ke dalam antrian di server dan akan segera diproses.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Permintaan Anda sedang diproses. Tergantung pada besarnya acara Anda, proses ini mungkin memerlukan waktu hingga beberapa menit.",
    "close": "menutup",
    "custom date and time": "tanggal dan waktu khusus",
    "custom time": "waktu khusus",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "setelahnya",
    "is before": "adalah sebelumnya",
    "is one of": "adalah salah satu dari",
    "minutes": "menit",
    "required": "diperlukan",
    "widget\u0004Back": "Kembali",
    "widget\u0004Buy": "Membeli",
    "widget\u0004Choose a different date": "Pilih tanggal yang berbeda",
    "widget\u0004Choose a different event": "Pilih acara lain",
    "widget\u0004Close": "Menutup",
    "widget\u0004Close ticket shop": "Tutup toko tiket",
    "widget\u0004Continue": "Melanjutkan",
    "widget\u0004Decrease quantity": "Kurangi kuantitas",
    "widget\u0004FREE": "BEBAS",
    "widget\u0004Increase quantity": "Tingkatkan kuantitas",
    "widget\u0004Load more": "Muat lebih banyak",
    "widget\u0004Next month": "Bulan depan",
    "widget\u0004Next week": "Minggu depan",
    "widget\u0004Only available with a voucher": "Hanya tersedia dengan voucher",
    "widget\u0004Open seat selection": "Pemilihan kursi terbuka",
    "widget\u0004Open ticket shop": "Buka toko tiket",
    "widget\u0004Previous month": "Bulan sebelumnya",
    "widget\u0004Previous week": "Minggu sebelumnya",
    "widget\u0004Price": "Harga",
    "widget\u0004Quantity": "Kuantitas",
    "widget\u0004Redeem": "Menukarkan",
    "widget\u0004Redeem a voucher": "Tukarkan voucher",
    "widget\u0004Register": "Daftar",
    "widget\u0004Reserved": "Disimpan",
    "widget\u0004Resume checkout": "Lanjutkan pembayaran",
    "widget\u0004Select %s": "Pilih %s",
    "widget\u0004Select variant %s": "Pilih varian %s",
    "widget\u0004Sold out": "Terjual habis",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Beberapa atau semua kategori tiket saat ini terjual habis. Jika mau, Anda dapat menambahkan diri Anda ke daftar tunggu. Kami kemudian akan memberi tahu jika kursi tersedia lagi.",
    "widget\u0004The cart could not be created. Please try again later": "Keranjang tidak dapat dibuat. Silakan coba lagi nanti",
    "widget\u0004The ticket shop could not be loaded.": "Toko tiket tidak dapat dimuat.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Saat ini ada banyak sekali pengguna di toko tiket ini. Silakan buka toko di tab baru untuk melanjutkan.",
    "widget\u0004Voucher code": "Kode Voucher",
    "widget\u0004Waiting list": "Daftar tunggu",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Kami tidak dapat membuat keranjang Anda, karena saat ini terdapat terlalu banyak pengguna di toko tiket ini. Silakan klik \"Lanjutkan\" untuk mencoba lagi di tab baru.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Saat ini Anda memiliki keranjang aktif untuk acara ini. Jika Anda memilih lebih banyak produk, produk tersebut akan ditambahkan ke keranjang Anda yang sudah ada.",
    "widget\u0004currently available: %s": "tersedia saat ini: %s",
    "widget\u0004from %(currency)s %(price)s": "dari %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "termasuk. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "termasuk. pajak",
    "widget\u0004minimum amount to order: %s": "jumlah minimum untuk memesan: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "ditambah %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "ditambah pajak"
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
    "DATETIME_FORMAT": "j N Y, G.i",
    "DATETIME_INPUT_FORMATS": [
      "%d-%m-%Y %H.%M.%S",
      "%d-%m-%Y %H.%M.%S.%f",
      "%d-%m-%Y %H.%M",
      "%d-%m-%y %H.%M.%S",
      "%d-%m-%y %H.%M.%S.%f",
      "%d-%m-%y %H.%M",
      "%m/%d/%y %H.%M.%S",
      "%m/%d/%y %H.%M.%S.%f",
      "%m/%d/%y %H.%M",
      "%m/%d/%Y %H.%M.%S",
      "%m/%d/%Y %H.%M.%S.%f",
      "%m/%d/%Y %H.%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j N Y",
    "DATE_INPUT_FORMATS": [
      "%d-%m-%Y",
      "%d/%m/%Y",
      "%d-%m-%y",
      "%d/%m/%y",
      "%d %b %Y",
      "%d %B %Y",
      "%m/%d/%y",
      "%m/%d/%Y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d-m-Y G.i",
    "SHORT_DATE_FORMAT": "d-m-Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "G.i",
    "TIME_INPUT_FORMATS": [
      "%H.%M.%S",
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

