# telegram-chats-analyzer
A web app for analyzing and visualizing telegram chats.

## Setup

### Frontend (client)

- Ensure that you have set up Node and npm.

- Download the repo by running
  
  `git clone https://github.com/mikelovesolivia/telegram-chats-analyzer.git`
  
- Go to the project folder and download the required packages by running

   ```
    cd client
    npm install
   ```


### Backend (server)

- Python version: 3.12.
- Set up the python environment by going to the project folder and running
  ```
  cd server
  pip install -r requirements.txt
  ```
- Download [PostgreSQL](https://www.postgresql.org/download/), which is used as the project database.
- Create a database named `chats` in PostgreSQL.
  
### Export Telegram Chats

Please refer to this [link](https://telegram.org/blog/export-and-more) and export your chats in json format.


## Run the Application

Open two terminals at the project folder, and run the following commands respectively:

### Start the Frontend

```
  cd client
  npm start
```

And the application will automatically shown in a browser. Or you can visit the webpage at http://localhost:3000.


### Start the Backend

First, please open `app.py` and change the username and password of PostgreSQL database to your own username and password.

```
  cd server
  python app.py
```

Then the server will be started.


## Demo 

## Tools Used:

- Frontend
  - React, Bootstrap, Node, npm, axios

- Backend
  - Flask, PostgreSQL, Pandas
