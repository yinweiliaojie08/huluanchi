FROM python:3.9.16-alpine
RUN pip3  --proxy="http://172.24.58.50:7890" install paramiko==3.0.0 scp==0.14.5
COPY transmission.py /root/transmission.py
CMD ["python3","-u","/root/transmission.py"]
