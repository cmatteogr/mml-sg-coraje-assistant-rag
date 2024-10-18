import os
from services.indexes_manager_service import IndexesManagerService
from repositories.indexes_repository import IndexesRepository
import json
import shutil

def run_create_index(path, index_path):
    """
    :param path: The directory path for which the index is to be created.
    :param index_path: final Index path
    :return: None
    """
    service = IndexesManagerService(IndexesRepository())

    if path != "data":
        index = service.create_index(path)
        service.save_index(index, index_path)
    else:
        print(f"\033[92m Servicio no disponible aún ___________"
              f"\U0001F995 \U0001F995 \U0001F995 \U0001F995 \033[0m___________")


INPUT_DIRECTORY = 'data/input'
INDEX_DIRECTORY = 'data/index'

if __name__ == "__main__":
    # Coraje Assistant - MLL-SG

    # NOTE: Change input_type to 'txt' if you want to index the transcriptions of the meetings
    input_type = 'csv'

    # read json file
    index_data_file_path = os.path.join(INPUT_DIRECTORY,'index_dict.json')
    # Open the file and load its contents as a list of dictionaries
    with open(index_data_file_path, 'r') as file:
        index_data = json.load(file)

    # init index orchestrator dict
    index_orchestrator = {}
    # for each meeting in the index data file, run the create_index function. create a new folder per meeting
    for meeting_data in index_data:
        print(f"create index for {meeting_data['original_title']}")
        index_n = meeting_data['original_title'].split('.')[0].strip()
        #new_filename = f"{index_n}. {meeting_data['new_title']}"
        new_filename = f"{index_n}"
        o_index_data_file_path = os.path.join(INPUT_DIRECTORY, f"meetings_transcriptions_{input_type}", f"{meeting_data['original_title']}.{input_type}")

        # create meeting folder, overwrite if exists
        meeting_data_folder_path = os.path.join(INDEX_DIRECTORY, new_filename)
        if os.path.exists(meeting_data_folder_path):
            shutil.rmtree(meeting_data_folder_path)
        os.makedirs(meeting_data_folder_path)

        # run create index
        run_create_index(o_index_data_file_path, meeting_data_folder_path)

        # add index to orchestrator data object
        index_orchestrator[new_filename] = meeting_data['summary']

    # save index orchestrator dict as JSON file
    index_orchestrator_file_path = os.path.join(INDEX_DIRECTORY, 'index_orchestrator.json')
    with open(index_orchestrator_file_path, 'w') as file:
        json.dump(index_orchestrator, file)