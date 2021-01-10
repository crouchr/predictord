# https://linuxize.com/post/how-to-install-opencv-on-debian-10/
# based on Debian Buster
FROM python:3.8.5-buster
LABEL author="Richard Crouch"
LABEL description="Weather Predictor daemon"

# generate logs in unbuffered mode
ENV PYTHONUNBUFFERED=0



# install opencv
RUN apt -y update
RUN apt -y install python3-opencv

# Install Python dependencies
RUN pip3 install pipenv
COPY Pipfile* ./
RUN pipenv install --system --deploy

RUN mkdir /app
# FIXME : replace this with volume
RUN mkdir /app/images

# Copy application and files
COPY app/*.py /app/
WORKDIR /app

# run Python unbuffered so the logs are flushed
#CMD ["python3", "-u", "predictord.py"]
CMD ["tail", "-f", "/dev/null"]
