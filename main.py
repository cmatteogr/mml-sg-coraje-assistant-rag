from datetime import datetime

import gradio as gr
import os

from models.gradio_models import QAGradio
from services.indexes_manager_service import IndexesManagerService
from services.langchain_manager_service import LangchainManagerService
from repositories.indexes_repository import IndexesRepository
from repositories.langchain_repository import LangchainRepository
from dotenv import load_dotenv
import json
from langchain.llms import Ollama
from unit_of_work.uow import SQLServerUnitOfWork

PROMPT_TEMPLATE_BASE_KEY = 'PROMPT_TEMPLATE_BASE'
PROMPT_TEMPLATE_INTRO_KEY = 'PROMPT_TEMPLATE_INTRO'
LLM_NAME_BASE_KEY = 'LLM_NAME_BASE'
LLM_NAME_INTRO_KEY = 'LLM_NAME_INTRO'
VECTOR_QUANTITY_KEY = 'VECTOR_QUANTITY'


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
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    # Use the intro LLM to orchestrate the retrieval
    llm_name_intro = os.getenv(LLM_NAME_INTRO_KEY)
    intro_llm = Ollama(model=llm_name_intro)

    return intro_llm


def get_substring_between(s, start_char, end_char):
    # Find the first occurrence of the start character
    start_index = s.find(start_char)
    # Find the first occurrence of the end character after the start character
    end_index = s.find(end_char, start_index + 1)

    # Check if both start and end characters exist in the string
    if start_index != -1 and end_index != -1:
        # Return the substring between the start and end character
        return s[start_index + 1:end_index]
    else:
        return None  # Return None if the start or end character is not found


def respond(question, history):
    for i in range(3):
        try:
            prompt_template_intro = os.getenv(PROMPT_TEMPLATE_INTRO_KEY)
            question_intro = prompt_template_intro.format(question=question, indexes_data=json.dumps(indexes_dict_data))
            question_intro = question_intro.replace("{", "{{").replace("}", "}}")

            # Generate a response
            response = intro_llm(question_intro)

            # clean response and read json from string
            response = response.replace("{{", "{").replace("}}", "}")
            print('response relevant indexes', response)
            indexes_data = json.loads(response)
            indexes_data_list = indexes_data['indexes']

            # if none index context was found then return
            if len(indexes_data_list) == 0:
                return "No data was found related to your question, try another question"

            print(f"Indexes with the response: {indexes_data_list}")

            # NOTE: full_context may need a limit to avoid Long context window
            contexts_len = 1000
            history_text = "\n".join(map(lambda q_r: ", ".join(q_r), history))
            full_context_question = history_text + "\n" + question
            full_context_question = full_context_question[-contexts_len:]

            # for each index, create a retriever and run the qa_instance
            responses = []
            for index_data_name_response in indexes_data_list:
                # define the qa instance to use
                qa_instance_response = qa_instances_data[index_data_name_response]

                # use the history and generate the response
                responses.append(qa_instance_response(full_context_question)["result"])

            # summarize the responses
            final_response = intro_llm(
                f"Summarize the following responses:{json.dumps(responses)} in one single response given this question: {question}. Return a JSON like this {{\"summary\": \"single_summary_response\"}}. Helpful JSON responses summary:")
            print('final_response', final_response)
            # clean response and read json from string
            final_response = get_substring_between(final_response, '{', '}')
            try:
                final_response = "{" + final_response + "}"
                final_response_data = json.loads(final_response.strip())
                final_response = final_response_data['summary']
            except Exception as e:
                print('error extracting summary', e)

            final_response = str(final_response)

            # save response in DB
            with uow:
                qa_user_gradio = QAGradio(question=str(question), answer=str(final_response), history=str(history),
                                          exe_datetime=datetime.now())
                uow.repo.insert_qa_users_gradio(qa_user_gradio)

            return str(final_response)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    load_dotenv()

    path_index = 'data/index'

    # load context indexes file, json file
    with open(os.path.join(path_index, 'index_orchestrator.json'), 'r') as file:
        indexes_dict_data = json.load(file)

    # init the intro LLM
    intro_llm = load_intro_llm()

    uow = SQLServerUnitOfWork()

    # Load all the qa instances save them as a dict
    qa_instances_data = {}
    for index_data_name in indexes_dict_data:
        # load the qa instance
        qa_instance = create_qa_retriever(os.path.join(path_index, index_data_name))
        # save the qa instance
        qa_instances_data[index_data_name] = qa_instance

    gr.ChatInterface(
        respond,
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(placeholder=f"Ask me about Medellin Machine Learning - Study Group", container=False,
                           scale=7),
        title=f"Coraje MML-SG. Chatbot",
        cache_examples=True,
    ).launch(share=True)
