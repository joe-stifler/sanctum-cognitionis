# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_interface import ChatInterface
from praesentatio_cognitionis.header import show_header
show_header(0)

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms import LLMFamily
from servitium_cognitionis.llms import LLMGeminiModels
from servitium_cognitionis.connectors.csv_connector import CSVConnector
from servitium_cognitionis.managers.redacao_manager import RedacaoManager
from servitium_cognitionis.data_access.data_interface import DataInterface

# module imports from the standard python environment
import os
import hmac
import vertexai
import replicate
import google.auth
import streamlit as st

# API Tokens and endpoints from `.streamlit/secrets.toml` file
os.environ["REPLICATE_API_TOKEN"] = st.secrets["IMAGE_GENERATION"]["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["IMAGE_GENERATION"]["REPLICATE_MODEL_ENDPOINTSTABILITY"]

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

########################################################################################

def setup_data_access():
    table_mappings = {
        'redacoes_aluno': 'databases/redacao/unicamp/unicamp_redacoes_aluno.csv',
        'redacoes_candidatos': 'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
        'redacoes_propostas': 'databases/redacao/unicamp/unicamp_redacoes_propostas.csv'
    }
    csv_connector = CSVConnector(table_mappings)
    data_interface = DataInterface({'csv': csv_connector})
    return data_interface

def generate_scorings(scores):
    max_score = 4
    criteria = ["Proposta Temática (Pt)", "Gênero (G)", "Leitura (Lt)", "Convenções da Escrita e Coesão (CeC)"]
    icons = ["🎯", "📚", "🔍", "✍️"]

    for crit, icon, score in zip(criteria, icons, scores):
        st.progress(score / max_score)
        st.caption(f'{icon} {crit}: {score}/{max_score}')

    st.divider()
    score_sum = sum(scores)
    max_score_overall = 12
    
    # generate an icon to represent an overall score
    icon = "📝"
    
    st.progress(score_sum / max_score_overall)
    st.caption(f'📝 Somatório Total: {score_sum}/{max_score_overall}')

def display_files_with_checkboxes_and_downloads(temp_persona_files):
    st.write("Arquivos disponíveis na base de conhecimento da persona:")
    
    # Create two columns: one for the checkbox, one for the download button
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])

        for idx, persona_file in enumerate(temp_persona_files.items()):
            chosen_col = col1 if idx % 2 == 0 else col2

            file_path, file_enabled = persona_file
            file_label = os.path.basename(file_path)

            with chosen_col:
                checkbox_label = f"`Usar {file_label}?`"
                is_checked = st.checkbox(checkbox_label, value=file_enabled, key=f"checkbox_{file_label}")
                temp_persona_files[file_path] = is_checked

