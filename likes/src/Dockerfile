FROM python:3.11-slim

WORKDIR /opt/app

ENV PYTHONPATH="/opt/app"  

COPY ./requirements.txt /opt/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /opt/app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#CMD ["fastapi", "run", "main.py", "--port", "8000"]