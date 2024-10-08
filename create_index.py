import os
from services.indexes_manager_service import IndexesManagerService
from repositories.indexes_repository import IndexesRepository

def run_create_index(path, name):

    service = IndexesManagerService(IndexesRepository())

    if path != "data":
        index = service.create_index(path)
        service.save_index(index, name)
    else:
        print(f"\033[92m Servicio no disponible aún ___________"
              f"\U0001F995 \U0001F995 \U0001F995 \U0001F995 \033[0m___________")



if __name__ == "__main__":
    path_data = 'data'
    meetings_txt_files = []

    meetings_transcriptions_folder_path = os.path.join(path_data, 'meetings_transcriptions')
    meetings_transcriptions_files = os.listdir(meetings_transcriptions_folder_path)

    # Read all the meetings txt files
    for num, file in enumerate(meetings_transcriptions_files):
        if file.endswith(".txt"):
            meetings_txt_files.append(f"{num}. {file}")

    # Read code repositories
    # NOTE: Logic to read code

    list_files = "\n".join(meetings_txt_files)
    file_choose = input(f"Escoge cual PDF es el que quieres vectorizar, escribe el numero que le"
                        f"corresponde a cada PDF \n-1. Todos\n{list_files}\n \033[91m___________________________ \n")

    name = input("\033[0mEscribe el nombre del index: \n \033[91m___________________________ \n")

    if file_choose == "-1":
        for meetings_txt_file in meetings_transcriptions_files:
            run_create_index(os.path.join(meetings_transcriptions_folder_path, meetings_txt_file), name)
    else:
        run_create_index(path_data + '/' + meetings_txt_files[int(file_choose) - 1].split(". ")[1], name)