def update_persona_layout():
    available_files = [
        # 'databases/redacao/unicamp/unicamp_redacoes_aluno.csv',
        'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
        'databases/redacao/unicamp/unicamp_redacoes_propostas.csv',
        'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt',
        'personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md',
    ]
    
    if "persona_settings" not in st.session_state:
        default_file_list = [
            'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt',
            'personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md'
        ]
        if list(LLMGeminiModels)[0] == LLMGeminiModels.GEMINI_1_5_PRO:
            default_file_list.extend(
                [
                    'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
                    'databases/redacao/unicamp/unicamp_redacoes_propostas.csv',
                ]
            )

        st.session_state["persona_settings"] = {
            "persona_name": "Dani Stella",

            "persona_files": [
                'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
                'databases/redacao/unicamp/unicamp_redacoes_propostas.csv',
                'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt',
                'personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md'
            ],

            "persona_description": """Dani Stella, professora de literatura e redação apaixonada por educar e inspirar.

Dani Stella, professora extremamente rigorosa de literatura profundamente dedicada a educar seus alunos. Você busca focar em identificar erros nas redações pois sabe que eles que garantirão o real crescimento dos alunos. Você é extremamente criteriosa e justa, e sempre busca dar feedbacks detalhados e construtivos para seus alunos. Você é conhecida por sua abordagem compassiva e resiliente, e por capacitar seus alunos a alcançar o sucesso no vestibular e a descobrir sua voz autêntica através da escrita. Para tanto, sabe que todo sucesso vem com um custo, sendo este o custo de que os alunos deverão ser capazes de lidar com críticas e feedbacks construtivos, os quais você raramente se abstém em pegar leve. Pois reconhece que é nas suas críticas duras que virá o real aprendizado. Você é uma pessoa de extrema respeito, principalmente devido ao seu rigor e justiça. Sempre opta por uma nota abaixo do que o aluno merece, pois sabe que é nos erros que o aluno cresce. Na dúvida, sempre escolhe dar uma nota pior pro aluno pois sabe que as consequências de uma nota melhor do que a merecida são muito piores do que o contrário. Você é conhecida por ser uma pessoa extremamente justa e rigorosa, e por sempre priorizar o crescimento do aluno acima de tudo.

Arquivos relevantes na sua base de conhecimento:
------------------------------------------------

informacoes\_importantes\_sobre\_a\_redacao\_unicamp.md 11701 Tokens grade\_de\_correcao\_analitica\_unicamp.txt 1116 Tokens base\_de\_dados\_redacoes\_candidatos.csv 49977 Tokens base\_de\_dados\_propostas\_de\_redacoes.csv 37571 Tokens

1.  'base\_de\_dados\_redacoes\_candidatos.csv': Este arquivo contém as redações dos candidatos e suas respectivas notas. Suas colunas são:
    -   Name
    -   Texto da Proposta
    -   Expectativa da Banca
    -   Número da Proposta
    -   Ano do Vestibular
    -   Interlocutores (I)
    -   Situação do Problema (S)
    -   Recorte Temático
    -   Tema
    -   Gênero (G)
    -   Construção composicional
    -   Tipologia textual,Projeto de texto
    -   Leitura do(s) texto(s) da coletânea
    -   Escolhas lexicais e sintáticas
    -   Recursos coesivos
    -   Norma culta
    -   Estilo
    -   Originalidade
    -   Pertinência
    -   Observações
2.  'base\_de\_dados\_propostas\_de\_redacoes.csv': Este arquivo contém as propostas de redação que foram utilizadas pelos candidatos. Utilize esta base para entender o contexto e as exigências de cada proposta. Você sempre deve consultar essa base de dados antes de qualquer análise de redação de um aluno, buscando encontrar qual é a proposta específica (tanto 1 ou 2) e o ano do vestibular que ela foi cobrada a qual o aluno escrever sua redação.
3.  'informacoes\_importantes\_sobre\_a\_redacao\_unicamp.md': Este arquivo contém informações detalhadas sobre os critérios de correção da redação da Unicamp. Suas colunas são:
    -   Name
    -   Redação do Candidato
    -   Categoria
    -   Comentarios Corretor
    -   Proposta Escolhida
    -   Ano do Vestibular
    -   Nota - Redação
    -   Comentário - Redação
    -   Nota - Proposta Temática (Pt)
    -   Comentário - Proposta Temática (Pt)
    -   Nota - Gênero (G)
    -   Comentário - Gênero (G)
    -   Nota - Leitura (Lt)
    -   Comentário - Leitura (Lt)
    -   Nota - Coesão e Coerência (CeC)
    -   Comentário - Coesão e Coerência (CeC)
4.  'grade\_de\_correcao\_analitica\_unicamp.txt': Este arquivo contém a grade de correção analítica da Unicamp, que detalha os critérios de correção e os níveis de desempenho esperados para cada um deles.

Comportamentos esperados de ti e que define quem você é:
--------------------------------------------------------

1.  Identifique o ano do vestibular e a proposta de redação escolhida pelo aluno(a). Caso isto não esteja informado, peça para que o aluno informe.
2.  Então, busque na base de dados 'base\_de\_dados\_redacoes\_candidatos.csv' a proposta de texto associada com a escolha do aluno, assim com as expectativas da banca de correção da unicamp para a dada proposta. Aproveite para capturar das múltiplas outras colunas na base de dados a informação de interlecutor, gênero, situação de produção, tema da proposta, recorte temático (este sendo de extrema relevância), dentre outros que ficará a cargo de você buscar. Aqui, antes de prosseeguir, informe o aluno sobre:
    -   O Tema da Proposta
    -   Recorte Temático
    -   Interlocutor
    -   Gênero exigido
    -   Situação de Produção
    -   Expectativa da Banca
    -   Situação de Produção
3.  Após entender com profundidade a proposta de redação e já saber o que a banca de correção espera, busque na base de 'base\_de\_dados\_redacoes\_candidatos.csv' por exemplos de redações que foram corrigidas por corretores reais. Isto lhe ajudará a entender como os corretores reais avaliaram as redações dos alunos e a ter uma noção de como você pode fazer isso para a redação que o seu aluno está lhe pedindo. Aqui, você pode buscar por redações que foram corrigidas com notas altas, baixas, e anuladas, para ter uma noção do que é esperado e do que deve ser evitado.
4.  Então, abra busque o conteúdo do arquivo 'grade\_de\_correcao\_analitica\_unicamp.txt' para entender quais são os critérios exatos de correção e como eles são avaliados. E então guie-se pelos seguintes itens:
    -   **Proposta temática (Pt):** verifique se o aluno cumpriu as tarefas solicitadas e se articulou com o tema da prova.
    -   **Gênero (G):** avalie a construção do gênero, considerando situação de produção, interlocução, construção composicional e tipologia textual.
    -   **Leitura (Lt):** analise como o aluno mobiliza os textos da coletânea e demonstra sua compreensão.
    -   **Convenções da escrita e Coesão (CeC):** avalie a qualidade da escrita, incluindo adequação à norma culta, recursos coesivos, escolhas lexicais e sintáticas.
5.  Somente então você pode começar a ler a redação do aluno. Leia com atenção e paciência, buscando compreender a mensagem que o aluno deseja transmitir e identificando os pontos fortes e fracos do texto, em especial os fracos pois é neles que o aluno precisa mais de ajuda. Assegure de ler e reler a redação do aluno, bem como voltar a ler a proposta de redação, as expectativas da banca no mínimo de 3 vezes. Após isto, prossiga com seus comentários:
    -   Comentar sobre a estrutura do texto, a progressão temática e a qualidade da argumentação.
    -   Analisar as escolhas lexicais, sintáticas e os recursos coesivos, destacando pontos fortes e fracos.
    -   Identificar eventuais erros de ortografia, acentuação e gramática.
    -   Oferecer sugestões para melhorar a clareza, a coesão e a fluência do texto.
6.  Após este importante passo anterior, prossiga para dar a nota a redação do aluno. Neste momento, é de extrema relevância que você esteja num estado calma e frio, onde a razão predomine sobre suas emoções. Seja aqui extremamente criteriosa, principalmente visando o crescimento do aluno por meio de explicitação de seus erros. Assegure-se de voltar na grade de correção analítica da Unicamp antes de realizar a efetiva atribuição da nota. Caso note inconsistências ou erros, os corrija. Aqui, você deve seguir os seguintes passos:
    -   **Proposta temática (Pt):** atribua uma nota de 0 a 2, considerando se o aluno cumpriu as tarefas solicitadas e se articulou com o tema da prova.
    -   **Gênero (G):** atribua uma nota de 0 a 3, avaliando a construção do gênero, considerando situação de produção, interlocução, construção composicional e tipologia textual.
    -   **Leitura (Lt):** atribua uma nota de 0 a 3, analisando como o aluno mobiliza os textos da coletânea e demonstra sua compreensão.
    -   **Convenções da escrita e Coesão (CeC):** atribua uma nota de 1 a 4, avaliando a qualidade da escrita, incluindo adequação à norma culta, recursos coesivos, escolhas lexicais e sintáticas.

Sempre utilize números inteiros.

1.  Sempre deixe explícito o motivo de cada nota que você atribuir, e forneça feedback detalhado e construtivo para o aluno. Lembre-se de que o feedback é uma ferramenta poderosa para o aprendizado.
2.  Então volte ao passo 1 novamente pelo menos 2 vezes para garantir que você não deixou passar nenhum detalhe importante. Assegure de concientemente mobilizar pensamentos críticos e analíticos em cada passo do processo de correção. Assegure de refletir se a nota que você atribuiu é justa, de fato reflete a realidade como é, e se o feedback que você deu é claro, conciso e construtivo.
3.  Por fim, informe a nota total da redação assim como o tipo de classificação segundo esta nota:\*\*
    -   Nota total: {0 a 12} / 12
    -   Classificação: {anulada / abaixo da média / mediana / acima da média}

Lembre-se: você prioriza o rigor, apontar os erros para o crescimento.
            """,
        }

    with st.expander("Configurações da persona do professor(a)", expanded=False):
        def on_change_persona_name():
            st.session_state["persona_settings"]["persona_name"] = st.session_state.new_persona_name

        st.text_input(
            "Nome da persona do professor(a):",
            st.session_state["persona_settings"]["persona_name"],
            on_change=on_change_persona_name,
            key='new_persona_name'
        )
        
        def on_change_persona_description():
            st.session_state["persona_settings"]["persona_description"] = st.session_state.new_persona_description

        st.text_area(
            "Descrição da persona do professor(a):",
            value=st.session_state["persona_settings"]["persona_description"],
            on_change=on_change_persona_description,
            key='new_persona_description'
        )

        def change_files_state():
            st.session_state["persona_settings"]["persona_files"] = list(st.session_state.new_persona_files)

        st.multiselect(
            'Arquivos disponíveis na base de conhecimento da persona:',
            available_files,
            default=st.session_state["persona_settings"]["persona_files"],
            on_change=change_files_state,
            key="new_persona_files"
        )

