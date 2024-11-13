from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import pandas as pd
from pymongo import MongoClient
from math import ceil
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get the templates directory from the environment variable
templates_dir = os.getenv("TEMPLATES_DIR", "default/templates/path")  # default path as fallback

# Set up Jinja2 template engine for the front end
templates = Jinja2Templates(directory=templates_dir)

# MongoDB connection setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # default to local if not set
client = MongoClient(mongo_uri)
db = client["medalist"]
collection = db["medals"]

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Get the upload path from environment variable
    upload_path = Path(os.getenv("UPLOAD_PATH", "/default/path/"))
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Sanitize file name and save the uploaded file
    filename = secure_filename(file.filename)
    file_location = upload_path / filename
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Parsing the CSV and insert data into MongoDB
    try:
        # Read the CSV into a pandas DataFrame
        df = pd.read_csv(file_location)

        # Convert DataFrame to list of dictionaries
        data = df.to_dict(orient="records")

        # Insert data into MongoDB
        collection.insert_many(data)

        # Redirect to the show_aggregated_stats endpoint after upload is successful
        return RedirectResponse(url="/show_aggregated_stats", status_code=303)  # 303 ensures a GET request on redirection
    except Exception as e:
        return {"error": str(e)}

# Home endpoint to serve the upload form
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

# Aggregated Stats Endpoint
@app.get("/show_aggregated_stats", response_class=HTMLResponse)
async def show_aggregated_stats(request: Request, page: int = Query(1, ge=1), per_page: int = Query(5, ge=1)):
    try:
        # Aggregation pipeline to group by multiple fields
        aggregation_pipeline = [
            {
                "$group": {
                    "_id": {
                        "medal_date": "$medal_date",
                        "medal_type": "$medal_type",
                        "medal_code": "$medal_code",
                        "name": "$name",
                        "gender": "$gender",
                        "country_code": "$country_code",
                        "country": "$country",
                        "country_long": "$country_long",
                        "nationality": "$nationality",
                        "team": "$team",
                        "team_gender": "$team_gender",
                        "discipline": "$discipline",
                        "event": "$event",
                        "event_type": "$event_type",
                        "url_event": "$url_event",
                        "birth_date": "$birth_date",
                        "code_athlete": "$code_athlete",
                        "code_team": "$code_team"
                    },
                    "count": {"$sum": 1}  # Counting the occurrences of each grouping
                }
            },
            {
                "$project": {
                    "_id": 0,  # exclude _id field in output
                    "medal_date": "$_id.medal_date",
                    "medal_type": "$_id.medal_type",
                    "medal_code": "$_id.medal_code",
                    "name": "$_id.name",
                    "gender": "$_id.gender",
                    "country_code": "$_id.country_code",
                    "country": "$_id.country",
                    "country_long": "$_id.country_long",
                    "nationality": "$_id.nationality",
                    "team": "$_id.team",
                    "team_gender": "$_id.team_gender",
                    "discipline": "$_id.discipline",
                    "event": "$_id.event",
                    "event_type": "$_id.event_type",
                    "url_event": "$_id.url_event",
                    "birth_date": "$_id.birth_date",
                    "code_athlete": "$_id.code_athlete",
                    "code_team": "$_id.code_team",
                    "count": 1  # Show the count of occurrences for each grouping
                }
            }
        ]

        # Aggregate data from MongoDB
        aggregated_data = collection.aggregate(aggregation_pipeline)
        aggregated_data_list = list(aggregated_data)

        # Paginate the results
        total_documents = len(aggregated_data_list)
        total_pages = ceil(total_documents / per_page)
        skip = (page - 1) * per_page
        data = aggregated_data_list[skip:skip + per_page]

        # Prepare the pagination info
        pagination = {
            "current_page": page,
            "total_pages": total_pages,
            "next_page": f"/show_aggregated_stats?page={page+1}&per_page={per_page}" if page < total_pages else None,
            "previous_page": f"/show_aggregated_stats?page={page-1}&per_page={per_page}" if page > 1 else None
        }

        return templates.TemplateResponse("aggregated_stats.html", {
            "request": request,
            "data": data,
            "pagination": pagination
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching aggregated data: {str(e)}")
