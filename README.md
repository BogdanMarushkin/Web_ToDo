**WEB TODO LIST**

Это пет-проект лист дел в вебе на локалхост

22.09.2026
Чтобы запустить фронтенд необходимо установить **Node.js**, затем выполнить **node install** в терминале и там же **node start**  
Теперь ваш фронтенд запущен по адресу *http://localhost:3000*

Чтобы запустить бэкенд необходимо установить все фреймворки из **requirements.txt**, затем в терминале файла выполнить:  
uvicorn main:app --port 8080 --reload

23.09.2026
На проект добавлена **БД PostgreSQL**  
Теперь для того, чтобы задачи сохранялись в бд необходимо создать докер контейнер с образом *postgresql* командой:   
*docker run docker run --name pg-container -e POSTGRES_PASSWORD=admin -d -p 15432:5432 postgres*
А затем запустить бд облачно:  
*docker exec -it pg-container psql -U postgres postgres*