def select_essay_layout(redacao_manager):
    expander = st.expander("Redações Disponíveis", expanded=False)

    vestibular = expander.selectbox("Escolha o vestibular", ["Unicamp", ])
    redacoes_propostas = redacao_manager.obter_redacao_propostas(
        vestibular,
        query = {
            'order_by': ['ano_vestibular', 'numero_proposta'],
            'ascending': [False, True]
        }
    )

    coletanea_escolhida = expander.selectbox(
        "Escolha a proposta e ano do vestibular",
        redacoes_propostas,
        format_func=lambda r: f"{r.nome}",
    )

    expander.text_area(
        "Coletânea de textos",
        coletanea_escolhida.texto_proposta,
        height=300,
        label_visibility='collapsed',
        disabled=True
    )
    
    return coletanea_escolhida


def essay_writing_layout(height_main_containers):
    with st.form("my_form2"):
        texto_redacao = st.text_area("Digite sua redação aqui", placeholder="Digite sua redação aqui", height=height_main_containers, label_visibility='collapsed')
        submitted = st.form_submit_button(
            "Submeter para avaliação", use_container_width=True)

    return submitted, texto_redacao

def specific_stable_diffusion_settings_layout():
    with st.expander("**Melhore sua imagem gerada**"):
        width = st.number_input("Largura da imagem gerada", value=1024)
        height = st.number_input("Altura da imagem gerada", value=1024)
        scheduler = st.selectbox('Scheduler', ('K_EULER', 'DDIM', 'DPMSolverMultistep', 'HeunDiscrete',
                                                'KarrasDPM', 'K_EULER_ANCESTRAL', 'PNDM'))
        num_inference_steps = st.slider(
            "Número de etapas de remoção de ruído", value=4, min_value=1, max_value=10)
        guidance_scale = st.slider(
            "Escala para orientação sem classificador", value=0.0, min_value=0.0, max_value=50.0, step=0.1)
        prompt_strength = st.slider(
            "Força do prompt ao usar img2img/inpaint (1.0 corresponde à destruição total das informações na imagem)", value=0.8, max_value=1.0, step=0.1)
        refine = st.selectbox(
            "Selecione o estilo refinado a ser usado (deixe os outros 2 de fora)", ("expert_ensemble_refiner", "None"))
        high_noise_frac = st.slider(
            "Fração de ruído a ser usada para `expert_ensemble_refiner`", value=0.8, max_value=1.0, step=0.1)
        negative_prompt = st.text_area("**Quais elementos indesejados você não quer na imagem?**",
                                        value="the absolute worst quality, distorted features",
                                        help="Este é um prompt negativo, basicamente digite o que você não quer ver na imagem gerada")

    return width, height, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, negative_prompt

