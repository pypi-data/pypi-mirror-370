

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
      "(mais uma data)",
      "(mais {num} datas)"
    ],
    "Add condition": "Adicionar condi\u00e7\u00e3o",
    "Additional information required": "Informa\u00e7\u00e3o adicional necess\u00e1ria",
    "All": "Tudo",
    "All of the conditions below (AND)": "Todas as condi\u00e7\u00f5es abaixo (E)",
    "An error has occurred.": "Um erro ocorreu.",
    "An error of type {code} occurred.": "Um erro do tipo {code} ocorreu.",
    "Apple Pay": "Apple Pay",
    "April": "Abril",
    "At least one of the conditions below (OR)": "Pelo menos uma das condi\u00e7\u00f5es abaixo (Ou)",
    "August": "Agosto",
    "Bancontact": "Contato banc\u00e1rio",
    "Barcode area": "\u00c1rea do c\u00f3digo de barras",
    "Calculating default price\u2026": "A calcular diferen\u00e7a de pre\u00e7o\u2026",
    "Cart expired": "Carrinho expirado",
    "Check-in QR": "Check-in QR",
    "Click to close": "Clique para fechar",
    "Close message": "Fechar mensagem",
    "Comment:": "Comentario:",
    "Confirming your payment \u2026": "A confirmar o seu pagamento\u2026",
    "Contacting Stripe \u2026": "A contactar o Stripe\u2026",
    "Contacting your bank \u2026": "A contactar o seu banco\u2026",
    "Copied!": "Copiado!",
    "Count": "Contagem",
    "Credit Card": "Cart\u00e3o de cr\u00e9dito",
    "Current date and time": "Data e hora atual",
    "December": "Dezembro",
    "Do you really want to leave the editor without saving your changes?": "Quer mesmo deixar o editor sem guardar as suas altera\u00e7\u00f5es?",
    "Error while uploading your PDF file, please try again.": "Erro ao carregar o seu ficheiro PDF, por favor tente novamente.",
    "Event admission": "Admiss\u00e3o ao evento",
    "Event end": "Fim do evento",
    "Event start": "In\u00edcio do evento",
    "February": "Fevereiro",
    "Fr": "Sex",
    "Generating messages \u2026": "A gerar mensagens\u2026",
    "Group of objects": "Grupo de objectos",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Janeiro",
    "July": "Julho",
    "June": "Junho",
    "March": "Mar\u00e7o",
    "Marked as paid": "Marcar como pago",
    "May": "Maio",
    "Mercado Pago": "Mercado Pago",
    "Mo": "Seg",
    "MyBank": "MyBank",
    "No": "N\u00e3o",
    "None": "Nada",
    "November": "Novembro",
    "Number of days with a previous entry": "N\u00famero de dias com entrada pr\u00e9via",
    "Number of previous entries": "N\u00famero de entradas anteriores",
    "Number of previous entries since midnight": "N\u00famero de entradas pr\u00e9vias desde a meia noite",
    "Object": "Objecto",
    "October": "Outubro",
    "Others": "Outros",
    "Paid orders": "Encomendas pagas",
    "PayPal": "PayPal",
    "PayPal Credit": "Cr\u00e9dito PayPal",
    "PayPal Pay Later": "PayPal Pagar Depois",
    "Placed orders": "Encomendas colocadas",
    "Please enter the amount the organizer can keep.": "Por favor insira o montante com que a organiza\u00e7\u00e3o pode ficar.",
    "Powered by pretix": "Powered by pretix",
    "Press Ctrl-C to copy!": "Pressione Ctrl-C para copiar!",
    "Product": "Produto",
    "Product variation": "Varia\u00e7\u00e3o do produto",
    "Przelewy24": "Przelewy24",
    "SEPA Direct Debit": "D\u00e9bito Direto SEPA",
    "SOFORT": "SOFORT",
    "Sa": "S\u00e1b",
    "Saving failed.": "Salvar falhou.",
    "September": "Setembro",
    "Su": "Dom",
    "Th": "Qui",
    "The PDF background file could not be loaded for the following reason:": "O ficheiro de fundo PDF n\u00e3o p\u00f4de ser carregado pela seguinte raz\u00e3o:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Os itens no seu carrinho j\u00e1 n\u00e3o est\u00e3o mais reservados para voc\u00ea. Voc\u00ea ainda pode finalizar o seu pedido, desde que eles estejam dispon\u00edveis.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Os artigos no seu carrinho est\u00e3o reservados para voc\u00ea por um minuto.",
      "Os artigos no seu carrinho est\u00e3o reservados para voc\u00ea por {num} minutos."
    ],
    "The organizer keeps %(currency)s %(amount)s": "O organizador mant\u00e9m %(currency)s %(amount)s",
    "The request took too long. Please try again.": "O pedido demorou demasiado. Por favor tente novamente.",
    "Ticket design": "Design do Bilhete",
    "Ticket type not allowed here": "Tipo de bilhete n\u00e3o \u00e9 permitido aqui",
    "Tolerance (minutes)": "Toler\u00e2ncia (minutos)",
    "Total": "Total",
    "Total revenue": "Total de receitas",
    "Tu": "Ter",
    "Unknown error.": "Erro desconhecido.",
    "Unknown ticket": "Bilhete desconhecido",
    "Use a different name internally": "Use um nome interno diferente",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Qua",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Estamos neste momento a enviar o seu pedido para o servidor. Se demorar mais de um minuto, verifique a sua liga\u00e7\u00e3o \u00e0 Internet e, em seguida, recarregue esta p\u00e1gina e tente novamente.",
    "We are processing your request \u2026": "Estamos processando o seu pedido \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Atualmente n\u00e3o conseguimos chegar ao servidor, mas continuamos a tentar. \u00daltimo c\u00f3digo de erro: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Atualmente n\u00e3o conseguimos chegar ao servidor. Por favor tente outra vez. C\u00f3digo de erro: {code}",
    "Yes": "Sim",
    "You get %(currency)s %(amount)s back": "Recebes %(currency)s %(amount)s de volta",
    "You have unsaved changes!": "Tem altera\u00e7\u00f5es por guardar!",
    "Your local time:": "Sua hora local:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "O seu pedido chegou ao servidor, mas ainda aguardamos que seja processado. Se demorar mais de dois minutos, entre em contato connosco ou volte ao seu navegador e tente novamente.",
    "Your request has been queued on the server and will soon be processed.": "O seu pedido est\u00e1 na fila no servidor e em breve ser\u00e1 processado.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "O seu pedido est\u00e1 a ser processado. Dependendo do tamanho do seu evento, isto pode demorar alguns minutos.",
    "custom time": "Hora personalisada",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "\u00e9 depois de",
    "is before": "\u00e9 antes de",
    "is one of": "\u00e9 um de",
    "minutes": "minutos",
    "widget\u0004Back": "Voltar atr\u00e1s",
    "widget\u0004Buy": "Comprar",
    "widget\u0004Choose a different date": "Escolha uma data diferente",
    "widget\u0004Choose a different event": "Escolha um evento diferente",
    "widget\u0004Close": "Fechar",
    "widget\u0004Close ticket shop": "Fechar bilheteira",
    "widget\u0004Continue": "Continuar",
    "widget\u0004FREE": "GR\u00c1TIS",
    "widget\u0004Next month": "Pr\u00f3ximo m\u00eas",
    "widget\u0004Next week": "Pr\u00f3xima semana",
    "widget\u0004Only available with a voucher": "Apenas dispon\u00edvel com um voucher",
    "widget\u0004Open seat selection": "Abrir sele\u00e7\u00e3o de lugares",
    "widget\u0004Previous month": "M\u00eas anterior",
    "widget\u0004Previous week": "Semana anterior",
    "widget\u0004Redeem": "Redimir",
    "widget\u0004Redeem a voucher": "Usar um voucher",
    "widget\u0004Register": "Registar",
    "widget\u0004Reserved": "Reservado",
    "widget\u0004Resume checkout": "Voltar ao checkout",
    "widget\u0004Select": "Selecionar",
    "widget\u0004Select %s": "Selecionados %s",
    "widget\u0004Select variant %s": "Selecione variantes %s",
    "widget\u0004Sold out": "Esgotado",
    "widget\u0004The cart could not be created. Please try again later": "O carrinho n\u00e3o p\u00f4de ser criado. Por favor, tente de novo mais tarde",
    "widget\u0004The ticket shop could not be loaded.": "N\u00e3o conseguimos carregar a bilheteira.",
    "widget\u0004Voucher code": "C\u00f3digo do voucher",
    "widget\u0004Waiting list": "Lista de espera",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Atualmente tem um carrinho ativo para este evento. Se selecionar mais produtos, ser\u00e3o adicionados ao seu carrinho existente.",
    "widget\u0004currently available: %s": "atualmente dispon\u00edveis: %s",
    "widget\u0004from %(currency)s %(price)s": "de %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "incl. %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "inc. impostos",
    "widget\u0004minimum amount to order: %s": "montante m\u00ednimo a encomendar: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "mais %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "mais impostos"
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
    "DATETIME_FORMAT": "j \\d\\e F \\d\\e Y \u00e0\\s H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M:%S",
      "%d/%m/%y %H:%M:%S.%f",
      "%d/%m/%y %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%d/%m/%Y",
      "%d/%m/%y"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "j \\d\\e F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d/m/Y H:i",
    "SHORT_DATE_FORMAT": "d/m/Y",
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

