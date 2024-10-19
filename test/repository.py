from datetime import datetime

from models.gradio_models import QAGradio
from unit_of_work.uow import SQLServerUnitOfWork

def test_insert_qa_users_gradio():
    uow = SQLServerUnitOfWork()
    with uow:
        qa_user_gradio = QAGradio(question='Test', answer='response', history='hist',
                                  exe_datetime=datetime.now())
        uow.repo.insert_qa_users_gradio(qa_user_gradio)