def stable_diffusion_prompt_form_layout() -> None:
    if "image_prompt" not in st.session_state:
        st.session_state["image_prompt"] = """In a fantastical scene, a creature with a human head and deer body emanates a green light."""
    
    with st.container(border=True):
        def on_change_prompt():
            st.session_state["image_prompt"] = st.session_state.new_prompt

        st.text_area(
            "**Comece a escrever, Machado de Assis ✍🏾**",
            value=st.session_state["image_prompt"],
            help="Escreva um prompt para gerar uma imagem criativa",
            label_visibility='collapsed',
            on_change=on_change_prompt,
            key='new_prompt',
        )

        submitted = st.button(
            "Gerar uma imagem a partir do texto abaixo", use_container_width=True)

    return submitted

# Define the function to generate images based on text prompts
def stable_diffusion_layout(submitted, *args):
    width, height, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, negative_prompt = args
    
    if "image_output" not in st.session_state:
        st.session_state["image_output"] = "praesentatio_cognitionis/resources/stable_diffusion_sample.png"

    generated_images_placeholder = st.empty()
    generated_images_placeholder.image(
        st.session_state["image_output"],
        caption=st.session_state["image_prompt"],
        use_column_width=True
    )

    if submitted:
        try:
            # Only call the API if the "Submit" button was pressed
            if submitted:
                with st.spinner('Gerando imagem...'):
                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        output = replicate.run(
                            REPLICATE_MODEL_ENDPOINTSTABILITY,
                            input={
                                "prompt": st.session_state["image_prompt"],
                                "width": width,
                                "height": height,
                                "num_outputs": 1,
                                "scheduler": scheduler,
                                "num_inference_steps": num_inference_steps,
                                "guidance_scale": guidance_scale,
                                "prompt_stregth": prompt_strength,
                                "refine": refine,
                                "high_noise_frac": high_noise_frac,
                                "negative_prompt": negative_prompt
                            }
                        )

                        if output:
                            st.image(
                                output,
                                use_column_width=True,
                                caption=st.session_state["image_prompt"],
                                output_format="auto"
                            )
                            st.session_state["image_output"] = output
        except Exception as e:
            st.error(f'Encountered an error: {e}', icon="🚨")

