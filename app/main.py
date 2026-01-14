"""A one-line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

Typical usage example:

  foo = ClassFoo()
  bar = foo.function_bar()
"""

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

# Chat Response
@app.post("/chat")
def response():
    pass


# Health Check up of the endpoint
@app.get("/health")
def get_health():
    pass



if __name__ == "__main__":
    pass



