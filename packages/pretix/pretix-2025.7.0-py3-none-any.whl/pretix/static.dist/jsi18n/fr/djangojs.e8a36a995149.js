

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n > 1;
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
      "(une date en plus)",
      "({num} plus de dates)"
    ],
    "=": "=",
    "Add condition": "Ajouter une condition",
    "Additional information required": "Plus d'informations requises",
    "All": "Tous",
    "All of the conditions below (AND)": "Toutes les conditions suivantes (ET)",
    "An error has occurred.": "Une erreur s'est produite.",
    "An error of type {code} occurred.": "Une erreur de type {code} s'est produite.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "En attente d'approbation",
    "April": "Avril",
    "At least one of the conditions below (OR)": "Au moins une des conditions suivantes (OU)",
    "August": "Ao\u00fbt",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "Zone de code-barres",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Calcul du prix par d\u00e9faut \u2026",
    "Cancel": "Annuler",
    "Canceled": "Annul\u00e9",
    "Cart expired": "Panier expir\u00e9",
    "Check-in QR": "Enregistrement QR code",
    "Checked-in Tickets": "Billets enregistr\u00e9s",
    "Click to close": "Cliquez pour fermer",
    "Close message": "Fermer le message",
    "Comment:": "Commentaire :",
    "Confirmed": "Confirm\u00e9",
    "Confirming your payment \u2026": "Confirmation de votre paiement\u2026",
    "Contacting Stripe \u2026": "Communication avec Stripe \u2026",
    "Contacting your bank \u2026": "Communication avec votre banque \u2026",
    "Continue": "Continuer",
    "Copied!": "Copi\u00e9 !",
    "Count": "Compter",
    "Credit Card": "Carte de cr\u00e9dit",
    "Current date and time": "Date et heure actuelle",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Jour courant de la semaine (1 = Lundi, 7 = Dimanche)",
    "Current entry status": "Statut actuel de l'entr\u00e9e",
    "Currently inside": "Actuellement \u00e0 l'int\u00e9rieur",
    "December": "D\u00e9cembre",
    "Do you really want to leave the editor without saving your changes?": "Voulez-vous vraiment quitter l'\u00e9diteur sans sauvegarder vos modifications ?",
    "Do you want to renew the reservation period?": "Souhaitez-vous renouveler la p\u00e9riode de r\u00e9servation ?",
    "Duplicate": "Doublon",
    "Enter page number between 1 and %(max)s.": "Saisir le num\u00e9ro de page entre 1 et %(max)s.",
    "Entry": "Entr\u00e9e",
    "Entry not allowed": "Entr\u00e9e non autoris\u00e9e",
    "Error while uploading your PDF file, please try again.": "Erreur lors du t\u00e9l\u00e9chargement de votre fichier PDF, veuillez r\u00e9essayer.",
    "Event admission": "Admission \u00e0 l'\u00e9v\u00e9nement",
    "Event end": "Fin de l'\u00e9v\u00e9nement",
    "Event start": "D\u00e9but de l'\u00e9v\u00e9nement",
    "Exit": "Quitter",
    "Exit recorded": "Sortie enregistr\u00e9e",
    "February": "F\u00e9vrier",
    "Fr": "Ve",
    "Friday": "Vendredi",
    "Gate": "Pont",
    "Generating messages \u2026": "Cr\u00e9ation de messages \u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Groupe d'objets",
    "If this takes longer than a few minutes, please contact us.": "Si cela prend plus de quelques minutes, veuillez nous contacter.",
    "Image area": "Zone d'image",
    "Information required": "Informations n\u00e9cessaires",
    "Invalid page number.": "Num\u00e9ro de page invalide.",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Janvier",
    "July": "Juillet",
    "June": "Juin",
    "Load more": "Charger plus",
    "March": "Mars",
    "Marked as paid": "Marqu\u00e9 comme pay\u00e9",
    "Maxima": "Maxima",
    "May": "Mai",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minutes depuis la premi\u00e8re entr\u00e9e (-1 \u00e0 la premi\u00e8re entr\u00e9e)",
    "Minutes since last entry (-1 on first entry)": "Minutes depuis la derni\u00e8re entr\u00e9e (-1 \u00e0 la premi\u00e8re entr\u00e9e)",
    "Mo": "Lu",
    "Monday": "Lundi",
    "MyBank": "MyBank",
    "No": "Non",
    "No active check-in lists found.": "Aucune liste d'enregistrement active n'a \u00e9t\u00e9 trouv\u00e9e.",
    "No results": "Aucun r\u00e9sultat",
    "No tickets found": "Pas de billets trouv\u00e9s",
    "None": "Aucun",
    "November": "Novembre",
    "Number of days with a previous entry": "Nombre de jours avec entr\u00e9e pr\u00e9alable",
    "Number of days with a previous entry before": "Nombre de jours avec entr\u00e9e pr\u00e9alable avant",
    "Number of days with a previous entry since": "Nombre de jours avec entr\u00e9e pr\u00e9alable depuis",
    "Number of previous entries": "Nombre d'entr\u00e9es pr\u00e9c\u00e9dentes",
    "Number of previous entries before": "Nombre d'entr\u00e9es pr\u00e9c\u00e9dentes avant",
    "Number of previous entries since": "Nombre d'entr\u00e9es pr\u00e9c\u00e9dentes depuis",
    "Number of previous entries since midnight": "Nombre d'entr\u00e9es depuis minuit",
    "OXXO": "OXXO",
    "Object": "Objet",
    "October": "Octobre",
    "Order canceled": "Commande annul\u00e9e",
    "Order not approved": "Commande non valid\u00e9e",
    "Others": "Autres",
    "Paid orders": "Commandes pay\u00e9es",
    "PayPal": "PayPal",
    "PayPal Credit": "PayPal Credit",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "M\u00e9thode de paiement non disponible",
    "Placed orders": "Commandes r\u00e9alis\u00e9es",
    "Please enter the amount the organizer can keep.": "Veuillez indiquer le montant que l'organisateur est autoris\u00e9 \u00e0 retenir.",
    "Powered by pretix": "Propuls\u00e9 par pretix",
    "Press Ctrl-C to copy!": "Appuyez sur Ctrl-C pour copier !",
    "Product": "Produit",
    "Product variation": "Variation du produit",
    "Przelewy24": "Przelewy24",
    "Redeemed": "\u00c9chang\u00e9",
    "Renew reservation": "Renouveler la r\u00e9servation",
    "Result": "R\u00e9sultat",
    "SEPA Direct Debit": "Mandat SEPA",
    "SOFORT": "SOFORT",
    "Sa": "Sa",
    "Saturday": "Samedi",
    "Saving failed.": "L'enregistrement a \u00e9chou\u00e9.",
    "Scan a ticket or search and press return\u2026": "Scanner ou rechercher le ticket et confirmer avec Entr\u00e9e\u2026",
    "Search query": "Requ\u00eate de recherche",
    "Search results": "R\u00e9sultats de la recherche",
    "Select a check-in list": "Choisis une liste d'enregistrement",
    "Selected only": "Seuls les s\u00e9lectionn\u00e9s",
    "September": "Septembre",
    "Su": "Di",
    "Sunday": "Dimanche",
    "Switch check-in list": "Changer de liste d'enregistrement",
    "Switch direction": "Changer la direction",
    "Text box": "Zone de texte",
    "Text object (deprecated)": "Objet textuel (obsol\u00e8te)",
    "Th": "Je",
    "The PDF background file could not be loaded for the following reason:": "Le fichier PDF g\u00e9n\u00e9r\u00e9 en arri\u00e8re-plan n'a pas pu \u00eatre charg\u00e9 pour la raison suivante :",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they're available.": "Les articles de votre panier ne vous sont plus r\u00e9serv\u00e9s. Vous pouvez encore compl\u00e9ter votre commande tant qu'ils sont disponibles.",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Les articles de votre panier ne vous sont plus r\u00e9serv\u00e9s. Vous pouvez toujours compl\u00e9ter votre commande tant qu'ils sont disponibles.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Les articles de votre panier sont r\u00e9serv\u00e9s pour une minute.",
      "Les articles de votre panier sont r\u00e9serv\u00e9s pendant {num} minutes."
    ],
    "The organizer keeps %(currency)s %(amount)s": "L'organisateur retient %(currency)s %(amount)s",
    "The request took too long. Please try again.": "La requ\u00eate a prit trop de temps. Veuillez r\u00e9essayer.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Ce billet n'a pas encore \u00e9t\u00e9 pay\u00e9. Continuer quand m\u00eame\u202f?",
    "This ticket requires special attention": "Ce ticket n\u00e9cessite une attention particuli\u00e8re",
    "Thursday": "Jeudi",
    "Ticket already used": "Billet d\u00e9j\u00e0 utilis\u00e9",
    "Ticket blocked": "Billet bloqu\u00e9",
    "Ticket code is ambiguous on list": "Le code du billet est ambigu dans la liste",
    "Ticket code revoked/changed": "Code de billet bloqu\u00e9/modifi\u00e9",
    "Ticket design": "Conception des billets",
    "Ticket not paid": "Ticket non pay\u00e9",
    "Ticket not valid at this time": "Billet non valable pour le moment",
    "Ticket type not allowed here": "Type de billet non autoris\u00e9 ici",
    "Tolerance (minutes)": "Tol\u00e9rance (minutes)",
    "Total": "Total",
    "Total revenue": "Total des revenus",
    "Trustly": "Trustly",
    "Tu": "Ma",
    "Tuesday": "Mardi",
    "Unknown error.": "Erreur inconnue.",
    "Unknown ticket": "Billet inconnu",
    "Unpaid": "Non pay\u00e9",
    "Use a different name internally": "Utiliser un nom diff\u00e9rent en interne",
    "Valid": "Valide",
    "Valid Tickets": "Billets valides",
    "Valid ticket": "Billet valide",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Me",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Nous envoyons actuellement votre demande au serveur. Si cela prend plus d'une minute, veuillez v\u00e9rifier votre connexion Internet, puis recharger cette page et r\u00e9essayer.",
    "We are processing your request \u2026": "Nous traitons votre demande \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Nous ne pouvons actuellement pas atteindre le serveur, mais nous continuons d'essayer. Dernier code d'erreur\u202f: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Actuellement, nous ne pouvons pas atteindre le serveur. Veuillez r\u00e9essayer. Code d'erreur\u202f: {code}",
    "WeChat Pay": "WeChat Pay",
    "Wednesday": "Mercredi",
    "Yes": "Oui",
    "You get %(currency)s %(amount)s back": "Vous recevez en retour %(currency)s %(amount)s",
    "You have unsaved changes!": "Vous avez des modifications non sauvegard\u00e9es !",
    "Your cart has expired.": "Votre panier a expir\u00e9.",
    "Your cart is about to expire.": "Votre panier est sur le point d'expirer.",
    "Your color has decent contrast and is sufficient for minimum accessibility requirements.": "Votre choix de couleur est assez bon pour la lecture et offre un bon contraste.",
    "Your color has great contrast and will provide excellent accessibility.": "Votre choix de couleur a un bon contraste et il est tr\u00e8s facile \u00e0 lire.",
    "Your color has insufficient contrast to white. Accessibility of your site will be impacted.": "Votre choix de couleur n'est pas assez contrast\u00e9e par rapport au blanc. L'accessibilit\u00e9 de votre site en sera affect\u00e9e.",
    "Your local time:": "Votre heure locale\u202f:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Votre demande a \u00e9t\u00e9 mise en attente sur le serveur et sera trait\u00e9e. Si cela prend plus de deux minutes, veuillez nous contacter ou retourner dans votre navigateur et r\u00e9essayer.",
    "Your request has been queued on the server and will soon be processed.": "Votre demande a \u00e9t\u00e9 mise en attente sur le serveur et sera trait\u00e9e prochainement.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Votre demande est maintenant en cours de traitement. Selon la taille de votre \u00e9v\u00e9nement, cela peut prendre jusqu' \u00e0 quelques minutes.",
    "Zimpler": "Zimpler",
    "close": "fermer",
    "custom date and time": "date et heure personnalis\u00e9e",
    "custom time": "heure personnalis\u00e9e",
    "entry_status\u0004absent": "absent",
    "entry_status\u0004present": "pr\u00e9sent",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "est apr\u00e8s",
    "is before": "est avant",
    "is one of": "est l'un des",
    "minutes": "minutes",
    "required": "obligatoire",
    "widget\u0004Back": "Retour",
    "widget\u0004Buy": "Acheter",
    "widget\u0004Checkout": "Finaliser ma commande",
    "widget\u0004Choose a different date": "Choisir une autre date",
    "widget\u0004Choose a different event": "Choisissez un autre \u00e9v\u00e9nement",
    "widget\u0004Close": "Fermer",
    "widget\u0004Close checkout": "Fermer la caisse",
    "widget\u0004Close ticket shop": "Fermer la billetterie",
    "widget\u0004Continue": "Continuer",
    "widget\u0004Currently not available": "Actuellement non disponible",
    "widget\u0004Decrease quantity": "Diminuer la quantit\u00e9",
    "widget\u0004FREE": "GRATUIT",
    "widget\u0004Filter": "Filtrer",
    "widget\u0004Filter events by": "Filtrer les \u00e9v\u00e9nements par",
    "widget\u0004Hide variants": "Masquer les variantes",
    "widget\u0004Image of %s": "Image de %s",
    "widget\u0004Increase quantity": "Augmenter la quantit\u00e9",
    "widget\u0004Load more": "Charger plus",
    "widget\u0004New price: %s": "Nouveau prix : %s",
    "widget\u0004Next month": "Mois suivant",
    "widget\u0004Next week": "La semaine prochaine",
    "widget\u0004Not available anymore": "Plus disponible",
    "widget\u0004Not yet available": "Pas encore disponible",
    "widget\u0004Only available with a voucher": "Disponible avec un bon de r\u00e9duction",
    "widget\u0004Open seat selection": "Ouvrir la s\u00e9lection de si\u00e8ges",
    "widget\u0004Open ticket shop": "Ouvrir la billetterie",
    "widget\u0004Original price: %s": "Prix initial : %s",
    "widget\u0004Previous month": "Moins pr\u00e9c\u00e9dent",
    "widget\u0004Previous week": "Semaine pr\u00e9c\u00e9dente",
    "widget\u0004Price": "Prix",
    "widget\u0004Quantity": "Quantit\u00e9",
    "widget\u0004Redeem": "Echanger",
    "widget\u0004Redeem a voucher": "Utiliser un bon d'achat",
    "widget\u0004Register": "S'enregistrer",
    "widget\u0004Reserved": "R\u00e9serv\u00e9",
    "widget\u0004Resume checkout": "Finaliser ma commande",
    "widget\u0004Select": "S\u00e9lectionner",
    "widget\u0004Select %s": "S\u00e9lectionn\u00e9 %s",
    "widget\u0004Select variant %s": "S\u00e9lectionner les variations %s",
    "widget\u0004Show variants": "Afficher les variantes",
    "widget\u0004Sold out": "Epuis\u00e9",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Certaines ou toutes les cat\u00e9gories de billets sont actuellement \u00e9puis\u00e9es. Si vous le souhaitez, vous pouvez vous ajouter \u00e0 la liste d\u2019attente. Nous vous informerons alors si des places sont \u00e0 nouveau disponibles.",
    "widget\u0004The cart could not be created. Please try again later": "Le panier n' a pas pu \u00eatre cr\u00e9\u00e9. Veuillez r\u00e9essayer plus tard",
    "widget\u0004The ticket shop could not be loaded.": "La billetterie n' a pas pu \u00eatre charg\u00e9e.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Il y a actuellement beaucoup d'utilisateurs dans cette boutique de billets. Veuillez ouvrir cette boutique de billets dans un nouvel onglet pour continuer.",
    "widget\u0004Voucher code": "Code de r\u00e9duction",
    "widget\u0004Waiting list": "Liste d'attente",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Nous n'avons pas pu cr\u00e9er vore panier, car il y a actuellement trop d'utilisateurs dans cette boutique de billets. Veuillez cliquer sur \"Continuer\" pour r\u00e9essayer dans un nouvel onglet.",
    "widget\u0004You cannot cancel this operation. Please wait for loading to finish.": "Vous ne pouvez pas annuler cette op\u00e9ration. Veuillez attendre la fin du chargement.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Vous avez actuellement un panier actif pour cet \u00e9v\u00e9nement. Si vous s\u00e9lectionnez d'autres produits, ils seront ajout\u00e9s \u00e0 votre panier.",
    "widget\u0004currently available: %s": "actuellement disponible\u202f: %s",
    "widget\u0004from %(currency)s %(price)s": "de %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "dont %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "taxes incluses",
    "widget\u0004minimum amount to order: %s": "quantit\u00e9 minimum \u00e0 commander\u202f: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "taxes en sus"
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
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j N Y H:i",
    "SHORT_DATE_FORMAT": "j N Y",
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

