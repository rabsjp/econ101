FROM python:3.4

# Force stdio/out/err to be unbuffered - we want to see errors pronto.
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY . .

RUN pip install -r requirements.txt

RUN git clone https://github.com/Leeps-Lab/otree-redwood.git
RUN pip install otree-redwood