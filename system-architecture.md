Arquitetura do Sistema \- Sanctum Cognitionis
-------------------------------------------------------------------

### 1. Introdução

Este documento apresenta a arquitetura do sistema Sanctum Cognitionis, levando em consideração as alterações na abordagem de backend e a integração de funcionalidades como memória LLM e geração de imagens.

### 2. Representação da Arquitetura

A arquitetura do sistema adota uma abordagem modular, com foco em um frontend robusto e um backend simplificado que interage diretamente com APIs externas.

-   **Frontend:** Desenvolvido em Streamlit, proporciona uma interface de usuário interativa e responsiva para os alunos.

-   **Backend:** Um único aplicativo backend em Python gerencia a lógica de negócios, interagindo diretamente com a API do Notion para persistência de dados e com APIs de LLMs (como Gemini, ChatGPT, etc.) para funcionalidades de tutoria, geração de texto e imagens.

### 3. Tecnologias Chave

-   **Streamlit:** Framework para desenvolvimento de aplicações web interativas.

-   **Notion API:** Permite a integração com o Notion para armazenamento e recuperação de dados do aluno, como cronograma de estudos, redações e progresso.

-   **LangChain:** Framework para gerenciar interações com LLMs, incluindo histórico de conversas e recuperação aumentada (RAG).

-   **LLMs (Gemini, ChatGPT, etc.):** Modelos de linguagem grandes para funcionalidades de tutoria, geração de texto, análise de sentimentos e extração de palavras\-chave.

-   **Stable Diffusion:** Modelo de IA para geração de imagens a partir de prompts de texto.

-   **Vector Database (opcional):** Para otimização de buscas semânticas na base de conhecimento (futura implementação).

### 4. Componentes do Sistema

-   **Página Inicial:** Apresenta uma visão geral do progresso do aluno, com destaques do cronograma de estudos, desempenho em simulados e feedback de redações.

-   **Página "Leituras Obrigatórias":** Oferece recursos para explorar as obras literárias exigidas pelos vestibulares, incluindo resumos, análises, questões e ferramentas interativas.

-   **Página "Cronograma de Estudos":** Permite ao aluno visualizar e gerenciar seu cronograma de estudos, com integração com LLMs para recomendações e feedback.

-   **Página "Simulados e Provas":** Apresenta o desempenho do aluno em simulados e provas, com análise de erros e sugestões de melhoria.

-   **Página "Redações":** Oferece um espaço para o aluno escrever e revisar suas redações, com feedback do tutor LLM e geração de imagens com Stable Diffusion.

-   **Página "Explorar Criatividade":** Permite ao aluno experimentar com ferramentas de geração de imagens, escrita criativa e música com IA.

-   **Página "Comunidade":** Fórum de discussão e grupos de estudo para interação e colaboração entre os alunos.

### 5. Fluxos de Trabalho

-   **Autenticação:** O aluno faz login usando suas credenciais do Notion, permitindo o acesso à sua base de dados personalizada.

-   **Recuperação de Dados:** O backend interage com a API do Notion para recuperar dados relevantes do aluno e exibi\-los no frontend.

-   **Interação com LLMs:** A dashboard envia prompts do aluno e contexto relevante (recuperado do Notion e da memória LLM) para as APIs de LLMs, e as respostas são exibidas na interface.

-   **Geração de Imagens:** A dashboard envia prompts para a API do Stable Diffusion e exibe as imagens geradas ao aluno.

-   **Memória LLM:** O histórico de conversas e informações relevantes do aluno são armazenados no Notion e utilizados para personalizar as interações futuras.

### 6. Critérios de Aceitação

-   **Funcionalidade:** Todas as funcionalidades devem operar conforme o esperado, passando por testes unitários e de integração.

-   **Usabilidade:** A interface deve ser intuitiva e fácil de usar para alunos com diferentes níveis de conhecimento técnico, comprovado por testes de usabilidade.

-   **Confiabilidade:** O sistema deve ser estável e garantir a persistência dos dados, demonstrado por testes de carga e recuperação de falhas.

-   **Desempenho:** A dashboard deve ter um tempo de resposta rápido, atendendo a benchmarks de desempenho estabelecidos.

-   **Segurança:** Os dados do aluno devem ser protegidos com medidas de segurança robustas, passando por auditorias de segurança.
