# Modelo de Margem Comercial

🇬🇧 [Read in English](README.md)

Modelo semântico governado que responde, para cada pedido: **quanto realmente ganhamos e por quê?** A margem é construída como uma cascata transparente de ~35 componentes com sinal (taxas de marketplace, frete, promoções, impostos, custo do produto, ads, fulfillment, devoluções, atendimento, perdas) em vez de um percentual opaco.

> Modelo semântico Power BI / Fabric, DAX, Power Query (M), dataflows e dicionário de dados do ERP.
> Tudo aqui é **sanitizado ou sintético**. Nenhuma empresa, parceiro, preço, custo ou margem reais aparecem neste repositório.

## O problema

Decisões comerciais (preço, campanhas, ads, em qual canal investir) eram tomadas sobre uma margem que ninguém conseguia decompor. Os custos estavam em lugares diferentes: extratos de marketplaces, ERP, faturas de centros de fulfillment, planilhas de campanhas, acordos de verba com fornecedores. As regras também mudam no tempo (um indicador de reputação altera o subsídio de frete mês a mês), então um pedido do trimestre passado não pode ser julgado com a regra deste.

## A solução

O fluxo está no [README em inglês](README.md#the-solution).

- **Definição escrita da margem** – cada componente documentado com sinal, significado e origem: itens da plataforma (comissão, frete do canal, taxa fixa, taxa de parcelamento, descontos e cupons, rebates) e da operação (custo do produto, impostos, verbas de indústria e do e-commerce, ads por campanha e por SKU, fulfillment, logística reversa, RMA, atendimento, cancelamentos, chargebacks, perdas, custo de capital, obsolescência).
- **Dicionário de dados do modelo** – mais de 150 campos documentados: tabela, alias, comportamento (coluna / cálculo), regra de cálculo e descrição de negócio, para que um analista novo consiga auditar qualquer número.
- **Dimensão de canal** – cada canal aponta para um *grupo de cálculo* e um *modelo de fulfillment* (envio próprio ou pelo marketplace), então um único conjunto de medidas atende todos os canais.
- **Regras com vigência** – indicadores do vendedor ficam com janelas de validade (mês a mês) e são buscados pela data de faturamento de cada pedido.
- **Entradas governadas** – nove tabelas de entrada (campanhas, ads, comissões especiais, indicadores de frete, monitor de SKU, verbas de fornecedor, rebates, verbas de marketing) mantidas em arquivos controlados e carregadas por um único dataflow; o negócio atualiza o dado sem mexer no modelo.
- **Ingestão de arquivos desorganizados** – extratos do centro de fulfillment chegam em muitos arquivos mensais com layouts diferentes; uma função personalizada por layout os combina em uma tabela de custo por SKU e período.
- **Framework de pastas de exibição** – medidas e colunas da tabela fato grande são organizadas por domínio, mantendo o modelo navegável conforme cresce.

## Executar a implementação de referência

[`reference_implementation/margin_waterfall.py`](reference_implementation/margin_waterfall.py) reproduz a cascata e o indicador de frete com vigência usando parâmetros sintéticos, para ler e testar a lógica sem o Power BI.

```bash
pip install pytest && pytest -q
```

## Decisões de projeto

- **Explicabilidade acima de um número único** – cada componente é separado e com sinal, e os testes garantem que as partes somam a margem.
- **Regras com data de vigência** – sem reprecificação retroativa do histórico.
- **Um modelo, vários canais** – o comportamento vem de atributos da dimensão, não de cópias de medidas por canal.
- **Documentação faz parte do modelo** – dicionário de dados e definição das métricas acompanham o modelo.

<!-- RESULTADOS: incluir depois (decisões habilitadas, vazamento de margem encontrado, tempo de refresh, usuários). -->

## Autoria

Construído e mantido por [Bárbara Gomes](https://github.com/Barbarags) – Coordenadora de Dados e BI.
