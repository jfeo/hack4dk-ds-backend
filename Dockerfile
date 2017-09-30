FROM bamos/openface
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir -p /home/hack4dk
WORKDIR /home/hack4dk
RUN mkdir static
COPY static static
VOLUME [ "/home/hack4dk/outcomes" ]
EXPOSE 5000
ENV FLASK_APP app.py
COPY app.py .
COPY face.py .
ENTRYPOINT [ "python", "-m", "flask", "run" ]
