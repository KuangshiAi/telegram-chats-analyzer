# telegram-chats-analyzer
Want an annual summary of your telegram chats with your best friend or lover?

Here is a web app for you to analyze and visualize telegram chats!

Authors: [mikelovesolivia](https://github.com/mikelovesolivia) & [KuangshiAi](https://github.com/KuangshiAi)

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
- Download [PostgreSQL](https://www.postgresql.org/download/), which is used as the project database. Use Ubuntu 22.04 as an example here:
  ```
  sudo apt update
  sudo apt install postgresql postgresql-contrib
  sudo systemctl start postgresql.service
  ```
- Reset password and create a database named `chats` in PostgreSQL.
  ```
  sudo systemctl start postgresql.service
  sudo -i -u postgres
  createdb chats
  psql
  ALTER USER postgres WITH PASSWORD 'Your_Password';
  exit
  ```

  
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

### Convert chat data format
If you have chat data downloaded from discord or text, you can go to `server/utils` folder, modify the related file names and run

```
python discord2tele.py
```

or 

```
python text2tele.py
```
and you will get the right format of your chat data as json file. You can then upload the file to the application as aforementioned.



### Start the Backend

First, please open `app.py` and `process_chat.py`, change the username and password of PostgreSQL database to your own username and password.

```
  cd server
  python app.py
```

Then the server will be started.


## Functions

- Visualize Chat Frequency Calendar
  - Generate a calendar heatmap of chat frequency to identify active and inactive periods.
  - ![image](https://github.com/user-attachments/assets/20639d87-e781-4fce-b804-77f849901084)

- Word Cloud
  - Create a word cloud to visualize the most frequently used words in chat messages.
  - ![image](https://github.com/user-attachments/assets/bca92464-0a63-4bf3-9df1-b4648a6c3843)

- Sentiment Analysis
  - Perform sentiment analysis on chat messages and use t-SNE to cluster examples based on emotional tone.
  - ![image](https://github.com/user-attachments/assets/95b63002-bba3-43d6-9959-87e0ba085644)

- Social Network Graph
  - Generate a social network graph to visualize user interactions in selected Telegram channels, highlighting key connections.
  - ![image](https://github.com/user-attachments/assets/89ef0c51-c953-4df2-855f-39ba5a4764fd)


- Pie Chart of Chat Numbers by User
  - Generate a pie chart representing the distribution of chat numbers among different users.
  - ![image](https://github.com/user-attachments/assets/804edc95-8b9d-46dd-8b2f-00f1c8f355c0)

- Radar Chart of Activity by Time of Day
  - Create a radar chart to visualize chat activity distribution across different times of the day.
  - ![image](https://github.com/user-attachments/assets/a6bc5b8d-7980-454d-8ed0-5ca0c3724fe8)


## Tools Used:

- Frontend
  - HTML, CSS, Bootstrap, JavaScript, React, Node, npm, axios

- Backend
  - Python, Flask, PostgreSQL, Pandas
 
- Visualization & Analysis
  - Matplotlib, NLTK, Networkx, Scikit-Learn
