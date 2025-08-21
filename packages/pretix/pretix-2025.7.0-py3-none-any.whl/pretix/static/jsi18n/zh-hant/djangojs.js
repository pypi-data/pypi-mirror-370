

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
      "\uff08\u518d\u4f86more\u65e5\u671f\uff09\n\uff08{num} more\u65e5\u671f\uff09"
    ],
    "=": "=",
    "Add condition": "\u589e\u52a0\u689d\u4ef6",
    "Additional information required": "\u9700\u8981\u984d\u5916\u7684\u8cc7\u8a0a",
    "All": "\u6240\u6709",
    "All of the conditions below (AND)": "\u4ee5\u4e0b\u6240\u6709\u7684\u689d\u4ef6 (\u548c)",
    "An error has occurred.": "\u767c\u751f\u932f\u8aa4\u4e86\u3002",
    "An error of type {code} occurred.": "\u767c\u751f {code} \u985e\u578b\u932f\u8aa4\u3002",
    "Apple Pay": "Apple Pay",
    "Approval pending": "\u7b49\u5f85\u6279\u51c6",
    "April": "\u56db\u6708",
    "At least one of the conditions below (OR)": "\u4ee5\u4e0b\u81f3\u5c11\u5176\u4e2d\u4e00\u500b\u689d\u4ef6 (\u6216)",
    "August": "\u516b\u6708",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "\u4e8c\u7dad\u689d\u78bc\u5340\u57df",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "\u8a08\u7b97\u9810\u8a2d\u50f9\u683c\u2026",
    "Cancel": "\u53d6\u6d88",
    "Canceled": "\u5df2\u53d6\u6d88",
    "Cart expired": "\u8cfc\u7269\u8eca\u904e\u671f",
    "Check-in QR": "\u5831\u5230 QR code",
    "Checked-in Tickets": "\u5df2\u7d93\u5165\u5834\u7684\u7968\u5238",
    "Click to close": "\u9ede\u64ca\u95dc\u9589",
    "Close message": "\u95dc\u9589\u8a0a\u606f",
    "Comment:": "\u8a3b\u89e3\uff1a",
    "Confirmed": "\u5df2\u78ba\u8a8d",
    "Confirming your payment \u2026": "\u78ba\u8a8d\u4f60\u7684\u4ed8\u6b3e\u8cc7\u8a0a...\u2026",
    "Contacting Stripe \u2026": "\u806f\u7e6b Stripe \u7576\u4e2d\u2026",
    "Contacting your bank \u2026": "\u806f\u7e6b\u4f60\u7684\u9280\u884c\u7576\u4e2d\u2026",
    "Continue": "\u7e7c\u7e8c",
    "Copied!": "\u8907\u88fd\uff01",
    "Count": "\u8a08\u6578",
    "Credit Card": "\u4fe1\u7528\u5361",
    "Current date and time": "\u76ee\u524d\u65e5\u671f\u8207\u6642\u9593",
    "Current day of the week (1 = Monday, 7 = Sunday)": "\u76ee\u524d\u4e00\u9031\u7576\u4e2d\u7684\u661f\u671f\u5e7e(1=\u661f\u671f\u4e00\uff0c7=\u661f\u671f\u5929)",
    "Current entry status": "\u7576\u524d\u5165\u5834\u72c0\u614b",
    "Currently inside": "\u76ee\u524d\u5728\u5834\u5167",
    "December": "\u5341\u4e8c\u6708",
    "Do you really want to leave the editor without saving your changes?": "\u4f60\u771f\u5f97\u8981\u4e0d\u5132\u5b58\u5c31\u96e2\u958b\u7de8\u8f2f\u5668\u55ce\uff1f",
    "Duplicate": "\u91cd\u8986",
    "Enter page number between 1 and %(max)s.": "\u8f38\u5165\u65bc 1 \u548c %(max)s \u4e4b\u9593\u7684\u9801\u865f\u3002",
    "Entry": "\u9032\u5834",
    "Entry not allowed": "\u4e0d\u5141\u8a31\u5165\u5834",
    "Error while uploading your PDF file, please try again.": "\u4e0a\u50b3\u4f60\u7684PDF\u6a94\u6848\u6642\u767c\u751f\u932f\u8aa4\uff0c\u8acb\u518d\u8a66\u4e00\u6b21\u3002",
    "Event admission": "\u6d3b\u52d5\u7ba1\u7406",
    "Event end": "\u6d3b\u52d5\u7d50\u675f",
    "Event start": "\u6d3b\u52d5\u958b\u59cb",
    "Exit": "\u51fa\u5834",
    "Exit recorded": "\u5df2\u7d93\u8a18\u9304\u96e2\u5834\u4e86",
    "February": "\u4e8c\u6708",
    "Fr": "\u661f\u671f\u4e94",
    "Friday": "\u9031\u4e94",
    "Gate": "\u9598\u53e3",
    "Generating messages \u2026": "\u7522\u751f\u8a0a\u606f\u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "\u7269\u4ef6\u7fa4\u7d44",
    "Image area": "\u5716\u7247\u5340\u57df",
    "Information required": "\u9700\u8981\u8cc7\u8a0a",
    "Invalid page number.": "\u9801\u865f\u7121\u6548\u3002",
    "Ita\u00fa": "Ita\u00fa",
    "January": "\u4e00\u6708",
    "July": "\u4e03\u6708",
    "June": "\u516d\u6708",
    "Load more": "\u8f09\u5165\u66f4\u591a",
    "March": "\u4e09\u6708",
    "Marked as paid": "\u6a19\u8a18\u70ba\u5df2\u4ed8\u8cbb",
    "Maxima": "Maxima",
    "May": "\u4e94\u6708",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "\u81ea\u5f9e\u7b2c\u4e00\u6b21\u5165\u5834\u7684\u5206\u9418(-1\u662f\u7b2c\u4e00\u6b21\u5165\u5834)",
    "Minutes since last entry (-1 on first entry)": "\u81ea\u5f9e\u6700\u5f8c\u5165\u5834\u4e4b\u5f8c\u7684\u5206\u9418(-1\u662f\u7b2c\u4e00\u6b21\u5165\u5834)",
    "Mo": "\u661f\u671f\u4e00",
    "Monday": "\u9031\u4e00",
    "MyBank": "MyBank",
    "No": "\u5426",
    "No active check-in lists found.": "\u5728\u6709\u6548\u7684\u5831\u5230\u6e05\u55ae\u7576\u4e2d\u6c92\u627e\u5230\u3002",
    "No results": "\u7121\u7d50\u679c",
    "No tickets found": "\u6c92\u6709\u627e\u5230\u7968\u5238",
    "None": "\u7121",
    "November": "\u5341\u4e00\u6708",
    "Number of days with a previous entry": "\u5148\u524d\u5165\u5834\u7684\u5929\u6578\u6578\u91cf",
    "Number of days with a previous entry before": "\u5148\u524d\u81ea\u4e0a\u6b21\u5165\u5834\u4ee5\u4f86\u7684\u5929\u6578",
    "Number of days with a previous entry since": "\u81ea\u4e0a\u6b21\u5165\u5834\u4ee5\u4f86\u7684\u5929\u6578",
    "Number of previous entries": "\u5148\u524d\u5165\u5834\u7684\u6578\u91cf",
    "Number of previous entries before": "\u5148\u524d\u7684\u5165\u5834\u7684\u6578\u91cf",
    "Number of previous entries since": "\u4e4b\u524d\u5165\u5834\u7684\u6578\u91cf",
    "Number of previous entries since midnight": "\u81ea\u5f9e\u6df1\u591c\u6642\u5148\u524d\u5165\u5834\u7684\u6578\u91cf",
    "OXXO": "OXXO",
    "Object": "\u7269\u4ef6",
    "October": "\u5341\u6708",
    "Order canceled": "\u8a02\u55ae\u5df2\u53d6\u6d88",
    "Order not approved": "\u7968\u5238\u672a\u78ba\u8a8d",
    "Others": "\u5176\u4ed6\u4eba",
    "Paid orders": "\u5df2\u4ed8\u6b3e\u8a02\u55ae",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "\u76ee\u524d\u7121\u6cd5\u4f7f\u7528\u7684\u4ed8\u6b3e\u65b9\u5f0f",
    "Placed orders": "\u5b58\u653e\u8a02\u55ae",
    "Please enter the amount the organizer can keep.": "\u8acb\u8f38\u5165\u4e3b\u8fa6\u65b9\u53ef\u4ee5\u4fdd\u7559\u7684\u91d1\u984d\u3002",
    "Powered by pretix": "pretix \u9a45\u52d5",
    "Press Ctrl-C to copy!": "\u6309 Ctrl-C \u4f86\u8907\u88fd\uff01",
    "Product": "\u7522\u54c1",
    "Product variation": "\u7522\u54c1\u8b8a\u9ad4",
    "Przelewy24": "Przelewy24",
    "Redeemed": "\u5df2\u514c\u63db",
    "Result": "\u7d50\u679c",
    "SEPA Direct Debit": "\u55ae\u4e00\u6b50\u5143\u652f\u4ed8\u5340\u7c3d\u5e33\u5361",
    "SOFORT": "SOFORT",
    "Sa": "\u661f\u671f\u516d",
    "Saturday": "\u9031\u516d",
    "Saving failed.": "\u5132\u5b58\u5931\u6557\u3002",
    "Scan a ticket or search and press return\u2026": "\u6383\u63cf\u6216\u662f\u641c\u5c0b\u7968\u5238\u7136\u5f8c\u6309\u8fd4\u56de\u2026",
    "Search query": "\u641c\u7d22\u67e5\u8a62",
    "Search results": "\u641c\u5c0b\u7d50\u679c",
    "Select a check-in list": "\u9078\u64c7\u5831\u5230\u6e05\u55ae",
    "Selected only": "\u53ea\u9078\u5b9a",
    "September": "\u4e5d\u6708",
    "Su": "\u661f\u671f\u5929",
    "Sunday": "\u9031\u65e5",
    "Switch check-in list": "\u5207\u63db\u5831\u5230\u6e05\u55ae",
    "Switch direction": "\u5207\u63db\u65b9\u5411",
    "Text box": "\u6587\u5b57\u6846",
    "Text object (deprecated)": "\u6587\u5b57\u7269\u4ef6\uff08\u5df2\u68c4\u7528\uff09",
    "Th": "\u661f\u671f\u56db",
    "The PDF background file could not be loaded for the following reason:": "\u80cc\u666f\u7684PDF\u6a94\u6848\u56e0\u70ba\u4e0b\u5217\u539f\u56e0\u7121\u6cd5\u8f09\u5165\uff1a",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "\u4f60\u8cfc\u7269\u8eca\u4e2d\u7684\u7269\u54c1\u4e0d\u518d\u70ba\u4f60\u4fdd\u7559\u3002\u53ea\u8981\u53ef\u7528\uff0c\u4f60\u4ecd\u7136\u53ef\u4ee5\u5b8c\u6210\u8a02\u55ae\u3002",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "\u8cfc\u7269\u8eca\u4e2d\u7684\u5546\u54c1\u5c07\u70ba\u4f60\u4fdd\u7559{num}\u5206\u9418\u3002"
    ],
    "The organizer keeps %(currency)s %(amount)s": "\u53ec\u96c6\u4eba\u4fdd\u7559%(currency)s %(amount)s",
    "The request took too long. Please try again.": "\u8acb\u6c42\u82b1\u592a\u9577\u6642\u9593\uff0c\u8acb\u518d\u8a66\u4e00\u6b21\u3002",
    "This ticket is not yet paid. Do you want to continue anyways?": "\u9019\u5f35\u7968\u5238\u9084\u6c92\u6709\u4ed8\u6b3e\uff0c\u4f60\u60f3\u8981\u7e7c\u7e8c\u55ce\uff1f",
    "This ticket requires special attention": "\u9019\u5f35\u7968\u5238\u9700\u8981\u7279\u5225\u7559\u610f",
    "Thursday": "\u9031\u56db",
    "Ticket already used": "\u7968\u5238\u5df2\u7d93\u4f7f\u7528\u4e86",
    "Ticket blocked": "\u7968\u5238\u5df2\u7d93\u5c01\u92b7",
    "Ticket code is ambiguous on list": "\u6e05\u55ae\u4e0a\u7684\u7968\u5238\u4ee3\u78bc\u4e0d\u6e05\u695a",
    "Ticket code revoked/changed": "\u7968\u5238\u4ee3\u78bc\u5df2\u7d93\u53d6\u6d88/\u6539\u8b8a",
    "Ticket design": "\u7968\u5238\u8a2d\u8a08",
    "Ticket not paid": "\u7968\u5238\u9084\u672a\u4ed8\u6b3e",
    "Ticket not valid at this time": "\u5728\u9019\u6642\u9593\u7968\u5238\u4ecd\u672a\u6709\u6548",
    "Ticket type not allowed here": "\u9019\u88e1\u4e0d\u5141\u9019\u7a2e\u7968\u5238\u985e\u578b",
    "Tolerance (minutes)": "\u5bb9\u5fcd\u5ea6 (\u5206\u9418)",
    "Total": "\u5168\u90e8",
    "Total revenue": "\u5168\u90e8\u6536\u5165",
    "Trustly": "Trustly",
    "Tu": "\u661f\u671f\u4e8c",
    "Tuesday": "\u9031\u4e8c",
    "Unknown error.": "\u4e0d\u77e5\u540d\u932f\u8aa4\u3002",
    "Unknown ticket": "\u4e0d\u77e5\u540d\u7684\u7968\u5238",
    "Unpaid": "\u672a\u4ed8\u6b3e",
    "Use a different name internally": "\u5728\u5167\u90e8\u4f7f\u7528\u5176\u4ed6\u540d\u7a31",
    "Valid": "\u6709\u6548",
    "Valid Tickets": "\u6709\u6548\u7968\u5238",
    "Valid ticket": "\u6709\u6548\u7968\u5238",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "\u661f\u671f\u4e09",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "\u6211\u5011\u76ee\u524d\u6b63\u5728\u50b3\u9001\u4f60\u7684\u8981\u6c42\u5230\u4f3a\u670d\u5668\uff0c\u5982\u679c\u82b1\u8d85\u904e\u4e00\u5206\u9418\uff0c\u8acb\u6aa2\u67e5\u4f60\u7684\u7db2\u8def\u9023\u7dda\uff0c\u4e26\u4e14\u91cd\u65b0\u6574\u7406\u9801\u9762\u518d\u8a66\u4e00\u6b21\u3002",
    "We are processing your request \u2026": "\u6211\u5011\u6b63\u5728\u8655\u7406\u4f60\u7684\u8acb\u6c42\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "\u6211\u5011\u76ee\u524d\u7121\u6cd5\u9023\u5230\u4f3a\u670d\u5668\uff0c\u4f46\u6211\u5011\u6703\u6301\u7e8c\u5617\u8a66\uff0c\u6700\u5f8c\u7684\u932f\u8aa4\u4ee3\u78bc\uff1a{code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "\u6211\u5011\u76ee\u524d\u7121\u6cd5\u9023\u5230\u4f3a\u670d\u5668\uff0c\u8acb\u518d\u8a66\u4e00\u6b21\uff0c\u932f\u8aa4\u4ee3\u78bc\uff1a{code}",
    "WeChat Pay": "\u5fae\u4fe1\u652f\u4ed8",
    "Wednesday": "\u9031\u4e09",
    "Yes": "\u662f",
    "You get %(currency)s %(amount)s back": "\u4f60\u62ff\u56de %(currency)s %(amount)s",
    "You have unsaved changes!": "\u4f60\u6709\u672a\u5132\u5b58\u7684\u8b8a\u66f4\uff01",
    "Your local time:": "\u4f60\u7684\u7576\u5730\u6642\u9593\uff1a",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "\u4f60\u7684\u8acb\u6c42\u5df2\u7d93\u9001\u9054\u4f3a\u670d\u5668\uff0c\u4f46\u4ecd\u9700\u8981\u7b49\u5f85\u8655\u7406\u3002\u5982\u679c\u8d85\u904e\u5169\u5206\u9418\u7684\u8a71\uff0c\u8acb\u806f\u7d61\u6211\u5011\u6216\u662f\u56de\u5230\u700f\u89bd\u5668\u518d\u8a66\u4e00\u6b21\u3002",
    "Your request has been queued on the server and will soon be processed.": "\u4f60\u7684\u8acb\u6c42\u5df2\u7d93\u5728\u4f3a\u670d\u5668\u7684\u4f47\u5217\uff0c\u4e0d\u4e45\u5c07\u6703\u8655\u7406\u3002",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "\u4f60\u7684\u8acb\u6c42\u5df2\u7d93\u5728\u8655\u7406\u4e86\uff0c\u8996\u4f60\u6d3b\u52d5\u7684\u5927\u5c0f\uff0c\u4e5f\u8a31\u6703\u82b1\u5e7e\u5206\u9418\u6642\u9593\u3002",
    "Zimpler": "Zimpler",
    "close": "\u95dc\u9589",
    "custom date and time": "\u5ba2\u88fd\u5316\u65e5\u671f\u8207\u6642\u9593",
    "custom time": "\u5ba2\u88fd\u5316\u6642\u9593",
    "entry_status\u0004absent": "\u7f3a\u5e2d",
    "entry_status\u0004present": "\u51fa\u5e2d",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "\u662f\u4e4b\u5f8c",
    "is before": "\u662f\u4e4b\u524d",
    "is one of": "\u5176\u4e2d\u4e00\u500b",
    "minutes": "\u5206\u9418",
    "required": "\u9700\u8981",
    "widget\u0004Back": "\u8fd4\u56de",
    "widget\u0004Buy": "\u8cfc\u8cb7",
    "widget\u0004Checkout": "\u7d50\u5e33",
    "widget\u0004Choose a different date": "\u9078\u64c7\u5176\u4ed6\u65e5\u671f",
    "widget\u0004Choose a different event": "\u9078\u64c7\u5176\u4ed6\u6d3b\u52d5",
    "widget\u0004Close": "\u95dc\u9589",
    "widget\u0004Close ticket shop": "\u95dc\u9589\u552e\u7968\u8655",
    "widget\u0004Continue": "\u7e7c\u7e8c",
    "widget\u0004Currently not available": "\u76ee\u524d\u4e0d\u53ef\u7528",
    "widget\u0004Decrease quantity": "\u6e1b\u5c11\u6578\u91cf",
    "widget\u0004FREE": "\u514d\u8cbb\u6216\u81ea\u7531",
    "widget\u0004Hide variants": "\u96b1\u85cf\u4e0d\u540c\u7684\u985e\u578b",
    "widget\u0004Image of %s": "%s\u7684\u5716\u50cf",
    "widget\u0004Increase quantity": "\u589e\u52a0\u6578\u91cf",
    "widget\u0004Load more": "\u8f09\u5165\u66f4\u591a",
    "widget\u0004New price: %s": "\u65b0\u50f9: %s",
    "widget\u0004Next month": "\u4e0b\u500b\u6708",
    "widget\u0004Next week": "\u4e0b\u9031",
    "widget\u0004Not available anymore": "\u4e0d\u518d\u53ef\u7528",
    "widget\u0004Not yet available": "\u76ee\u524d\u7121\u6cd5\u4f7f\u7528",
    "widget\u0004Only available with a voucher": "\u50c5\u9650\u512a\u60e0\u5238\u53ef\u7528",
    "widget\u0004Open seat selection": "\u958b\u653e\u9078\u4f4d",
    "widget\u0004Open ticket shop": "\u958b\u653e\u552e\u7968",
    "widget\u0004Original price: %s": "\u539f\u50f9: %s",
    "widget\u0004Previous month": "\u524d\u4e00\u500b\u6708\u4efd",
    "widget\u0004Previous week": "\u524d\u4e00\u9031",
    "widget\u0004Price": "\u50f9\u683c",
    "widget\u0004Quantity": "\u6578\u91cf",
    "widget\u0004Redeem": "\u514c\u63db",
    "widget\u0004Redeem a voucher": "\u514c\u63db\u512a\u60e0\u5238",
    "widget\u0004Register": "\u8a3b\u518a",
    "widget\u0004Reserved": "\u4fdd\u7559",
    "widget\u0004Resume checkout": "\u7e7c\u7e8c\u7d50\u5e33",
    "widget\u0004Select": "\u9078\u64c7",
    "widget\u0004Select %s": "\u9078\u64c7%s",
    "widget\u0004Select variant %s": "\u9078\u64c7\u985e\u578b %s",
    "widget\u0004Show variants": "\u986f\u793a\u4e0d\u540c\u7684\u985e\u578b",
    "widget\u0004Sold out": "\u552e\u7f44",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "\u90e8\u5206\u6216\u5168\u90e8\u9580\u7968\u985e\u5225\u76ee\u524d\u5df2\u552e\u7f44\u3002\u5982\u679c\u9700\u8981\uff0c\u4f60\u53ef\u4ee5\u5c07\u81ea\u5df1\u6dfb\u52a0\u5230\u7b49\u5019\u540d\u55ae\u4e2d\u3002\u7136\u5f8c\uff0c\u6211\u5011\u5c07\u901a\u77e5\u4f60\u662f\u5426\u6709\u7a7a\u4f4d\u3002",
    "widget\u0004The cart could not be created. Please try again later": "\u7121\u6cd5\u5275\u7acb\u8cfc\u7269\u8eca\u3002\u8acb\u7a0d\u5f8c\u91cd\u8a66",
    "widget\u0004The ticket shop could not be loaded.": "\u552e\u7968\u8655\u7121\u6cd5\u8f09\u5165\u3002",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "\u76ee\u524d\u9019\u500b\u552e\u7968\u8655\u6709\u5f88\u591a\u4f7f\u7528\u8005\u3002\u8acb\u5728\u65b0\u9078\u9805\u4e2d\u6253\u958b\u5546\u5e97\u4ee5\u4fbf\u7e7c\u7e8c\u3002",
    "widget\u0004Voucher code": "\u512a\u60e0\u5238\u4ee3\u78bc",
    "widget\u0004Waiting list": "\u5019\u88dc\u540d\u55ae",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "\u6211\u5011\u7121\u6cd5\u5efa\u7acb\u4f60\u7684\u8cfc\u7269\u8eca\uff0c\u56e0\u70ba\u6b64\u552e\u7968\u8655\u76ee\u524d\u6709\u592a\u591a\u4f7f\u7528\u8005\u3002\u8acb\u6309\u5169\u4e0b\u7e7c\u7e8c\u300c\u5728\u65b0\u9078\u9805\u4e2d\u91cd\u8a66\u300d\u3002",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "\u4f60\u7576\u524d\u6709\u6b64\u6d3b\u52d5\u7684\u6d3b\u52d5\u8cfc\u7269\u8eca\u3002\u5982\u679c\u4f60\u9078\u64c7\u66f4\u591a\u7522\u54c1\uff0c\u5c07\u6703\u88ab\u6dfb\u52a0\u5230\u4f60\u73fe\u6709\u7684\u8cfc\u7269\u8eca\u4e2d\u3002",
    "widget\u0004currently available: %s": "\u7576\u524d\u53ef\u7528\uff1a %s",
    "widget\u0004from %(currency)s %(price)s": "\u5f9e %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "\u5305\u542b. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "\u542b\u7a05",
    "widget\u0004minimum amount to order: %s": "\u6700\u4f4e\u8a02\u8cfc\u91d1\u984d\uff1a %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "\u52a0\u4e0a%(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "\u9644\u52a0\u7a05"
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

