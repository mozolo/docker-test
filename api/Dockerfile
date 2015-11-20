FROM python:2.7.10-wheezy
RUN pip install gunicorn==19.3.0
RUN pip install six==1.9.0 itsdangerous==0.24 MarkupSafe==0.23 Werkzeug==0.9.6 Jinja2==2.7.3 Flask==0.10.1 Flask-HTTPAuth==2.3.0 Flask-RESTful==0.3.1 
RUN pip install pymongo==3.0.3
RUN mkdir /opt/taskapi
COPY apiserver.py /opt/taskapi/
RUN chmod a+rwx /opt/taskapi/*

EXPOSE 5000

CMD python /opt/taskapi/apiserver.py

