FROM ubuntu:18.04
MAINTAINER Daniel Cieszko "cieszdan@gmail.com"
RUN apt-get update
RUN apt-get install -y python3.6
RUN apt-get install -y python3-pip python3-dev
RUN cd /usr/local/bin
RUN ln -s /usr/bin/python3.6 python
RUN ln -s /usr/bin/python3.6 python3
RUN pip3 install --upgrade pip
RUN pip3 install jupyter
RUN pip3 install networkx
RUN pip3 install jsonpickle
RUN pip3 install numpy
RUN mkdir -p /var/log/gcs
COPY Charts /opt/gcs/Charts
COPY Grammar /opt/gcs/Grammar
WORKDIR /opt/gcs
ENTRYPOINT ["jupyter"]
CMD ["notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--ip='*'", "--NotebookApp.token=''"]