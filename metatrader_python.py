import MetaTrader5 as mt5
from datetime import datetime

# Variáveis vistas apenas nessa biblioteca, basta alterar symbol e qtd_contratos que a mudança reflete em todas as funções abaixo
symbol = str('WING24')
qtd_contratos = float(7)

def inicia_conexao():
    if not mt5.initialize(path=r'C:\Program Files\Meta Trader 5 conta real\terminal64.exe', login=456321, server='server_corretora', password='teste'):
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

    valor = valor / qtd_contratos * 5
    return int(valor)

def verifica_simbolo():
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info is None:
        print(f'Ativo "{symbol}" não encontrado em order_check()')
        mt5.shutdown()
        quit()
    else:
        print(f'"{symbol}" ativo')
        print()

    # se o símbolo não estiver disponível no MarketWatch, adicionamo-lo
    if not symbol_info.visible:
        print(f'Ativo "{symbol}" não disponivel, tentando adicionar')

        if not mt5.symbol_select(symbol, True):
            print(f'Falha em adicionar "{symbol}" saindo')
            mt5.shutdown()
            quit()

def compra_mt5():
    preco_atual = mt5.symbol_info_tick(symbol).ask
    desvio = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": qtd_contratos,
        "type": mt5.ORDER_TYPE_BUY,
        "price": preco_atual,
        "deviation": desvio,
        "magic": 123456,
        "comment": "Ordem de compra",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # enviamos a solicitação de negociação
    result = mt5.order_send(request)

    # verificamos o resultado da execução
    print(f'1. order_send(): solicitando ordem de compra ID "{result.order}"'
          f' ativo "{symbol}" quantidade "{qtd_contratos:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{desvio}" pontos')

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
    preco_atual = mt5.symbol_info_tick(symbol).bid
    desvio = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": qtd_contratos,
        "type": mt5.ORDER_TYPE_SELL,
        "price": preco_atual,
        "deviation": desvio,
        "magic": 123456,
        "comment": "Ordem de venda",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # enviamos a solicitação de negociação
    result = mt5.order_send(request)

    # verificamos o resultado da execução
    print(f'1. order_send(): solicitando ordem de venda ID "{result.order}"'
          f' ativo "{symbol}" quantidade "{qtd_contratos:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{desvio}" pontos')

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
    for tuplas in mt5.positions_get(symbol=symbol):
        yield dict(tuplas._asdict())

def gerador_saldo_diario():
    inicio = datetime.today()
    inicio = datetime(inicio.year, inicio.month, inicio.day)
    fim = datetime.now()

    for tuplas in mt5.history_deals_get(inicio, fim):
        yield dict(tuplas._asdict())

def saida_compra_mt5():
    # criamos uma solicitação de fechamento
    for itens in gerador():
        if itens['magic'] == 123456 and itens['type'] == 0:
            preco_atual = mt5.symbol_info_tick(symbol).bid
            desvio = 20
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": itens['volume'],
                "type": mt5.ORDER_TYPE_SELL,
                "position": itens['ticket'],
                "price": preco_atual,
                "deviation": desvio,
                "magic": 123456,
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
                  f' ativo "{symbol}" quantidade "{quantidade:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{desvio}" pontos')

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
        if itens['magic'] == 123456 and itens['type'] == 1:
            preco_atual = mt5.symbol_info_tick(symbol).ask
            desvio = 20
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": itens['volume'],
                "type": mt5.ORDER_TYPE_BUY,
                "position": itens['ticket'],
                "price": preco_atual,
                "deviation": desvio,
                "magic": 123456,
                "comment": "Saida da venda",
                "type_time": mt5.ORDER_TIME_DAY,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            id_antigo = itens['ticket']
            quantidade = itens['volume']

            # enviamos a solicitação de negociação
            result = mt5.order_send(request)

            print(f'3. order_send(): solicitando saida venda ID "{id_antigo}" ordem ID "{result.order}'
                  f'" ativo "{symbol}" quantidade "{quantidade:.0f}" no preço "{preco_atual:.0f}" com desvio permitido de "{desvio}" pontos')

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
        if itens['magic'] == 123456 and itens['entry'] == 1:
            saldo += itens['profit']

    return saldo

def saldo_atual():
    """
    Teste
    :return: Retorna o saldo atual da operação em aberto em reais
    """

    saldo = float(0)

    for itens in gerador():
        if itens['magic'] == 123456:
            saldo += itens['profit']

    return saldo

def verifica_posicao():
    posicao = None

    for itens in gerador():
        if itens['magic'] == 123456:
            posicao = itens['type']
            break

    return posicao

def qtd_posicionado():
    quantidade = float(0)

    for itens in gerador():
        if itens['magic'] == 123456 and itens['type'] == 0:
            quantidade += itens['volume']
        elif itens['magic'] == 123456 and itens['type'] == 1:
            quantidade -= itens['volume']

    return int(quantidade)

def volume_contratos():
    total = 0

    for i in gerador_saldo_diario():
        if i['magic'] == 123456:
            total += i['volume']

    return total

if __name__ == "__main__":
    pass