def llm_family_model_layout():
    if "llm_families" not in st.session_state:
        st.session_state["llm_families"] = {
            str(family.value): family.value for family in LLMFamily
        }
        st.session_state["chosen_llm_family"] = str(LLMFamily.VERTEXAI_GEMINI)

    with st.expander("Provedor de inteligência artificial", expanded=False):
        def on_change_llm_family():
            st.session_state["chosen_llm_family"] = st.session_state.new_llm_family_name
        
        st.selectbox(
            'Escolha seu provedor de inteligência artificial',
            st.session_state["llm_families"].keys(),
            on_change=on_change_llm_family,
            key='new_llm_family_name'
        )
        
        llm_family_name = st.session_state["chosen_llm_family"]
        llm_family = st.session_state["llm_families"][llm_family_name]
        
        def on_change_llm_model():
            llm_family.update_current_model_name(st.session_state.new_llm_model_name)

        llm_model_name = st.selectbox(
            'Escolha seu modelo de inteligência artificial',
            llm_family.available_model_names(),
            on_change=on_change_llm_model,
            index=llm_family.current_model_index(),
            key='new_llm_model_name'
        )
        
        llm_model = llm_family.get_available_model(llm_model_name)
        
        def on_change_update_llm_model():
            llm_model.temperature = st.session_state.new_model_temperature

        st.slider(
            'Temperatura',
            min_value=llm_model.temperature_range[0],
            max_value=llm_model.temperature_range[1],
            value=llm_model.temperature,
            on_change=on_change_update_llm_model,
            key='new_model_temperature'
        )
        
        def on_change_update_llm_max_output_tokens():
            llm_model.max_output_tokens = st.session_state.new_max_output_tokens

        st.slider(
            'Número máximo de tokens de saída',
            min_value=llm_model.output_tokens_range[0],
            max_value=llm_model.output_tokens_range[1],
            value=llm_model.max_output_tokens,
            on_change=on_change_update_llm_max_output_tokens,
            key='new_max_output_tokens'
        )

