import MetaTrader5 as mt5
from datetime import datetime


# Basta alterar symbol e qtd_contratos que a mudança reflete em todas as funções abaixo
SYMBOL = str('WINZ25')
QTD_CONTRATOS = float(1)
ID_ROBO = 123456 # É possivel rodar mais de uma automação no mesmo MetaTrader5, e o ID é o que diferencia cada uma
SPREAD = 100


def inicia_conexao():
    if not mt5.initialize(path=r'C:\Program Files\MetaTrader 5 - XP Real\terminal64.exe'):
        print(f'Erro na inicialização, código do erro = {mt5.last_error()}')
        quit()


def encerra_conexao():
    mt5.shutdown()


def total_pontos(valor: float):
    """
    Converte o resultado financeiro em pontos

    :param valor: valor financeiro a ser convertido
    :return: retorna o saldo em pontos
    """

    valor = valor / QTD_CONTRATOS * 5
    return int(valor)


def quantidade_contratos():
    return QTD_CONTRATOS


def verifica_simbolo():
    symbol_info = mt5.symbol_info(SYMBOL)

    if symbol_info is None:
        print(f'Ativo "{SYMBOL}" não encontrado em order_check()')
        mt5.shutdown()
        quit()
    else:
        print(f'"{SYMBOL}" ativo')
        print()

    # se o símbolo não estiver disponível no MarketWatch, adicionamo-lo
    if not symbol_info.visible:
        print(f'Ativo "{SYMBOL}" não disponivel, tentando adicionar')

        if not mt5.symbol_select(SYMBOL, True):
            print(f'Falha em adicionar "{SYMBOL}" saindo')
            mt5.shutdown()
            quit()

    return SYMBOL


def compra_mt5():
    preco_atual = mt5.symbol_info_tick(SYMBOL).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": QTD_CONTRATOS,
        "type": mt5.ORDER_TYPE_BUY,
        "price": preco_atual,
        "deviation": SPREAD,
        "magic": ID_ROBO,
        "comment": "Ordem de compra",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # enviamos a solicitação de negociação
    result = mt5.order_send(request)

    # verificamos o resultado da execução
    print(f'1. order_send(): solicitando ordem de compra ID "{result.order}"'
          f' ativo "{SYMBOL}" quantidade "{QTD_CONTRATOS:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{SPREAD}" pontos')

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f'2. order_send falhou, retcode={result.retcode}')

        # solicitamos o resultado na forma de dicionário e exibimos elemento por elemento
        result_dict = result._asdict()

        for field in result_dict.keys():
            print(f'   {field}={result_dict[field]}')

            # se esta for uma estrutura de uma solicitação de negociação, também a exibiremos elemento a elemento
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()

                for tradereq_filed in traderequest_dict:
                    print(f'      traderequest: {tradereq_filed}={traderequest_dict[tradereq_filed]}')
    else:
        print(f'2. ordem de compra executada')
        print()


def venda_mt5():
    preco_atual = mt5.symbol_info_tick(SYMBOL).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": QTD_CONTRATOS,
        "type": mt5.ORDER_TYPE_SELL,
        "price": preco_atual,
        "deviation": SPREAD,
        "magic": ID_ROBO,
        "comment": "Ordem de venda",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # enviamos a solicitação de negociação
    result = mt5.order_send(request)

    # verificamos o resultado da execução
    print(f'1. order_send(): solicitando ordem de venda ID "{result.order}"'
          f' ativo "{SYMBOL}" quantidade "{QTD_CONTRATOS:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{SPREAD}" pontos')

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f'2. order_send falhou, retcode={result.retcode}')

        # solicitamos o resultado na forma de dicionário e exibimos elemento por elemento
        result_dict = result._asdict()

        for field in result_dict.keys():
            print(f'   {field}={result_dict[field]}')

            # se esta for uma estrutura de uma solicitação de negociação, também a exibiremos elemento a elemento
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()

                for tradereq_filed in traderequest_dict:
                    print(f'      traderequest: {tradereq_filed}={traderequest_dict[tradereq_filed]}')
    else:
        print(f'2. ordem de venda executada')
        print()


def gerador():
    for tuplas in mt5.positions_get(symbol=SYMBOL):
        yield dict(tuplas._asdict())


def gerador_saldo_diario():
    inicio = datetime.today()
    inicio = datetime(inicio.year, inicio.month, inicio.day)
    fim = datetime.now()

    for tuplas in mt5.history_deals_get(inicio, fim, group=SYMBOL):
        yield dict(tuplas._asdict())


