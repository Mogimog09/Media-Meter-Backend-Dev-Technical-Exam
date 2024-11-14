# FastAPI-Csv2Database-Importer  
A simple FastAPI application that allows you to upload CSV files, process the data, and store it into a MongoDB database simultaneously displaying received database files in webpage with pagination feature. This tool is perfect for importing large datasets from CSV files into MongoDB in an easy and efficient way.

## Features  
**File Upload:** Users can upload CSV files containing data on medalists.  
**MongoDB Integration:** Stores uploaded data into a MongoDB database.  
**Aggregation & Pagination:** Displays aggregated statistics of medalists, with pagination.  
**Environment Variable Security:** Uses .env for storing sensitive data like MongoDB credentials and file paths.  

## Technologies Used
**FastAPI** - Web framework for building APIs quickly with Python.  
**MongoDB** - Database for storing medalist data.  
**Pandas** - Data manipulation and CSV parsing.  
**Jinja2** - Template engine for rendering HTML.  
**Python-dotenv** - Loads environment variables from a .env file.  

**Run in command line:**
1: cd MAINFOLDER/app

2:uvicorn main:app --reload

3: access localhost


**Note:** MongoDB should be set up to run file  
Once file is successfully uploaded, it will be saved to mongodb database and collection, then page will redirect to aggregation page displaying table of all uploaded information with pagination.  
If file is not successfully uploaded or if mongodb content is removed, no info will display on the webpage table.

![upload](https://github.com/user-attachments/assets/fc68599f-8eab-404e-9669-5376e7f3b43b)
![mongodb](https://github.com/user-attachments/assets/15b4c653-5c71-4a28-8aca-956af78aefb3)
![display uploaded](https://github.com/user-attachments/assets/a16b9fbd-0757-41b7-b3bc-4547ffd56742)