@st.cache_resource
def get_redacao_manager():
    print("Creating RedacaoManager")
    redacao_manager = RedacaoManager(
        dal=setup_data_access(),
        tabela_redacoes_propostas='redacoes_propostas',
        tabela_redacoes_aluno='redacoes_aluno',
        tabela_redacoes_candidatos='redacoes_candidatos'
    )
    return redacao_manager

@st.cache_resource
def get_chat_interface():
    print("Creating ChatInterface")
    chat_interface = ChatInterface(
        session_id="redacoes",
        user_name=":blue[estudante]",
        user_avatar="👩🏾‍🎓",
        chat_height=400
    )
    return chat_interface

def convert_files_to_str(files_path: str):
    files_content = "Arquivos disponíveis na base de conhecimento da persona:\n\n"
    files_content += "--------------------------------------------------------\n\n"

    for file_path in files_path:
        files_content += f"Conteudo para o arquivo {file_path} below:\n\n"

        with open(file_path, "r") as file:
            files_content += file.read() + "\n\n"

    return files_content

def callback_update_persona(chat_interface):
    ai_persona_name = st.session_state["persona_settings"]["persona_name"]
    chosen_llm_family_name = st.session_state["chosen_llm_family"]
    chosen_llm_family = st.session_state["llm_families"][chosen_llm_family_name]

    persona_description = st.session_state["persona_settings"]["persona_description"]
    persona_files = st.session_state["persona_settings"]["persona_files"]

    persona_files_str = convert_files_to_str(persona_files)

    prompt_with_files_str = f"{persona_description}\n\n{persona_files_str}"

    chat_interface.setup_ai(
        ai_model=chosen_llm_family.current_model(),
        ai_avatar="👩🏽‍🏫",
        ai_name=f':red[{ai_persona_name}]',
        ai_base_prompt=prompt_with_files_str,
    )


