FROM public.ecr.aws/lambda/python:3.11
RUN yum install -y gcc postgresql-devel && yum clean all
WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["lambda_handler.handler"]
