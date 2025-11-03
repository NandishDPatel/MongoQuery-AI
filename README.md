## Project photos

- Landing page before connecting to mongoDB
- ![Landing Page](images/01.png)

- After sucessful connection
- ![Successfull Connection Page](images/02.png)

- First query result 
- ![1st query](images/03.png)

- Technical Flow
- ![Technical flow](images/06.png)

- Second query result
- ![2nd query](images/04.png)

- Query result format
- ![Query result format](images/05.png)

- Responsive UI
- ![responsive UI](images/07.png)

## 🐳 Docker Setup

#### Step 1: Install Docker Desktop
- Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Install and restart your computer

#### Step 2: Set up Environment Variables
- Edit .env with your actual credentials of mongouri and GROQ API
- Get the groq API from here ["https://console.groq.com/home"]

#### Step 3 : Initialize the Database
```bash
docker-compose run --rm mongoquery-ai python connect.py
```

#### Step 4 : Run and access the streamlit application
```bash
docker-compose up --build
```
- To access your website go to [http://localhost:8501](http://localhost:8501)

#### To stop the application 
```bash
docker-compose down
```
