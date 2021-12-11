FROM python:3.9

WORKDIR /app
RUN apt update && apt install -y build-essential libpython3-dev libdbus-1-dev
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY *.py ./

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
