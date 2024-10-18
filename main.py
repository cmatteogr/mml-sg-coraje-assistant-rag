import gradio as gr
import os
from services.indexes_manager_service import IndexesManagerService
from services.langchain_manager_service import LangchainManagerService
from repositories.indexes_repository import IndexesRepository
from repositories.langchain_repository import LangchainRepository
from dotenv import load_dotenv
import json
from langchain.llms import Ollama

PROMPT_TEMPLATE_BASE_KEY = 'PROMPT_TEMPLATE_BASE'
PROMPT_TEMPLATE_INTRO_KEY = 'PROMPT_TEMPLATE_INTRO'
LLM_NAME_BASE_KEY = 'LLM_NAME_BASE'
LLM_NAME_INTRO_KEY = 'LLM_NAME_INTRO'
VECTOR_QUANTITY_KEY = 'VECTOR_QUANTITY'

#PROMPT_TEMPLATE = "1. Use the following pieces of context to answer the question at the end.\n2. If you don't know the answer, just say that \"No sé la respuesta\" but don't make up an answer on your own.\n3. Keep the answer crisp and limited to 3,4 sentences.\nContext: {context}\nQuestion: {question}\nHelpful Answer:"


def get_index_files(path_index):
    return [f"{num}. {file}" for num, file in enumerate(os.listdir(path_index))]


def choose_index_file(indexes_files):
    list_indexes = "\n".join(indexes_files)
    file_choose = input(
        f"Escoge cual indice quieres utilizar, escribe el numero que le corresponde a cada indice \n{list_indexes}\n \033[91m___________________________ \n"
    )
    return indexes_files[int(file_choose)].split(". ")[1]


def create_qa_retriever(path):
    prompt_template_base = os.getenv(PROMPT_TEMPLATE_BASE_KEY)
    llm_name_base = os.getenv(LLM_NAME_BASE_KEY)

    vector_quantity = os.getenv(VECTOR_QUANTITY_KEY)

    index_service = IndexesManagerService(IndexesRepository())
    vector = index_service.load_index(path)

    langchain_service = LangchainManagerService(LangchainRepository())
    llm = langchain_service.load_model(llm_name_base)
    retriever = langchain_service.create_retriever(vector, int(vector_quantity))
    llm_chain = langchain_service.create_prompt(prompt_template_base, llm)
    qa_chain = langchain_service.create_qa_chain(llm_chain, retriever)

    return qa_chain


def load_intro_llm():
    # Use the intro LLM to orchestrate the retrieval
    llm_name_intro = os.getenv(LLM_NAME_INTRO_KEY)
    intro_llm = Ollama(model=llm_name_intro)

    return intro_llm


def respond(question, history):
    prompt_template_intro = os.getenv(PROMPT_TEMPLATE_INTRO_KEY)
    question_intro = prompt_template_intro.format(question=question, indexes_data=json.dumps(indexes_data))
    question_intro = question_intro.replace("{", "{{").replace("}", "}}")

    # Generate a response
    response = intro_llm(question_intro)

    # clean response and read json from string
    response = response.replace("{{", "{").replace("}}", "}")
    indexes_data = json.loads(response)
    indexes_data_list = indexes_data['indexes']

    path_index = 'data'
    index_files = get_index_files(path_index)
    chosen_file = choose_index_file(index_files)
    qa_instance = create_qa_retriever(os.path.join(path_index, chosen_file))


    # NOTE: full_context may need a limit to avoid Long context window
    contexts_len = 1000
    history_text = "\n".join(map(lambda q_r: ", ".join(q_r), history))
    full_context = history_text + "\n" + question
    full_context = full_context[-contexts_len:]

    return qa_instance(full_context)["result"]


if __name__ == "__main__":
    load_dotenv()

    # load context indexes file, json file
    with open('data/index/index_orchestrator.json', 'r') as file:
        indexes_data = json.load(file)

    intro_llm = load_intro_llm()

    gr.ChatInterface(
        respond,
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(placeholder=f"Ask me about Medellin Machine Learning - Study Group", container=False, scale=7),
        title=f"Coraje Chatbot",
        cache_examples=True,
        retry_btn=None,
    ).launch(share=True)
