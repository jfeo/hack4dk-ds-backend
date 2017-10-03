FROM bamos/openface
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir -p /home/hack4dk
WORKDIR /home/hack4dk
EXPOSE 5000
ENV FLASK_APP app.py
VOLUME [ "/home/hack4dk/outcomes" ]
RUN mkdir inputs
COPY inputs inputs
RUN mkdir static
COPY static static
COPY app.py .
COPY face.py .
COPY test.py .
ENTRYPOINT [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
