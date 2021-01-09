FROM python:3.8.5-buster
LABEL author="Richard Crouch"
LABEL description="Weather Predictor daemon"

# Install Python dependencies
RUN pip3 install pipenv
COPY Pipfile* ./
RUN pipenv install --system --deploy

# Copy application and files
RUN mkdir /app
COPY app/*.py /app/
WORKDIR /app

# run Python unbuffered so the logs are flushed
CMD ["python3", "-u", "predictord.py"]
#CMD ["tail", "-f", "/dev/null"]
