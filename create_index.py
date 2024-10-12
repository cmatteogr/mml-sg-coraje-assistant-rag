import os
from services.indexes_manager_service import IndexesManagerService
from repositories.indexes_repository import IndexesRepository

def run_create_index(path, name):
    """
    :param path: The directory path for which the index is to be created.
    :param name: The name to save the created index under.
    :return: None
    """
    service = IndexesManagerService(IndexesRepository())

    if path != "data":
        index = service.create_index(path)
        service.save_index(index, name)
    else:
        print(f"\033[92m Servicio no disponible aún ___________"
              f"\U0001F995 \U0001F995 \U0001F995 \U0001F995 \033[0m___________")


DATA_DIRECTORY = 'data'


def get_meeting_txt_files(meetings_folder_path):
    meetings_files = os.listdir(meetings_folder_path)
    txt_files = [f"{num}. {file}" for num, file in enumerate(meetings_files) if file.endswith(".txt")]
    return txt_files


def user_input_for_indexing(txt_files):
    list_files = "\n".join(txt_files)
    file_choice = input(f"Choose which PDF to vectorize, enter the number corresponding to each PDF \n"
                        f"-1. All\n{list_files}\n \033[91m___________________________ \n")
    index_name = input("\033[0mEnter the name of the index: \n \033[91m___________________________ \n")
    return file_choice, index_name


if __name__ == "__main__":
    meetings_transcriptions_folder_path = os.path.join(DATA_DIRECTORY, 'meetings_transcriptions')
    meetings_txt_files = get_meeting_txt_files(meetings_transcriptions_folder_path)

    file_choice, index_name = user_input_for_indexing(meetings_txt_files)

    if file_choice == "-1":
        for meeting_file in os.listdir(meetings_transcriptions_folder_path):
            run_create_index(os.path.join(meetings_transcriptions_folder_path, meeting_file), index_name)
    else:
        chosen_file = meetings_txt_files[int(file_choice) - 1].split(". ")[1]
        run_create_index(os.path.join(meetings_transcriptions_folder_path, chosen_file), index_name)