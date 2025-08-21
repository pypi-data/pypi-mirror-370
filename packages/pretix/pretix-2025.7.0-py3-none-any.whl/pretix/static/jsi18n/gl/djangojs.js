

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
      "(unha data m\u00e1is)",
      "({num} m\u00e1is datas)"
    ],
    "Add condition": "Engadir condici\u00f3n",
    "Additional information required": "Requ\u00edrese informaci\u00f3n adicional",
    "All": "Todos",
    "All of the conditions below (AND)": "Todas as condici\u00f3ns seguintes (E)",
    "An error has occurred.": "Houbo un erro.",
    "An error of type {code} occurred.": "Ocurreu un error de tipo {code}.",
    "April": "Abril",
    "At least one of the conditions below (OR)": "Polo menos unha das seguintes condici\u00f3ns (OU)",
    "August": "Agosto",
    "Barcode area": "\u00c1rea para c\u00f3digo de barras",
    "Calculating default price\u2026": "Calculando o prezo por defecto\u2026",
    "Cancel": "Cancelar",
    "Canceled": "Cancelado",
    "Cart expired": "O carro da compra caducou",
    "Check-in QR": "QR de validaci\u00f3n",
    "Checked-in Tickets": "Rexistro de c\u00f3digo QR",
    "Click to close": "Click para cerrar",
    "Close message": "Cerrar mensaxe",
    "Comment:": "Comentario:",
    "Confirming your payment \u2026": "Confirmando o pagamento\u2026",
    "Contacting Stripe \u2026": "Contactando con Stripe\u2026",
    "Contacting your bank \u2026": "Contactando co banco\u2026",
    "Continue": "Continuar",
    "Copied!": "Copiado!",
    "Count": "Cantidade",
    "Current date and time": "Data e hora actual",
    "Currently inside": "Actualmente dentro",
    "December": "Decembro",
    "Do you really want to leave the editor without saving your changes?": "Realmente desexa sa\u00edr do editor sen gardar os cambios?",
    "Entry": "Acceso",
    "Entry not allowed": "Entrada non permitida",
    "Error while uploading your PDF file, please try again.": "Houbo un erro mentres se cargaba o arquivo PDF. Por favor, int\u00e9nteo de novo.",
    "Event admission": "Admisi\u00f3n ao evento",
    "Event end": "Fin do evento",
    "Event start": "Comezo do evento",
    "Exit": "Sa\u00edda",
    "Exit recorded": "Sa\u00edda rexistrada",
    "February": "Febreiro",
    "Fr": "Ve",
    "Generating messages \u2026": "Xerando mensaxes\u2026",
    "Group of objects": "Grupo de obxectos",
    "Image area": "\u00c1rea de imaxe",
    "Information required": "Informaci\u00f3n requirida",
    "January": "Xaneiro",
    "July": "Xullo",
    "June": "Xu\u00f1o",
    "Load more": "Cargar m\u00e1is",
    "March": "Marzo",
    "Marked as paid": "Marcado como pagado",
    "May": "Maio",
    "Mo": "Lu",
    "No": "Non",
    "No active check-in lists found.": "Non se atoparon listas de rexistro activas.",
    "No tickets found": "Non se atoparon t\u00edckets",
    "None": "Ning\u00fan",
    "November": "Novembro",
    "Number of days with a previous entry": "N\u00famero de d\u00edas cunha entrada previa",
    "Number of previous entries": "N\u00famero de entradas previas",
    "Number of previous entries since midnight": "N\u00famero de entradas previas desde a medianoite",
    "Object": "Obxecto",
    "October": "Outubro",
    "Order canceled": "Pedido cancelado",
    "Others": "Outros",
    "Paid orders": "Pedidos pagados",
    "Placed orders": "Pedidos enviados",
    "Please enter the amount the organizer can keep.": "Por favor, ingrese a cantidade que pode conservar o organizador.",
    "Powered by pretix": "Desenvolto por Pretix",
    "Press Ctrl-C to copy!": "Presione Control+C para copiar!",
    "Product": "Produto",
    "Product variation": "Ver variaci\u00f3ns do produto",
    "Redeemed": "Trocado",
    "Result": "Resultado",
    "Sa": "S\u00e1b",
    "Saving failed.": "O gardado fallou.",
    "Scan a ticket or search and press return\u2026": "Escanee o t\u00edcket ou busque e presione volver\u2026",
    "Search query": "Consultar unha procura",
    "Search results": "Resultados da procura",
    "Select a check-in list": "Seleccione unha lista de rexistro",
    "Selected only": "Soamente seleccionados",
    "September": "Setembro",
    "Su": "Dom",
    "Switch check-in list": "Cambiar a lista de rexistro",
    "Switch direction": "Cambiar enderezo",
    "Th": "Xo",
    "The PDF background file could not be loaded for the following reason:": "O arquivo PDF de fondo non se puido cargar polo motivo seguinte:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Os artigos da t\u00faa cesta xa non est\u00e1n reservados para ti. A\u00ednda podes completar o teu pedido mentres estean dispo\u00f1ibles.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Os artigos da t\u00faa cesta est\u00e1n reservados para ti durante un minuto.",
      "Os artigos da t\u00faa cesta est\u00e1n reservados para ti durante {num} minutos."
    ],
    "The organizer keeps %(currency)s %(amount)s": "O organizador queda %(currency)s %(price)s",
    "The request took too long. Please try again.": "A petici\u00f3n levou demasiado tempo. Int\u00e9nteo de novo.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Este t\u00edcket a\u00ednda non se pagou. Desexa continuar de todos os xeitos?",
    "This ticket requires special attention": "Este t\u00edcket require atenci\u00f3n especial",
    "Ticket already used": "Este t\u00edcket xa foi utilizado",
    "Ticket code revoked/changed": "C\u00f3digo de t\u00edcket revogado/cambiado",
    "Ticket design": "Dese\u00f1o do t\u00edcket",
    "Ticket not paid": "T\u00edcket pendente de pago",
    "Ticket type not allowed here": "Tipo de t\u00edcket non permitido",
    "Tolerance (minutes)": "Tolerancia (en minutos)",
    "Total": "Total",
    "Total revenue": "Ingresos totais",
    "Tu": "Mar",
    "Unknown error.": "Erro desco\u00f1ecido.",
    "Unknown ticket": "T\u00edcket desco\u00f1ecido",
    "Unpaid": "Sen pagar",
    "Use a different name internally": "Usar un nome diferente internamente",
    "Valid": "V\u00e1lido",
    "Valid Tickets": "T\u00edckets v\u00e1lidos",
    "Valid ticket": "Entrada v\u00e1lida",
    "We": "M\u00e9r",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Estamos enviando a s\u00faa solicitude ao servidor. Se este proceso tarda m\u00e1is dun minuto, por favor, revise a s\u00faa conexi\u00f3n a Internet, recargue a p\u00e1xina e int\u00e9nteo de novo.",
    "We are processing your request \u2026": "Estamos procesando a s\u00faa solicitude\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Agora mesmo non podemos contactar co servidor, pero segu\u00edmolo intentando. O \u00faltimo c\u00f3digo de erro foi: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Agora mesmo non podemos contactar co servidor. Por favor, int\u00e9nteo de novo. C\u00f3digo de erro: {code}",
    "Yes": "Si",
    "You get %(currency)s %(amount)s back": "Obt\u00e9s %(currency)s %(price)s de volta",
    "You have unsaved changes!": "Tes cambios sen gardar!",
    "Your local time:": "A s\u00faa hora local:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "A s\u00faa solicitude chegou ao servidor pero seguimos esperando a que sexa procesada. Se tarda m\u00e1is de dous minutos, por favor, contacte con n\u00f3s ou volva \u00e1 p\u00e1xina anterior no seu navegador e int\u00e9nteo de novo.",
    "Your request has been queued on the server and will soon be processed.": "A s\u00faa solicitude foi enviada ao servidor e ser\u00e1 procesada en breve.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "A s\u00faa solicitude estase procesando. Isto pode tardar varios minutos, dependendo do tama\u00f1o do seu evento.",
    "close": "cerrar",
    "custom date and time": "Seleccionar data e hora",
    "custom time": "Seleccionar hora",
    "is after": "est\u00e1 despois",
    "is before": "est\u00e1 antes",
    "is one of": "\u00e9 un de",
    "minutes": "minutos",
    "required": "campo requirido",
    "widget\u0004Back": "Atr\u00e1s",
    "widget\u0004Buy": "Mercar",
    "widget\u0004Choose a different date": "Elixir unha data diferente",
    "widget\u0004Choose a different event": "Elixir un evento distinto",
    "widget\u0004Close": "Cerrar",
    "widget\u0004Close ticket shop": "Cerrar a tenda de t\u00edckets",
    "widget\u0004Continue": "Continuar",
    "widget\u0004FREE": "De balde",
    "widget\u0004Load more": "Cargar m\u00e1is",
    "widget\u0004Next month": "Mes seguinte",
    "widget\u0004Next week": "Semana seguinte",
    "widget\u0004Only available with a voucher": "S\u00f3 dispo\u00f1ible mediante vale",
    "widget\u0004Open seat selection": "Abrir selecci\u00f3n de asentos",
    "widget\u0004Open ticket shop": "Abrir a tenda de t\u00edckets",
    "widget\u0004Previous month": "Mes anterior",
    "widget\u0004Previous week": "Semana anterior",
    "widget\u0004Redeem": "Trocar",
    "widget\u0004Redeem a voucher": "Trocar un vale",
    "widget\u0004Register": "Rexistrarse",
    "widget\u0004Reserved": "Reservado",
    "widget\u0004Resume checkout": "Continuar co pagamento",
    "widget\u0004Sold out": "Esgotado",
    "widget\u0004The cart could not be created. Please try again later": "O carro de compras non se puido crear. Por favor, int\u00e9nteo de novo m\u00e1is tarde",
    "widget\u0004The ticket shop could not be loaded.": "Non se puido cargar a tenda de t\u00edckets.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Actualmente hai moitas persoas usuarias na tenda de t\u00edckets. Por favor, abra a tenda nunha nova pestana para continuar.",
    "widget\u0004Voucher code": "C\u00f3digo do cup\u00f3n",
    "widget\u0004Waiting list": "Lista de agarda",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "Non puidemos crear o seu carro debido a que hai moitas persoas usuarias na tenda. Por favor, presione \"Continuar\" para intentalo nunha nova pestana.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Xa ten un carro de compras activo para este evento. Se selecciona m\u00e1is produtos, estes engadiranse ao carro actual.",
    "widget\u0004currently available: %s": "dispo\u00f1ible actualmente: %s",
    "widget\u0004from %(currency)s %(price)s": "dende %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "incl\u00fae %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "impostos inclu\u00eddos",
    "widget\u0004minimum amount to order: %s": "cantidade m\u00ednima de pedido: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "m\u00e1is %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "m\u00e1is impostos"
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
    "DATETIME_FORMAT": "j \\d\\e F \\d\\e Y \\\u00e1\\s H:i",
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
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y",
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
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j \\d\\e F",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "d-m-Y, H:i",
    "SHORT_DATE_FORMAT": "d-m-Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F \\d\\e Y"
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

