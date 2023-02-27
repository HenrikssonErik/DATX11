FROM python:3.11

COPY test_files_test_runner/requirements.txt /req/
RUN pip install -r /req/requirements.txt
ADD podman_test_executer.py .

RUN mkdir /DATX11/
CMD ["python", "./podman_test_executer.py"]



