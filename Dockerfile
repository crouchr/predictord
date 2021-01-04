FROM python:3.8.5-buster
LABEL author="Richard Crouch"
LABEL description="Weather Forecast daemon"

# Install Python dependencies
RUN pip3 install pipenv
COPY Pipfile* ./
RUN pipenv install --system --deploy

# Copy application and files
RUN mkdir /app
COPY app/*.py /app/
WORKDIR /app

CMD ["python3", "predictord.py"]
