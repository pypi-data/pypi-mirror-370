

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
      "({num} \u4ed6\u306e\u65e5\u7a0b)"
    ],
    "=": "=",
    "Add condition": "\u6761\u4ef6\u3092\u8ffd\u52a0",
    "Additional information required": "\u8ffd\u52a0\u60c5\u5831\u304c\u5fc5\u8981\u3067\u3059",
    "All": "\u5168\u3066",
    "All of the conditions below (AND)": "\u4ee5\u4e0b\u5168\u3066\u306e\u6761\u4ef6\uff08\u3068\uff09",
    "An error has occurred.": "\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002",
    "An error of type {code} occurred.": "{code} \u306e\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002",
    "Apple Pay": "Apple Pay",
    "Approval pending": "\u627f\u8a8d\u4fdd\u7559\u4e2d",
    "April": "\uff14\u6708",
    "At least one of the conditions below (OR)": "\u4ee5\u4e0b\u306e\u6761\u4ef6\u306e\u3046\u3061\u3001\u6700\u4f4e\uff11\u3064\uff08\u307e\u305f\u306f\uff09",
    "August": "\uff18\u6708",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "\u30d0\u30fc\u30b3\u30fc\u30c9\u30a8\u30ea\u30a2",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "\u30c7\u30d5\u30a9\u30eb\u30c8\u306e\u6599\u91d1\u3092\u8a08\u7b97\u4e2d\u2026",
    "Cancel": "\u30ad\u30e3\u30f3\u30bb\u30eb",
    "Canceled": "\u30ad\u30e3\u30f3\u30bb\u30eb\u6e08\u307f",
    "Cart expired": "\u30ab\u30fc\u30c8\u306e\u6709\u52b9\u671f\u9650\u304c\u5207\u308c\u3066\u3044\u307e\u3059",
    "Check-in QR": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u7528QR\u30b3\u30fc\u30c9",
    "Checked-in Tickets": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u6e08\u307f\u306e\u30c1\u30b1\u30c3\u30c8",
    "Click to close": "\u30af\u30ea\u30c3\u30af\u3057\u3066\u9589\u3058\u308b",
    "Close message": "\u9589\u3058\u308b",
    "Comment:": "\u6ce8\u91c8:",
    "Confirmed": "\u78ba\u8a8d\u6e08\u307f",
    "Confirming your payment \u2026": "\u304a\u652f\u6255\u3044\u306e\u78ba\u8a8d\u4e2d\u2026",
    "Contacting Stripe \u2026": "Stripe\u306b\u63a5\u7d9a\u4e2d\u2026",
    "Contacting your bank \u2026": "\u9280\u884c\u3078\u554f\u3044\u5408\u308f\u305b\u4e2d\u2026",
    "Continue": "\u6b21\u3078",
    "Copied!": "\u30b3\u30d4\u30fc\u5b8c\u4e86\uff01",
    "Count": "\u7dcf\u6570",
    "Credit Card": "\u30af\u30ec\u30b8\u30c3\u30c8\u30ab\u30fc\u30c9",
    "Current date and time": "\u73fe\u5728\u306e\u65e5\u6642",
    "Current day of the week (1 = Monday, 7 = Sunday)": "\u73fe\u5728\u306e\u66dc\u65e5 (1 = \u6708\u66dc\u65e5, 7 = \u65e5\u66dc\u65e5)",
    "Current entry status": "\u73fe\u5728\u306e\u767b\u9332\u30b9\u30c6\u30fc\u30bf\u30b9",
    "Currently inside": "\u73fe\u5728\u30aa\u30f3\u30e9\u30a4\u30f3\u3067\u3059",
    "December": "\uff11\uff12\u6708",
    "Do you really want to leave the editor without saving your changes?": "\u5909\u66f4\u5185\u5bb9\u3092\u4fdd\u5b58\u305b\u305a\u306b\u7de8\u96c6\u3092\u7d42\u4e86\u3057\u307e\u3059\u304b\uff1f",
    "Do you want to renew the reservation period?": "\u4e88\u7d04\u306e\u671f\u9593\u3092\u66f4\u65b0\u3057\u307e\u3059\u304b\uff1f",
    "Duplicate": "\u8907\u88fd",
    "Enter page number between 1 and %(max)s.": "1\u4ee5\u4e0a%(max)s\u4ee5\u4e0b\u306e\u30da\u30fc\u30b8\u756a\u53f7\u3092\u5165\u529b\u3002",
    "Entry": "\u5165\u53e3",
    "Entry not allowed": "\u5165\u529b\u3067\u304d\u307e\u305b\u3093",
    "Error while uploading your PDF file, please try again.": "PDF\u306e\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u4e2d\u306b\u554f\u984c\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002\u518d\u8a66\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "Event admission": "\u30a4\u30d9\u30f3\u30c8\u306e\u5165\u5834",
    "Event end": "\u30a4\u30d9\u30f3\u30c8\u7d42\u4e86",
    "Event start": "\u30a4\u30d9\u30f3\u30c8\u958b\u59cb",
    "Exit": "\u9000\u51fa",
    "Exit recorded": "\u8a18\u9332\u3092\u4fdd\u5b58",
    "February": "\uff12\u6708",
    "Fr": "\u91d1",
    "Friday": "\u91d1\u66dc\u65e5",
    "Gate": "\u30b2\u30fc\u30c8",
    "Generating messages \u2026": "\u30e1\u30c3\u30bb\u30fc\u30b8\u3092\u4f5c\u6210\u4e2d\u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "\u30aa\u30d6\u30b8\u30a7\u30af\u30c8\u30b0\u30eb\u30fc\u30d7",
    "If this takes longer than a few minutes, please contact us.": "\u6570\u5206\u4ee5\u4e0a\u304b\u304b\u308b\u5834\u5408\u306f\u3001\u304a\u554f\u3044\u5408\u308f\u305b\u304f\u3060\u3055\u3044\u3002",
    "Image area": "\u753b\u50cf\u30a8\u30ea\u30a2",
    "Information required": "\u60c5\u5831\u304c\u5fc5\u8981",
    "Invalid page number.": "\u7121\u52b9\u306a\u30da\u30fc\u30b8\u756a\u53f7\u3002",
    "Ita\u00fa": "Ita\u00fa",
    "January": "\uff11\u6708",
    "July": "\uff17\u6708",
    "June": "\uff16\u6708",
    "Load more": "\u3082\u3063\u3068\u898b\u308b",
    "March": "\uff13\u6708",
    "Marked as paid": "\u652f\u6255\u3044\u6e08\u307f",
    "Maxima": "Maxima",
    "May": "\uff15\u6708",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "\u6700\u521d\u306e\u3068\u3046\u308d\u304f\u304b\u3089\u306e\u7d4c\u904e\u5206\u6570(\u6700\u521d\u306e\u767b\u9332\u306f-1)",
    "Minutes since last entry (-1 on first entry)": "\u6700\u5f8c\u306e\u767b\u9332\u304b\u3089\u306e\u7d4c\u904e\u5206\u6570\uff08\u6700\u521d\u306e\u767b\u9332\u306f-1\uff09",
    "Mo": "\u6708",
    "Monday": "\u6708\u66dc\u65e5",
    "MyBank": "MyBank",
    "No": "\u3044\u3044\u3048",
    "No active check-in lists found.": "\u30a2\u30af\u30c6\u30a3\u30d6\u306a\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u30ea\u30b9\u30c8\u306f\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002",
    "No results": "\u7d50\u679c\u306a\u3057",
    "No tickets found": "\u30c1\u30b1\u30c3\u30c8\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093",
    "None": "\u306a\u3044",
    "November": "\uff11\uff11\u6708",
    "Number of days with a previous entry": "\u3053\u308c\u307e\u3067\u306e\u5165\u529b\u65e5\u6570",
    "Number of days with a previous entry before": "\u3053\u306e\u6642\u70b9\u3088\u308a\u524d\u306b\u5165\u529b\u304c\u884c\u308f\u308c\u305f\u65e5\u6570",
    "Number of days with a previous entry since": "\u3053\u306e\u6642\u70b9\u3088\u308a\u5f8c\u306b\u5165\u529b\u304c\u884c\u308f\u308c\u305f\u65e5\u6570",
    "Number of previous entries": "\u3053\u308c\u307e\u3067\u306e\u5165\u529b\u4ef6\u6570",
    "Number of previous entries before": "\u3053\u306e\u6642\u70b9\u3088\u308a\u524d\u306b\u5165\u529b\u3055\u308c\u305f\u4ef6\u6570",
    "Number of previous entries since": "\u3053\u306e\u6642\u70b9\u304b\u3089\u4eca\u307e\u3067\u306e\u5165\u529b\u4ef6\u6570",
    "Number of previous entries since midnight": "\uff10\u6642\u304b\u3089\u73fe\u5728\u307e\u3067\u306e\u5165\u529b\u4ef6\u6570",
    "OXXO": "OXXO",
    "Object": "\u30aa\u30d6\u30b8\u30a7\u30af\u30c8",
    "October": "\uff11\uff10\u6708",
    "Order canceled": "\u6ce8\u6587\u304c\u30ad\u30e3\u30f3\u30bb\u30eb\u3055\u308c\u307e\u3057\u305f",
    "Order not approved": "\u627f\u8a8d\u3055\u308c\u306a\u3044\u6ce8\u6587",
    "Others": "\u305d\u306e\u4ed6",
    "Paid orders": "\u652f\u6255\u3044\u6e08\u307f\u306e\u6ce8\u6587",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal\u30af\u30ec\u30b8\u30c3\u30c8",
    "PayPal Pay Later": "PayPal\u5f8c\u6255\u3044",
    "PayU": "PayU",
    "Payment method unavailable": "\u652f\u6255\u3044\u65b9\u6cd5\u304c\u5229\u7528\u3067\u304d\u307e\u305b\u3093",
    "Placed orders": "\u53d7\u6ce8\u72b6\u6cc1",
    "Please enter the amount the organizer can keep.": "\u4e3b\u50ac\u8005\u304c\u7559\u4fdd\u3059\u308b\u6599\u91d1\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "Powered by pretix": "Pretix\u306e\u30a4\u30d9\u30f3\u30c8\u30c1\u30b1\u30c3\u30c8\u58f2\u308a\u5834",
    "Press Ctrl-C to copy!": "Ctrl-C\u3092\u62bc\u3057\u3066\u30b3\u30d4\u30fc\uff01",
    "Product": "\u5546\u54c1",
    "Product variation": "\u5546\u54c1\u306e\u7a2e\u985e",
    "Przelewy24": "Przelewy24",
    "Redeemed": "\u4f7f\u7528\u6e08",
    "Renew reservation": "\u4e88\u7d04\u3092\u66f4\u65b0",
    "Result": "\u7d50\u679c",
    "SEPA Direct Debit": "SEPA Direct Debit",
    "SOFORT": "SOFORT",
    "Sa": "\u571f",
    "Saturday": "\u571f\u66dc\u65e5",
    "Saving failed.": "\u4fdd\u5b58\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002",
    "Scan a ticket or search and press return\u2026": "\u30c1\u30b1\u30c3\u30c8\u306e\u30b9\u30ad\u30e3\u30f3\u53c8\u306f\u691c\u7d22\u3092\u884c\u3044\u3001\u30ea\u30bf\u30fc\u30f3\u3092\u62bc\u3059\u2026",
    "Search query": "\u691c\u7d22\u30af\u30a8\u30ea",
    "Search results": "\u7d50\u679c\u3092\u691c\u7d22\u3059\u308b",
    "Select a check-in list": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u30ea\u30b9\u30c8\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044",
    "Selected only": "\u9078\u629e\u3057\u305f\u3082\u306e\u306e\u307f",
    "September": "\uff19\u6708",
    "Su": "\u65e5",
    "Sunday": "\u65e5\u66dc\u65e5",
    "Switch check-in list": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u30ea\u30b9\u30c8\u3092\u5207\u308a\u66ff\u3048",
    "Switch direction": "\u65b9\u5411\u8ee2\u63db",
    "Text box": "\u30c6\u30ad\u30b9\u30c8\u30dc\u30c3\u30af\u30b9",
    "Text object (deprecated)": "\u30c6\u30ad\u30b9\u30c8\u30aa\u30d6\u30b8\u30a7\u30af\u30c8 (\u5ec3\u6b62\u6e08)",
    "Th": "\u6728",
    "The PDF background file could not be loaded for the following reason:": "\u4ee5\u4e0b\u306e\u7406\u7531\u306b\u3088\u308aPDF\u30d5\u30a1\u30a4\u30eb\u306e\u8aad\u307f\u8fbc\u307f\u306b\u5931\u6557\u3057\u307e\u3057\u305f\uff1a",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they're available.": "\u30ab\u30fc\u30c8\u306b\u5165\u3063\u3066\u3044\u308b\u5546\u54c1\u306f\u304a\u53d6\u308a\u7f6e\u304d\u3067\u304d\u307e\u305b\u3093\u3002\u5728\u5eab\u304c\u3042\u308c\u3070\u3001\u3053\u306e\u307e\u307e\u6ce8\u6587\u3092\u9032\u3081\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "\u30ab\u30fc\u30c8\u306b\u5165\u3063\u3066\u3044\u308b\u5546\u54c1\u306f\u73fe\u5728\u58f2\u308a\u5207\u308c\u3067\u3059\u3002\u5728\u5eab\u304c\u3042\u308c\u3070\u3001\u3053\u306e\u307e\u307e\u6ce8\u6587\u3092\u5b8c\u4e86\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "\u30ab\u30fc\u30c8\u5185\u306e\u5546\u54c1\u306e\u4e88\u7d04\u306f {num} \u5206\u4ee5\u5185\u306b\u5b8c\u4e86\u3057\u307e\u3059\u3002"
    ],
    "The organizer keeps %(currency)s %(amount)s": "\u4e3b\u50ac\u8005\u306f%(currency)s %(amount)s\u3092\u7559\u4fdd\u3057\u307e\u3059",
    "The request took too long. Please try again.": "\u30ea\u30af\u30a8\u30b9\u30c8\u306e\u6642\u9593\u5207\u308c\u3067\u3059\u3002\u518d\u8a66\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "This ticket is not yet paid. Do you want to continue anyways?": "\u30c1\u30b1\u30c3\u30c8\u306e\u652f\u6255\u3044\u304c\u5b8c\u4e86\u3057\u3066\u3044\u307e\u305b\u3093\u3002\u3053\u306e\u307e\u307e\u7d9a\u3051\u307e\u3059\u304b\uff1f",
    "This ticket requires special attention": "\u3053\u306e\u30c1\u30b1\u30c3\u30c8\u306f\u7279\u5225\u306a\u5bfe\u5fdc\u304c\u5fc5\u8981\u3067\u3059",
    "Thursday": "\u6728\u66dc\u65e5",
    "Ticket already used": "\u4f7f\u7528\u6e08\u307f\u306e\u30c1\u30b1\u30c3\u30c8",
    "Ticket blocked": "\u30c1\u30b1\u30c3\u30c8\u30d6\u30ed\u30c3\u30af\u4e2d",
    "Ticket code is ambiguous on list": "\u30ea\u30b9\u30c8\u306e\u30c1\u30b1\u30c3\u30c8\u30b3\u30fc\u30c9\u306f\u66d6\u6627\u3067\u3059",
    "Ticket code revoked/changed": "\u30c1\u30b1\u30c3\u30c8\u30b3\u30fc\u30c9\u306e\u30d6\u30ed\u30c3\u30af/\u5909\u66f4",
    "Ticket design": "\u30c1\u30b1\u30c3\u30c8\u306e\u30c7\u30b6\u30a4\u30f3",
    "Ticket not paid": "\u30c1\u30b1\u30c3\u30c8\u672a\u6255\u3044",
    "Ticket not valid at this time": "\u73fe\u6642\u70b9\u3067\u7121\u52b9\u306a\u30c1\u30b1\u30c3\u30c8",
    "Ticket type not allowed here": "\u3053\u306e\u7a2e\u985e\u306e\u30c1\u30b1\u30c3\u30c8\u306f\u4f7f\u7528\u3067\u304d\u307e\u305b\u3093",
    "Tolerance (minutes)": "\u8a31\u5bb9\u8aa4\u5dee\uff08\u5206\uff09",
    "Total": "\u5408\u8a08",
    "Total revenue": "\u58f2\u4e0a\u5408\u8a08",
    "Trustly": "Trustly",
    "Tu": "\u706b",
    "Tuesday": "\u706b\u66dc\u65e5",
    "Unknown error.": "\u4e0d\u660e\u306a\u30a8\u30e9\u30fc\u3002",
    "Unknown ticket": "\u4e0d\u660e\u306a\u30c1\u30b1\u30c3\u30c8",
    "Unpaid": "\u672a\u6255\u3044",
    "Use a different name internally": "\u5185\u90e8\u3067\u5225\u306e\u540d\u524d\u3092\u4f7f\u7528\u3057\u3066\u304f\u3060\u3055\u3044",
    "Valid": "\u6709\u52b9",
    "Valid Tickets": "\u6709\u52b9\u306a\u30c1\u30b1\u30c3\u30c8",
    "Valid ticket": "\u6709\u52b9\u306a\u30c1\u30b1\u30c3\u30c8",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "\u6c34",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "\u30ea\u30af\u30a8\u30b9\u30c8\u304c\u30b5\u30fc\u30d0\u3078\u9001\u4fe1\u3055\u308c\u307e\u3057\u305f\u3002\uff11\u5206\u4ee5\u4e0a\u7d4c\u3063\u3066\u3082\u5fdc\u7b54\u304c\u306a\u3044\u5834\u5408\u306f\u3001\u30a4\u30f3\u30bf\u30fc\u30cd\u30c3\u30c8\u63a5\u7d9a\u3092\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u78ba\u8a8d\u5b8c\u4e86\u5f8c\u3001\u30a6\u30a7\u30d6\u30da\u30fc\u30b8\u3092\u518d\u5ea6\u8aad\u8fbc\u307f\u3001\u518d\u8a66\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "We are processing your request \u2026": "\u30ea\u30af\u30a8\u30b9\u30c8\u3092\u51e6\u7406\u4e2d\u3067\u3059 \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "\u73fe\u5728\u30b5\u30fc\u30d0\u3078\u306e\u63a5\u7d9a\u304c\u3067\u304d\u307e\u305b\u3093\u304c\u3001\u63a5\u7d9a\u8a66\u884c\u4e2d\u3067\u3059\u3002\u30a8\u30e9\u30fc\u30b3\u30fc\u30c9\uff1a {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "\u73fe\u5728\u30b5\u30fc\u30d0\u304c\u5fdc\u7b54\u3057\u3066\u3044\u307e\u305b\u3093\u3002\u518d\u8a66\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u30a8\u30e9\u30fc\u30b3\u30fc\u30c9\uff1a {code}",
    "WeChat Pay": "WeChat Pay",
    "Wednesday": "\u6c34\u66dc\u65e5",
    "Yes": "\u306f\u3044",
    "You get %(currency)s %(amount)s back": "%(currency)s %(amount)s \u304c\u6255\u3044\u623b\u3055\u308c\u307e\u3059",
    "You have unsaved changes!": "\u4fdd\u5b58\u3055\u308c\u3066\u3044\u306a\u3044\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\uff01",
    "Your cart has expired.": "\u30ab\u30fc\u30c8\u306e\u4fdd\u5b58\u671f\u9650\u304c\u5207\u308c\u3066\u3044\u307e\u3059\u3002",
    "Your color has decent contrast and is sufficient for minimum accessibility requirements.": "\u3042\u306a\u305f\u306e\u8272\u306f\u9069\u5207\u306a\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8\u3092\u6301\u3061\u3001\u6700\u5c0f\u9650\u306e\u30a2\u30af\u30bb\u30b7\u30d3\u30ea\u30c6\u30a3\u8981\u4ef6\u306b\u5341\u5206\u3067\u3059\u3002",
    "Your color has great contrast and will provide excellent accessibility.": "\u3042\u306a\u305f\u306e\u8272\u306f\u7d20\u6674\u3089\u3057\u3044\u30b3\u30f3\u30c8\u30e9\u30b9\u30c8\u3092\u6301\u3061\u3001\u512a\u308c\u305f\u30a2\u30af\u30bb\u30b7\u30d3\u30ea\u30c6\u30a3\u3092\u63d0\u4f9b\u3057\u307e\u3059\u3002",
    "Your local time:": "\u73fe\u5730\u6642\u9593\uff1a",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "\u304a\u5ba2\u69d8\u306e\u30ea\u30af\u30a8\u30b9\u30c8\u304c\u30b5\u30fc\u30d0\u30fc\u3078\u9001\u4fe1\u3055\u308c\u307e\u3057\u305f\u3002\u73fe\u5728\u51e6\u7406\u306e\u5f85\u6a5f\u4e2d\u3067\u3059\u30022\u5206\u4ee5\u4e0a\u7d4c\u3063\u3066\u3082\u5fdc\u7b54\u304c\u306a\u3044\u5834\u5408\u306f\u3001\u5f0a\u793e\u3078\u304a\u554f\u3044\u5408\u308f\u305b\u3044\u305f\u3060\u304f\u304b\u3001\u30d6\u30e9\u30a6\u30b6\u3092\u4e00\u3064\u524d\u306b\u623b\u3057\u3066\u518d\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002",
    "Your request has been queued on the server and will soon be processed.": "\u30b5\u30fc\u30d0\u3078\u9001\u4fe1\u3055\u308c\u305f\u30ea\u30af\u30a8\u30b9\u30c8\u9806\u306b\u304a\u5fdc\u3048\u3057\u3066\u3044\u307e\u3059\u3002\u4eca\u3057\u3070\u3089\u304f\u304a\u5f85\u3061\u304f\u3060\u3055\u3044\u3002",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "\u304a\u5ba2\u69d8\u306e\u30ea\u30af\u30a8\u30b9\u30c8\u306f\u73fe\u5728\u51e6\u7406\u4e2d\u3067\u3059\u3002\u30a4\u30d9\u30f3\u30c8\u306e\u898f\u6a21\u306b\u3088\u308a\u3001\u6570\u5206\u304b\u304b\u308b\u5834\u5408\u304c\u3042\u308a\u307e\u3059\u3002",
    "Zimpler": "Zimpler",
    "close": "\u9589\u3058\u308b",
    "custom date and time": "\u65e5\u6642\u78ba\u5b9a",
    "custom time": "\u6642\u523b\u78ba\u5b9a",
    "entry_status\u0004absent": "\u6b20\u5e2d",
    "entry_status\u0004present": "\u51fa\u5e2d",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "\u306e\u5f8c",
    "is before": "\u306e\u524d",
    "is one of": "\u306e\u4e00\u3064\u3067\u3059",
    "minutes": "\u5206",
    "required": "\u5fc5\u9808",
    "widget\u0004Back": "\u623b\u308b",
    "widget\u0004Buy": "\u30ab\u30fc\u30c8\u5185",
    "widget\u0004Checkout": "\u30c1\u30a7\u30c3\u30af\u30a2\u30a6\u30c8",
    "widget\u0004Choose a different date": "\u4ed6\u306e\u65e5\u4ed8\u3092\u9078\u629e\u3059\u308b",
    "widget\u0004Choose a different event": "\u4ed6\u306e\u30a4\u30d9\u30f3\u30c8\u3092\u9078\u629e\u3059\u308b",
    "widget\u0004Close": "\u9589\u3058\u308b",
    "widget\u0004Close ticket shop": "\u30c1\u30b1\u30c3\u30c8\u30b7\u30e7\u30c3\u30d7\u9589\u5e97",
    "widget\u0004Continue": "\u7d9a\u3051\u308b",
    "widget\u0004Currently not available": "\u73fe\u6642\u70b9\u3067\u63d0\u4f9b\u4e0d\u53ef",
    "widget\u0004Decrease quantity": "\u6570\u91cf\u3092\u6e1b\u3089\u3059",
    "widget\u0004FREE": "\u7121\u6599",
    "widget\u0004Hide variants": "\u30d0\u30ea\u30a8\u30fc\u30b7\u30e7\u30f3\u3092\u96a0\u3059",
    "widget\u0004Image of %s": "%s\u306e\u30a4\u30e1\u30fc\u30b8",
    "widget\u0004Increase quantity": "\u6570\u91cf\u3092\u5897\u3084\u3059",
    "widget\u0004Load more": "\u3055\u3089\u306b\u8aad\u307f\u8fbc\u3080",
    "widget\u0004New price: %s": "\u65b0\u3057\u3044\u4fa1\u683c: %s",
    "widget\u0004Next month": "\u7fcc\u6708",
    "widget\u0004Next week": "\u7fcc\u9031",
    "widget\u0004Not available anymore": "\u4eca\u5f8c\u306e\u63d0\u4f9b\u4e0d\u53ef",
    "widget\u0004Not yet available": "\u63d0\u4f9b\u958b\u59cb\u524d",
    "widget\u0004Only available with a voucher": "\u30af\u30fc\u30dd\u30f3\u3092\u304a\u6301\u3061\u306e\u65b9\u306e\u307f",
    "widget\u0004Open seat selection": "\u5ea7\u5e2d\u4e00\u89a7\u3092\u958b\u304f",
    "widget\u0004Open ticket shop": "\u30c1\u30b1\u30c3\u30c8\u30b7\u30e7\u30c3\u30d7\u3092\u958b\u304f",
    "widget\u0004Original price: %s": "\u5143\u306e\u4fa1\u683c: %s",
    "widget\u0004Previous month": "\u524d\u6708",
    "widget\u0004Previous week": "\u524d\u9031",
    "widget\u0004Price": "\u4fa1\u683c",
    "widget\u0004Quantity": "\u6570\u91cf",
    "widget\u0004Redeem": "\u4f7f\u7528\u3059\u308b",
    "widget\u0004Redeem a voucher": "\u30af\u30fc\u30dd\u30f3\u3092\u4f7f\u7528\u3059\u308b",
    "widget\u0004Register": "\u767b\u9332",
    "widget\u0004Reserved": "\u4e88\u7d04\u5b8c\u4e86",
    "widget\u0004Resume checkout": "\u8cfc\u5165\u3092\u7d9a\u884c\u3059\u308b",
    "widget\u0004Select": "\u9078\u629e",
    "widget\u0004Select %s": "%s\u3092\u9078\u629e",
    "widget\u0004Select variant %s": "\u30d0\u30ea\u30a2\u30f3\u30c8 %s\u3092\u9078\u629e",
    "widget\u0004Show variants": "\u30d0\u30ea\u30a8\u30fc\u30b7\u30e7\u30f3\u3092\u8868\u793a",
    "widget\u0004Sold out": "\u58f2\u308a\u5207\u308c",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "\u73fe\u5728\u3001\u4e00\u90e8\u307e\u305f\u306f\u3059\u3079\u3066\u306e\u30ab\u30c6\u30b4\u30ea\u3067\u30c1\u30b1\u30c3\u30c8\u304c\u58f2\u308a\u5207\u308c\u3066\u3044\u307e\u3059\u3002\u3054\u5e0c\u671b\u306b\u5fdc\u3058\u3066\u3001\u3054\u81ea\u8eab\u3067\u7a7a\u5e2d\u5f85\u3061\u30ea\u30b9\u30c8\u306b\u8ffd\u52a0\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002\u305d\u306e\u5f8c\u3001\u7a7a\u5e2d\u304c\u51fa\u6765\u6b21\u7b2c\u304a\u77e5\u3089\u305b\u3057\u307e\u3059\u3002",
    "widget\u0004The cart could not be created. Please try again later": "\u30ab\u30fc\u30c8\u304c\u4f5c\u6210\u3067\u304d\u307e\u305b\u3093\u3002\u5f8c\u307b\u3069\u518d\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044",
    "widget\u0004The ticket shop could not be loaded.": "\u30c1\u30b1\u30c3\u30c8\u30b7\u30e7\u30c3\u30d7\u306e\u8aad\u307f\u8fbc\u307f\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "\u73fe\u5728\u30c1\u30b1\u30c3\u30c8\u30b7\u30e7\u30c3\u30d7\u304c\u6df7\u307f\u5408\u3063\u3066\u3044\u307e\u3059\u3002\u65b0\u3057\u3044\u30bf\u30d6\u3067\u30c1\u30b1\u30c3\u30c8\u30b7\u30e7\u30c3\u30d7\u3092\u958b\u304d\u7d9a\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "widget\u0004Voucher code": "\u30af\u30fc\u30dd\u30f3\u30b3\u30fc\u30c9",
    "widget\u0004Waiting list": "\u7a7a\u5e2d\u5f85\u3061\u30ea\u30b9\u30c8",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "\u73fe\u5728\u30c1\u30b1\u30c3\u30c8\u30b7\u30e7\u30c3\u30d7\u304c\u6df7\u96d1\u3057\u3066\u3044\u308b\u305f\u3081\u3001\u304a\u5ba2\u69d8\u306e\u30ab\u30fc\u30c8\u3092\u4f5c\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002\u65b0\u3057\u3044\u30bf\u30d6\u3092\u958b\u304d\u300c\u6b21\u3078\u300d\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "\u304a\u5ba2\u69d8\u306e\u30ab\u30fc\u30c8\u306f\u30a4\u30d9\u30f3\u30c8\u306e\u7533\u3057\u8fbc\u307f\u306b\u6709\u52b9\u3067\u3059\u3002\u5546\u54c1\u3092\u9078\u629e\u3057\u3001\u30ab\u30fc\u30c8\u3078\u8ffd\u52a0\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "widget\u0004currently available: %s": "\u73fe\u5728%s\u4f7f\u7528\u53ef\u80fd",
    "widget\u0004from %(currency)s %(price)s": "%(currency)s %(price)s\u304b\u3089",
    "widget\u0004incl. %(rate)s% %(taxname)s": "%(rate)s% %(taxname)s\u8fbc",
    "widget\u0004incl. taxes": "\u7a0e\u8fbc",
    "widget\u0004minimum amount to order: %s": "\u6700\u5c0f\u6ce8\u6587\u6570\u91cf\uff1a%s",
    "widget\u0004plus %(rate)s% %(taxname)s": "%(rate)s% %(taxname)s\u629c",
    "widget\u0004plus taxes": "\u7a0e\u629c"
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
    "DATETIME_FORMAT": "Y\u5e74n\u6708j\u65e5G:i",
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
    "DATE_FORMAT": "Y\u5e74n\u6708j\u65e5",
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
    "MONTH_DAY_FORMAT": "n\u6708j\u65e5",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "Y/m/d G:i",
    "SHORT_DATE_FORMAT": "Y/m/d",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "G:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
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

