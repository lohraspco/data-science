from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import FastAPI, Request, Depends, BackgroundTasks, Form
from fastapi import APIRouter, HTTPException
templates = Jinja2Templates(directory="template")

def spell_number(num, multiply_by_2):
    return num * 2
router = APIRouter()


def spell_number(num, multiply_by_2):
    return num * 2

class InputTest(BaseModel):
    num: str

@router.post('/sumitform')
async def form_post(request: Request, num: int = Form(...), multiply_by_2: bool = Form(False)):
    result = spell_number(num, multiply_by_2)
    return templates.TemplateResponse('test.html', context={'request': request, 'result': result, 'num': num})


@router.get("/test")
def form_post(request: Request, num:str = ""):
    return templates.TemplateResponse('test.html', context={'request': request, "num":num})

@router.get("/test/{num}")
def form_post(request: Request):
    return templates.TemplateResponse('test.html', context={'request': request})