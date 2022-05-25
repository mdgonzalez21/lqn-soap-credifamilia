FROM lambci/lambda:build-python3.8

RUN yum install pkg-config libxmlsec1 xmlsec1-openssl xmlsec1 libxml2 libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel -y

COPY lib "${LAMBDA_TASK_ROOT}/lib"
COPY tests ${LAMBDA_TASK_ROOT}
COPY service.py ${LAMBDA_TASK_ROOT}
COPY config.yaml ${LAMBDA_TASK_ROOT}
COPY config_dev.yaml ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -U pip
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

RUN cp /usr/lib64/libxmlsec1-openssl.so.1 "${LAMBDA_TASK_ROOT}/lib"
RUN cp /usr/lib64/libxmlsec1-openssl.so "${LAMBDA_TASK_ROOT}/lib"
RUN cp /usr/lib64/libxmlsec1.so.1 "${LAMBDA_TASK_ROOT}/lib"
RUN cp /usr/lib64/libltdl.so.7 "${LAMBDA_TASK_ROOT}/lib"
RUN cp /usr/lib64/libxslt.so.1 "${LAMBDA_TASK_ROOT}/lib"
RUN cp /usr/lib64/libxml2.so.2 "${LAMBDA_TASK_ROOT}/lib"

RUN zip -r lambda.zip .


CMD [ "service" ]