def saida_compra_mt5():
    # criamos uma solicitação de fechamento
    for itens in gerador():
        if itens['magic'] == ID_ROBO and itens['type'] == 0:
            preco_atual = mt5.symbol_info_tick(SYMBOL).bid

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": itens['volume'],
                "type": mt5.ORDER_TYPE_SELL,
                "position": itens['ticket'],
                "price": preco_atual,
                "deviation": SPREAD,
                "magic": ID_ROBO,
                "comment": "Saida da compra",
                "type_time": mt5.ORDER_TIME_DAY,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            # pega a ID da ordem de compra
            id_antigo = itens['ticket']
            quantidade = itens['volume']

            # enviamos a solicitação de negociação
            result = mt5.order_send(request)

            # verificamos o resultado da execução
            print(f'3. order_send(): solicitando saida compra ID "{id_antigo}" ordem ID "{result.order}"'
                  f' ativo "{SYMBOL}" quantidade "{quantidade:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{SPREAD}" pontos')

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f'4. order_send falhou, retcode={result.retcode}')
                print(f'   resultado: {result}')
            else:
                print('4. ordem saida compra executada')

            result = None
            print()


def saida_venda_mt5():
    # criamos uma solicitação de fechamento
    for itens in gerador():
        if itens['magic'] == ID_ROBO and itens['type'] == 1:
            preco_atual = mt5.symbol_info_tick(SYMBOL).ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": itens['volume'],
                "type": mt5.ORDER_TYPE_BUY,
                "position": itens['ticket'],
                "price": preco_atual,
                "deviation": SPREAD,
                "magic": ID_ROBO,
                "comment": "Saida da venda",
                "type_time": mt5.ORDER_TIME_DAY,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            id_antigo = itens['ticket']
            quantidade = itens['volume']

            # enviamos a solicitação de negociação
            result = mt5.order_send(request)

            print(f'3. order_send(): solicitando saida venda ID "{id_antigo}" ordem ID "{result.order}'
                  f'" ativo "{SYMBOL}" quantidade "{quantidade:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{SPREAD}" pontos')

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                # verificamos o resultado da execução
                print(f'4. order_send falhou, retcode={result.retcode}')
                print(f'   resultado: {result}')
            else:
                print('4. ordem saida venda executada')
            print()


def saldo_diario():
    """
    teste
    """
    saldo = float(0)

    for itens in gerador_saldo_diario():
        if itens['magic'] == ID_ROBO and itens['entry'] == 1:
            saldo += itens['profit']

    return saldo


def saldo_atual():
    """
    Teste
    :return: Retorna o saldo atual da operação em aberto em reais
    """

    saldo = float(0)

    for itens in gerador():
        if itens['magic'] == ID_ROBO:
            saldo += itens['profit']

    return saldo


def verifica_posicao():
    posicao = None

    for itens in gerador():
        if itens['magic'] == ID_ROBO:
            posicao = itens['type']
            break

    return posicao


def qtd_posicionado():
    quantidade = float(0)

    for itens in gerador():
        if itens['magic'] == ID_ROBO and itens['type'] == 0:
            quantidade += itens['volume']
        elif itens['magic'] == ID_ROBO and itens['type'] == 1:
            quantidade -= itens['volume']

    return int(quantidade)


def volume_contratos():
    total = 0

    for i in gerador_saldo_diario():
        if i['magic'] == ID_ROBO:
            total += i['volume']

    return int(total)


def id_ordem_aberta():
    for ordens in mt5.orders_get(symbol=SYMBOL):
        ordem = dict(ordens._asdict())

        if ordem['magic'] == ID_ROBO:
            return ordem['ticket']

    return None


def preco_atual():
    preco = mt5.symbol_info_tick(SYMBOL)

    if preco is not None:
        return preco.bid, preco.ask
    else:
        return None, None


def cancelar_ordem_aberta():
    id_ordem = id_ordem_aberta()

    if id_ordem is not None:
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": id_ordem
        }

        # enviamos a solicitação de negociação
        result = mt5.order_send(request)

        # verificamos o resultado da execução
        print(f'1. order_send(): solicitando ordem de cancelamento ID "{result.order}"'
              f' ativo "{SYMBOL}" quantidade "{QTD_CONTRATOS:.0f}"')

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f'2. order_send falhou, retcode={result.retcode}')

            # solicitamos o resultado na forma de dicionário e exibimos elemento por elemento
            result_dict = result._asdict()

            for field in result_dict.keys():
                print(f'   {field}={result_dict[field]}')

                # se esta for uma estrutura de uma solicitação de negociação, também a exibiremos elemento a elemento
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()

                    for tradereq_filed in traderequest_dict:
                        print(f'      traderequest: {tradereq_filed}={traderequest_dict[tradereq_filed]}')
        else:
            print(f'2. ordem aberta cancelada')
            print()


if __name__ == "__main__":
    pass
