from fastapi import FastAPI
from pydantic import BaseModel

from .especial import Mycrony, all_in_period


app = FastAPI()

class InputData(BaseModel):
    period: int = 30


@app.post("/birthday_reminder")
def birthday_reminder(data: InputData):
    mycrony = Mycrony()
    return all_in_period(mycrony.get_all_current_birthdays(), period=data.period)

