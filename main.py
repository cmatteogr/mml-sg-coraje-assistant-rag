import gradio as gr
import os
from services.indexes_manager_service import IndexesManagerService
from services.langchain_manager_service import LangchainManagerService
from repositories.indexes_repository import IndexesRepository
from repositories.langchain_repository import LangchainRepository
from dotenv import load_dotenv

PROMPT_TEMPLATE_KEY = 'PROMPT_TEMPLATE'
LLM_NAME_KEY = 'LLM_NAME'
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
    prompt_template = os.getenv(PROMPT_TEMPLATE_KEY)
    llm_name = os.getenv(LLM_NAME_KEY)
    vector_quantity = os.getenv(VECTOR_QUANTITY_KEY)

    print(prompt_template)

    index_service = IndexesManagerService(IndexesRepository())
    vector = index_service.load_index(path)

    langchain_service = LangchainManagerService(LangchainRepository())
    llm = langchain_service.load_model(llm_name)
    retriever = langchain_service.create_retriever(vector, int(vector_quantity))
    llm_chain = langchain_service.create_prompt(prompt_template, llm)
    qa_chain = langchain_service.create_qa_chain(llm_chain, retriever)

    return qa_chain


def respond(question, history):
    # NOTE: full_context may need a limit to avoid Long context window
    contexts_len = 1000
    history_text = "\n".join(map(lambda q_r: ", ".join(q_r), history))
    full_context = history_text + "\n" + question
    full_context = full_context[-contexts_len:]

    return qa(full_context)["result"]


if __name__ == "__main__":
    load_dotenv()

    path_index = 'data'
    index_files = get_index_files(path_index)
    chosen_file = choose_index_file(index_files)

    qa = create_qa_retriever(os.path.join(path_index, chosen_file))


    gr.ChatInterface(
        respond,
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(placeholder=f"Hazme una pregunta acerca de {chosen_file}", container=False, scale=7),
        title=f"{chosen_file} Chatbot",
        cache_examples=True,
        retry_btn=None,
    ).launch(share=True)
