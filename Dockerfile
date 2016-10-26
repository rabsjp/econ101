FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code

WORKDIR /code

ADD . .

RUN pip install -r requirements-docker.txt
RUN git clone https://github.com/Leeps-Lab/otree-core.git

RUN cd otree-core
RUN pip install
RUN cd ..
