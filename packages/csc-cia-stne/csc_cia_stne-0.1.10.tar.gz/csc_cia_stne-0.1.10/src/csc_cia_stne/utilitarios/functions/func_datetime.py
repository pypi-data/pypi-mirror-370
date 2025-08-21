from datetime import datetime
from zoneinfo import ZoneInfo

def now_sp():

    data_hora_sp = datetime.now(ZoneInfo("America/Sao_Paulo"))
    data_hora_sp = data_hora_sp.replace(tzinfo=None)  # Remove a informação de fuso horário
    return data_hora_sp