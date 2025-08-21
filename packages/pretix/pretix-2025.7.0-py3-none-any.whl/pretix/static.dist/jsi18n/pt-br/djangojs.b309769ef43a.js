

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
      "({num} mais datas)"
    ],
    "=": "=",
    "Add condition": "Adicionar condi\u00e7\u00e3o",
    "Additional information required": "Informa\u00e7\u00f5es adicionais necess\u00e1rias",
    "All": "Todos",
    "All of the conditions below (AND)": "Todas as condi\u00e7\u00f5es abaixo (E)",
    "An error has occurred.": "Um erro ocorreu.",
    "An error of type {code} occurred.": "Ocorreu um erro do tipo {code}.",
    "Apple Pay": "Apple Pay",
    "Approval pending": "Aprova\u00e7\u00e3o pendente",
    "April": "Abril",
    "At least one of the conditions below (OR)": "Pelo menos uma das condi\u00e7\u00f5es abaixo (OU)",
    "August": "Agosto",
    "BLIK": "BLIK",
    "Bancontact": "Bancontact",
    "Barcode area": "\u00c1rea do c\u00f3digo de barras",
    "Boleto": "Boleto",
    "Calculating default price\u2026": "Calculando o pre\u00e7o padr\u00e3o\u2026",
    "Cancel": "Cancelar",
    "Canceled": "Cancelado",
    "Cart expired": "Carrinho expirado",
    "Check-in QR": "Check-in QR Code",
    "Checked-in Tickets": "Ingressos validados",
    "Click to close": "Clique para fechar",
    "Close message": "Fechar mensagem",
    "Comment:": "Coment\u00e1rio:",
    "Confirmed": "Confirmado",
    "Confirming your payment \u2026": "Confirmado o seu pagamento  \u2026",
    "Contacting Stripe \u2026": "Contactando Stripe \u2026",
    "Contacting your bank \u2026": "Contactando o seu banco \u2026",
    "Continue": "Continuar",
    "Copied!": "Copiado!",
    "Count": "Contagem",
    "Credit Card": "Cart\u00e3o de Cr\u00e9dito",
    "Current date and time": "Data e hora atual",
    "Current day of the week (1 = Monday, 7 = Sunday)": "Dia atual da semana (1 = Segunda, 7 = Domingo)",
    "Current entry status": "Status de entrada atual",
    "Currently inside": "Atualmente dentro",
    "December": "Dezembro",
    "Do you really want to leave the editor without saving your changes?": "Voc\u00ea realmente quer deixar o editor sem salvar suas mudan\u00e7as?",
    "Duplicate": "Duplicar",
    "Enter page number between 1 and %(max)s.": "Entre um n\u00famero de p\u00e1gina entre 1 e %(max)s.",
    "Entry": "Entrada",
    "Entry not allowed": "Entrada n\u00e3o permitida",
    "Error while uploading your PDF file, please try again.": "Erro durante o envio do seu arquivo PDF. Por favor, tente novamente.",
    "Event admission": "Admiss\u00e3o ao evento",
    "Event end": "T\u00e9rmino do evento",
    "Event start": "In\u00edcio do evento",
    "Exit": "Sa\u00edda",
    "Exit recorded": "Sa\u00edda registrada",
    "February": "Fevereiro",
    "Fr": "Sex",
    "Gate": "Port\u00e3o",
    "Generating messages \u2026": "Gerando mensagens \u2026",
    "Google Pay": "Google Pay",
    "Group of objects": "Grupo de objetos",
    "Image area": "\u00c1rea de imagem",
    "Information required": "Informa\u00e7\u00e3o necess\u00e1ria",
    "Invalid page number.": "N\u00famero de p\u00e1gina inv\u00e1lido.",
    "Ita\u00fa": "Ita\u00fa",
    "January": "Janeiro",
    "July": "Julho",
    "June": "Junho",
    "Load more": "Carregar mais",
    "March": "Mar\u00e7o",
    "Marked as paid": "Marcado como pago",
    "Maxima": "Maxima",
    "May": "Maio",
    "Mercado Pago": "Mercado Pago",
    "Minutes since first entry (-1 on first entry)": "Minutos desde a primeira entrada (-1 para a primeira entrada)",
    "Minutes since last entry (-1 on first entry)": "Minutos desde a \u00faltima entrada (-1 para a primeira entrada)",
    "Mo": "Seg",
    "MyBank": "MyBank",
    "No": "N\u00e3o",
    "No active check-in lists found.": "Nenhuma lista de check-in encontrada.",
    "No tickets found": "Nenhum ingresso encontrado",
    "None": "Nenhum",
    "November": "Novembro",
    "Number of days with a previous entry": "N\u00famero de dias com uma entrada anterior",
    "Number of days with a previous entry before": "N\u00famero de dias com uma entrada anterior antes",
    "Number of days with a previous entry since": "N\u00famero de dias com uma entrada anterior desde",
    "Number of previous entries": "N\u00famero de entradas anteriores",
    "Number of previous entries before": "N\u00famero de entradas anteriores antes",
    "Number of previous entries since": "N\u00famero de entradas anteriores desde",
    "Number of previous entries since midnight": "N\u00famero de entradas anteriores desde a meia noite",
    "OXXO": "OXXO",
    "Object": "Objeto",
    "October": "Outubro",
    "Order canceled": "Pedido cancelado",
    "Order not approved": "Pedido n\u00e3o aprovado",
    "Others": "Outros",
    "Paid orders": "Pedidos pagos",
    "PayPal": "PayPal",
    "PayPal Credit": "Cr\u00e9dito no PayPal",
    "PayPal Pay Later": "PayPal Pay Later",
    "PayU": "PayU",
    "Payment method unavailable": "M\u00e9todo de pagamento indispon\u00edvel",
    "Placed orders": "Pedidos feitos",
    "Please enter the amount the organizer can keep.": "Por favor informe o valor que a organiza\u00e7\u00e3o pode manter.",
    "Powered by pretix": "Desenvolvido por pretix",
    "Press Ctrl-C to copy!": "Pressione Ctrl+C para copiar!",
    "Product": "Produto",
    "Product variation": "Varia\u00e7\u00e3o do produto",
    "Przelewy24": "Przelewy24",
    "Redeemed": "Resgatado",
    "Result": "Resultado",
    "SEPA Direct Debit": "D\u00e9bito Direto SEPA",
    "SOFORT": "SOFORT",
    "Sa": "S\u00e1b",
    "Saving failed.": "Erro ao salvar.",
    "Scan a ticket or search and press return\u2026": "Escanear um ingresso ou pesquisar e pressionar enter\u2026",
    "Search query": "Termo de busca",
    "Search results": "Resultados da busca",
    "Select a check-in list": "Selecione uma lista de check-in",
    "Selected only": "Selecionado apenas",
    "September": "Setembro",
    "Su": "Dom",
    "Switch check-in list": "Trocar lista de check-in",
    "Switch direction": "Trocar dire\u00e7\u00e3o",
    "Text box": "Caixa de texto",
    "Text object (deprecated)": "Objeto de texto (descontinuado)",
    "Th": "Qui",
    "The PDF background file could not be loaded for the following reason:": "O arquivo de fundo PDF n\u00e3o p\u00f4de ser carregado pelo seguinte motivo:",
    "The items in your cart are no longer reserved for you. You can still complete your order as long as they\u2019re available.": "Os itens no seu carrinho n\u00e3o est\u00e3o mais reservados para voc\u00ea. Voc\u00ea ainda pode completar o seu pedido desde que eles ainda estejam dispon\u00edveis.",
    "The items in your cart are reserved for you for one\u00a0minute.": [
      "Os itens em seu carrinho est\u00e3o reservados para voc\u00ea por 1 minuto.",
      "Os itens em seu carrinho est\u00e3o reservados para voc\u00ea por {num} minutos."
    ],
    "The organizer keeps %(currency)s %(amount)s": "A organiza\u00e7\u00e3o mant\u00e9m %(currency)s %(amount)s",
    "The request took too long. Please try again.": "A solicita\u00e7\u00e3o demorou muito. Por favor, tente novamente.",
    "This ticket is not yet paid. Do you want to continue anyways?": "Este ingresso ainda n\u00e3o foi pago. Voc\u00ea deseja continuar mesmo assim?",
    "This ticket requires special attention": "Este ingresso requer uma aten\u00e7\u00e3o especial",
    "Ticket already used": "Ingresso j\u00e1 utilizado",
    "Ticket blocked": "Ingresso bloqueado",
    "Ticket code is ambiguous on list": "C\u00f3digo do ingresso est\u00e1 amb\u00edguo na lista",
    "Ticket code revoked/changed": "C\u00f3digo do ingresso revogado/alterado",
    "Ticket design": "Design do ingresso",
    "Ticket not paid": "Ingresso n\u00e3o pago",
    "Ticket not valid at this time": "Ingresso inv\u00e1lido neste momento",
    "Ticket type not allowed here": "Tipo de ingresso n\u00e3o permitido aqui",
    "Tolerance (minutes)": "Toler\u00e2ncia (minutos)",
    "Total": "Total",
    "Total revenue": "Receita total",
    "Trustly": "Confi\u00e1vel",
    "Tu": "Ter",
    "Unknown error.": "Erro desconhecido.",
    "Unknown ticket": "Ingresso desconhecido",
    "Unpaid": "N\u00e3o pago",
    "Use a different name internally": "Use um nome diferente internamente",
    "Valid": "V\u00e1lido",
    "Valid Tickets": "Ingressos V\u00e1lidos",
    "Valid ticket": "Ingresso v\u00e1lido",
    "Venmo": "Venmo",
    "Verkkopankki": "Verkkopankki",
    "We": "Qua",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Estamos enviando sua solicita\u00e7\u00e3o para o servidor. Se isto tomar mais do que um minuto, verifique sua conex\u00e3o com a Internet e em seguida recarregue esta p\u00e1gina e tente novamente.",
    "We are processing your request \u2026": "Estamos processando sua solicita\u00e7\u00e3o \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "N\u00e3o conseguimos acessar o servidor, mas continuaremos tentando. \u00daltimo c\u00f3digo do erro: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "N\u00e3o conseguimos acessar o servidor. Por favor, tente novamente. C\u00f3digo do erro: {code}",
    "WeChat Pay": "WeChat Pay",
    "Yes": "Sim",
    "You get %(currency)s %(amount)s back": "Voc\u00ea recebe %(currency)s %(amount)s de volta",
    "You have unsaved changes!": "Voc\u00ea tem mudan\u00e7as n\u00e3o salvas!",
    "Your local time:": "Sua hora local:",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Sua solicita\u00e7\u00e3o chegou ao nosso servidor mas ainda precisamos esperar ela ser processada. Se isto tomar mais do que dois minutos, por favor entre em contato conosco ou retorne no seu navegador e tente novamente.",
    "Your request has been queued on the server and will soon be processed.": "Sua solicita\u00e7\u00e3o foi agendada em nosso servidor e ser\u00e1 processada assim que poss\u00edvel.",
    "Your request is currently being processed. Depending on the size of your event, this might take up to a few minutes.": "Sua solicita\u00e7\u00e3o est\u00e1 sendo processada. Dependendo do tamanho do seu evento, isto pode demorar alguns minutos.",
    "Zimpler": "Zimpler",
    "close": "fechar",
    "custom date and time": "data e hora customizada",
    "custom time": "hora customizada",
    "entry_status\u0004absent": "ausente",
    "entry_status\u0004present": "presente",
    "eps": "eps",
    "giropay": "giropay",
    "iDEAL": "iDEAL",
    "is after": "\u00e9 depois",
    "is before": "\u00e9 antes",
    "is one of": "\u00e9 um de",
    "minutes": "minutos",
    "required": "necess\u00e1rio",
    "widget\u0004Back": "Voltar",
    "widget\u0004Buy": "Comprar",
    "widget\u0004Choose a different date": "Escolha uma data diferente",
    "widget\u0004Choose a different event": "Escolha um evento diferente",
    "widget\u0004Close": "Fechar",
    "widget\u0004Close ticket shop": "Fechar loja de ingressos",
    "widget\u0004Continue": "Continuar",
    "widget\u0004Currently not available": "Atualmente n\u00e3o dispon\u00edvel",
    "widget\u0004Decrease quantity": "Diminuir quantidade",
    "widget\u0004FREE": "GRATUITO",
    "widget\u0004Hide variants": "Ocultar varia\u00e7\u00f5es",
    "widget\u0004Image of %s": "Imagem de %s",
    "widget\u0004Increase quantity": "Aumentar quantidade",
    "widget\u0004Load more": "Carregar mais",
    "widget\u0004New price: %s": "Novo pre\u00e7o: %s",
    "widget\u0004Next month": "Pr\u00f3ximo m\u00eas",
    "widget\u0004Next week": "Pr\u00f3xima semana",
    "widget\u0004Not available anymore": "N\u00e3o est\u00e1 mais dispon\u00edvel",
    "widget\u0004Not yet available": "Ainda n\u00e3o est\u00e1 dispon\u00edvel",
    "widget\u0004Only available with a voucher": "Apenas dispon\u00edvel com um cupom",
    "widget\u0004Open seat selection": "Abrir sele\u00e7\u00e3o de assentos",
    "widget\u0004Open ticket shop": "Abrir loja de ingressos",
    "widget\u0004Original price: %s": "Pre\u00e7o original: %s",
    "widget\u0004Previous month": "M\u00eas anterior",
    "widget\u0004Previous week": "Semana anterior",
    "widget\u0004Price": "Pre\u00e7o",
    "widget\u0004Quantity": "Quantidade",
    "widget\u0004Redeem": "Resgatar",
    "widget\u0004Redeem a voucher": "Resgatar cupom",
    "widget\u0004Register": "Registrar",
    "widget\u0004Reserved": "Reservado",
    "widget\u0004Resume checkout": "Retomar checkout",
    "widget\u0004Select": "Selecione",
    "widget\u0004Select %s": "Selecion %s",
    "widget\u0004Select variant %s": "Selecione varia\u00e7\u00e3o %s",
    "widget\u0004Show variants": "Exibir varia\u00e7\u00f5es",
    "widget\u0004Sold out": "Esgotado",
    "widget\u0004Some or all ticket categories are currently sold out. If you want, you can add yourself to the waiting list. We will then notify if seats are available again.": "Algumas ou todas as categorias de ingressos est\u00e3o esgotadas no momento. Se quiser, voc\u00ea pode se adicionar \u00e0 lista de espera. Em seguida, notificaremos se os assentos estiverem dispon\u00edveis novamente.",
    "widget\u0004The cart could not be created. Please try again later": "O carrinho n\u00e3o pode ser criado. Por favor, tente novamente mais tarde",
    "widget\u0004The ticket shop could not be loaded.": "A loja de ingressos n\u00e3o pode ser carregada.",
    "widget\u0004There are currently a lot of users in this ticket shop. Please open the shop in a new tab to continue.": "Atualmente, existem muitos usu\u00e1rios nesta loja de ingressos. Por favor, abra a loja em uma nova guia para continuar.",
    "widget\u0004Voucher code": "C\u00f3digo do cupom",
    "widget\u0004Waiting list": "Lista de espera",
    "widget\u0004We could not create your cart, since there are currently too many users in this ticket shop. Please click \"Continue\" to retry in a new tab.": "N\u00e3o foi poss\u00edvel criar seu carrinho, pois atualmente h\u00e1 muitos usu\u00e1rios nesta loja de ingressos. Clique em \"Continuar\" para tentar novamente em uma nova guia.",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "No momento, voc\u00ea tem um carrinho ativo para este evento. Se voc\u00ea selecionar mais produtos, eles ser\u00e3o adicionados ao seu carrinho existente.",
    "widget\u0004currently available: %s": "dispon\u00edvel atualmente: %s",
    "widget\u0004from %(currency)s %(price)s": "a partir de %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "inclu\u00eddo %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "incl. taxas",
    "widget\u0004minimum amount to order: %s": "valor m\u00ednimo por pedido: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "mais %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "mais taxas"
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
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M:%S",
      "%d/%m/%y %H:%M:%S.%f",
      "%d/%m/%y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y-%m-%d"
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

