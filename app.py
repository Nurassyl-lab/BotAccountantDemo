from fastapi import FastAPI

# Create an instance of FastAPI
app = FastAPI()

# Define a simple route
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Define another route for testing
@app.get("/hello")
def read_hello():
    return {"message": "Hello from FastAPI!"}

