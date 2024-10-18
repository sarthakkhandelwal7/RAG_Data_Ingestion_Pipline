# Use the official Python 3.11 image
FROM python:3.11.4-slim-buster

# Install AWS Lambda Runtime Interface Client
RUN pip install awslambdaric

# Set the working directory
WORKDIR /var/task

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies using Pipenv
RUN pip install pipenv
RUN pipenv install --system --deploy

# Copy function code
COPY lambda_function.py ./

# Set the entrypoint for AWS Lambda
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "lambda_function.lambda_handler" ]
