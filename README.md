# Projeto Final: Análise de Avaliações de Consumidores

Projeto final da disciplina de Introdução à Ciência de Dados no curso de Ciência de
Dados e Inteligência Artificial da FGV EMAp.

**Objetivo**:
> Analisar avaliações de consumidores para diversos produtos ou serviços para
> identificar padrões de satisfação do cliente e áreas para melhoria, utilizando
> técnicas de raspagem de de dados web, análises no Excel e insights potencializados
> por IA.

Para nosso trabalho, decidimos pela extração e análise de avaliações de usuários sobre
filmes que concorreram ao Academy Awards (Oscar).

Etapas do projeto:
- Busca e coleta dos dados de filmes premiados em festivais de cinema conhecidos;
- Raspagem de avaliações dos usuários do IMDb para os filmes de uma categoria;
- Limpeza das reviews e remoção de duplicatas;
- Identificação das emoções expressas em cada review;
- Análise dos dados e verificação de hipóteses por meio do Excel.

Para a extração dos dados, os seguintes arquivos devem ser executados em sequência:
- `web_scrapping.py`
- `sanitation.py`
- `gpt.py`
