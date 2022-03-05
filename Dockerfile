FROM python:3.10

WORKDIR /nba_data

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8502

COPY . .

