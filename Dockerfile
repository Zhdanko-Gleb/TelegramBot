FROM python:latest

RUN mkdir /src
WORKDIR /src
COPY . /src
RUN pip install -r requirements.txt
RUN pip install torch==1.5.0+cpu torchvision==0.6.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