def main():
    gemini_cloud_location = st.secrets["VERTEXAI"]["GEMINI_CLOUD_LOCATION"]

    key_path = ".streamlit/google_secrets.json"
    
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    
    with open(key_path, "w") as file:
        file.write(st.secrets["VERTEXAI"]["GOOGLE_JSON_SECRETS"])

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    _credentials, project_id = google.auth.default()

    vertexai.init(project=project_id, location=gemini_cloud_location)

    height_main_containers = 400
    chat_interface = get_chat_interface()
    redacao_manager = get_redacao_manager()

    st.markdown("<h1 style='text-align: center;'>📚 Página de Redações 📚</h1>", unsafe_allow_html=True)
    st.divider()

    col2, col3, col4 = st.columns([3, 3, 2], gap="large")
        

    with col2:
        submitted, texto_redacao = essay_writing_layout(height_main_containers)
        coletanea_escolhida = select_essay_layout(redacao_manager)

        with st.expander("Feedback da Redação", expanded=False):
            generate_scorings([0, 0, 0, 0])

        if submitted and chat_interface.check_chat_state():
            st.toast('Redação sendo enviada para avaliação...')

            context_mensagem = (
                # f"## Nome:\n\n{coletanea_escolhida.nome}\n\n"
                f"## Ano do Vestibular:\n\n{coletanea_escolhida.ano_vestibular}\n\n"
                f"## Proposta Escolhida:\n\n{coletanea_escolhida.numero_proposta}\n\n"
                # f"## Texto da Proposta:\n\n{coletanea_escolhida.texto_proposta}\n\n"

                # f"## Interlocutores:\n\n{coletanea_escolhida.interlocutores_i}\n\n"
                # f"## Situacao do Problema:\n\n{coletanea_escolhida.situacao_problema_s}\n\n"
                # f"## Recorte Tematico:\n\n{coletanea_escolhida.recorte_tematico}\n\n"
                # f"## Tema:\n\n{coletanea_escolhida.tema}\n\n"
                # f"## Genero:\n\n{coletanea_escolhida.genero_g}\n\n"
                # f"## Construcao Composicional:\n\n{coletanea_escolhida.construcao_composicional}\n\n"

                # f"## Tipologia Textual:\n\n{coletanea_escolhida.tipologia_textual}\n\n"
                # f"## Projeto de Texto:\n\n{coletanea_escolhida.projeto_texto}\n\n"
                # f"## Ler Textos da Coletanea:\n\n{coletanea_escolhida.leitura_textos_coletanea}\n\n"
                # f"## Escolhas Lexicais e Sintaticas:\n\n{coletanea_escolhida.escolhas_lexicais_sintaticas}\n\n"
                # f"## Recursos Coesivos:\n\n{coletanea_escolhida.recursos_coesivos}\n\n"
                # f"## Norma Culta:\n\n{coletanea_escolhida.norma_culta}\n\n"
                # f"## Estilo:\n\n{coletanea_escolhida.estilo}\n\n"
                # f"## Originalidade:\n\n{coletanea_escolhida.originalidade}\n\n"
                # f"## Pertinencia:\n\n{coletanea_escolhida.pertinencia}\n\n"
                # f"## Observacoes:\n\n{coletanea_escolhida.observacoes}\n\n"
                # f"## Expectativa da Banca:\n\n{coletanea_escolhida.expectativa_banca}\n\n"
                # f"---------------------------------------------------------\n\n"
                # f"---------------------------------------------------------\n\n"
                # f"{persona_name}, utilize o conteudo acima para avaliar a redação do aluno que segue abaixo.\n\n"
                f"---------------------------------------------------------\n\n"
                f"---------------------------------------------------------\n\n"
                f"## Redação do Aluno:\n\n{texto_redacao}\n\n"
            )
            
            chat_interface.send_user_message(texto_redacao, context_mensagem)

    with col3:
        chat_interface.setup_layout()
        chat_interface.setup_state()

        llm_family_model_layout()
        update_persona_layout()

        update_persona = st.button(
            "Atualizar Persona",
            use_container_width=True,
            on_click=callback_update_persona,
            args=(chat_interface,)
        )

        if not update_persona:
            chat_interface.run()

        if "first_run" not in st.session_state:
            st.session_state["first_run"] = True
            callback_update_persona(chat_interface)

    with col4:
        image_container = st.container(border=True, height=int(1.22 * height_main_containers))
        submitted = stable_diffusion_prompt_form_layout()
        specific_stable_diffusion_params = specific_stable_diffusion_settings_layout()

        with image_container:
            stable_diffusion_layout(submitted, *specific_stable_diffusion_params)

if __name__ == "__main__":
    main()
