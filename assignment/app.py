import os
from fastapi import FastAPI, BackgroundTasks
from image_generator import ImageGenerator
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, BackgroundTasks
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response


app = FastAPI()
images_db: dict = {}

class ImageRequest(BaseModel):
    prompt: str
    

# Function to be run as a background task.
# This is just a placeholder function for demonstration.
# In your application, this could be a function that generates an image.
def write_log(message: str):
    # Example of a time-consuming task: Writing a message to a file.
    # Replace this with the logic of your image generation task.
    with open("log.txt", "a") as file:
        file.write(f"{message}\n")

@app.get("/example")
async def example_endpoint(background_tasks: BackgroundTasks):
    # This endpoint demonstrates how to add a background task.
    # The `write_log` function will be executed after the response is sent.
    # Note: The task runs in the same process but does not block the response.
    background_tasks.add_task(write_log, "Example endpoint was visited")
    return {"message": "This is an example endpoint"}

# TODO: Define your POST /images endpoint for asynchronous image generation
# This endpoint should accept a custom prompt, process it asynchronously,
# and return an image ID for later retrieval.

@app.post("/images")
async def create_image(request: ImageRequest, background_tasks: BackgroundTasks):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail= "The prompt can´t be empty")

    image_id = str(uuid.uuid4())
    images_db[image_id] = {"status": "processing"}
    background_tasks.add_task(gen_image_task, image_id, request.prompt)
    return {"image_id": image_id, "status": "processing"}


            
# TODO: Implement the background task function for image generation
# This function will use the ImageGenerator service to generate images
# based on the provided custom prompt and save them.

image_generator = ImageGenerator(api_key=os.getenv("STABILITY_API_KEY"))

def gen_image_task(image_id: str, prompt: str):
    try:
        image_bytes = image_generator.generate_image(prompt)
        images_db[image_id] = {"status": "ready", "image_bytes": image_bytes}
    except Exception as e:
        print(f"Error generating image for {image_id}:{e}")
        images_db[image_id] = {"status": "failed"}


# TODO: Create an endpoint for retrieving generated images
# The endpoint should take an image ID and return the corresponding image
# if it's ready, or an appropriate status message otherwise.

@app.get ("/image/{image_id}") 
async def get_image(image_id:str):
    image_data = images_db.get(image_id)

    if image_data is None: 
        raise HTTPException(status_code=404, detail= "Image not found")

    if image_data["status"] == "processing":
        return {"status": "processing"}

    if image_data["status"] == "failed":
        raise HTTPException(status_code=500, detail= "Image generation failed")

    return Response(content=image_data["image_bytes"], media_type= "image/png")






# TODO: Implement error handling for various possible failure scenarios

# OPTIONAL: Implement any necessary profanity checking or validation for the user prompts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
