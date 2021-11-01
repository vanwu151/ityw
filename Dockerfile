#django项目打包实例
FROM 218.94.64.98:2888/library/pythondjangobase:v3.0.3
COPY ./itywProject /opt/Django
EXPOSE 8080
#CMD source /etc/profile && cd /opt/Django && python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8080
CMD source /etc/profile && cd /opt/Django && python3 manage.py runserver 0.0.0.0:8080
