# Dados e integração — integrante 1 (Luccas)

Implementar a parte atribuída a Luccas no Planejamento_PI_Cesta_Basica.pdf: auditoria, tratamento rastreável, séries mensais, integração e reprodução. Fonte original preservada. Não implementar as três questões dos colegas nem inventar conclusões.

Abordagem escolhida para esta implementação: scripts Python com pandas/openpyxl, configuração JSON e CSV/JSON abertos. Um notebook dificultaria a ordem de execução; banco/dashboard acrescentariam escopo sem necessidade. A escolha técnica é da assistente, dentro do pedido de planejar e executar.

Cada linha mantém os oito valores de origem, número da linha Excel, campos normalizados, status e motivos. Repetições exatas mantêm a primeira ocorrência como representante por padrão, com opção de mantê-las; isso é hipótese operacional auditável. Dados inválidos, nomes genéricos não resolvidos e suspeitas explícitas de preço/quantidade ficam em quarentena, nunca são apagados. Não usar limiares estimados na série inteira para decidir exclusões.

Unidades kg/L/unidade são hipóteses configuradas por produto, identificadas como inferidas até confirmação da fonte. PPK é conferido contra preço/quantidade; o preço unitário é recalculado dessa razão quando válido. Alias semanticamente explícito pode ser normalizado; Farinha/Pão/Macarrão permanecem pendentes. Todos os critérios são publicados junto às saídas.

Média aritmética das observações válidas por produto/mercado/mês; também exportar mediana, mínimo, máximo e contagens. Série geral dá peso igual aos mercados observados, em vez de às linhas. Grade mensal completa dos pares observados na origem; lacunas preservadas, sem imputação. Cobertura é relativa à janela global da base, não significa continuidade operacional do estabelecimento.

main.py executa preparação por padrão. Módulos futuros oferecem executar(dados_dir: Path, saida_dir: Path) e são chamados só quando explicitamente solicitados. Ausência/erro não é sucesso. Registrar status em manifesto; integração real das questões permanece pendente até os colegas entregarem seus módulos.

Python >=3.12. Dependências fixadas. Testar nomes ambíguos, duplicatas, preços/quantidades inválidos, ausências, ponderação de mercados, lacunas, preservação da origem e falha de integração. Sem commits/push automáticos.
