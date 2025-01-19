# Use the official AWS Lambda Python 3.11 runtime as the base image
FROM public.ecr.aws/lambda/python:3.11

# Set the working directory inside the container
WORKDIR /var/task

# Install Pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock ./

# Install the dependencies using Pipenv, ensuring they are installed in the system environment (not a virtual environment)
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the rest of the application code to the working directory
COPY lambda_function.py ./

# Set the entrypoint for AWS Lambda
CMD ["lambda_function.lambda_handler"]
