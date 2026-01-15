

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.agent import response as agent_response
from services.ingestion import ingest_docs
from database.sql_memory import memory
import uuid
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ingest_docs()
    except Exception as e:
        print(f"Error during ingestion: {e}")
    yield
    memory.close()

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    selected_tool: str
    response: str
    retrieved_context: Optional[str] = None

# Chat Response
@app.post("/chat", response_model=ChatResponse)
def response_endpoint(request: ChatRequest):
    try:
        # session ID
        session_id = str(uuid.uuid4())
        
        result = agent_response(request.question)
        
        bot_output = result["output"]
        intermediate_steps = result["intermediate_steps"]
        
        selected_tool = "LLM (Default)"
        retrieved_context = None
        
        if intermediate_steps:
            # last tool action as the primary one, 
            last_action, observation = intermediate_steps[-1]
            selected_tool = last_action.tool
            retrieved_context = str(observation)
        
        # Log to DB
        memory.save_chat(
            session_id=session_id,
            user_message=request.question,
            bot_response=bot_output,
            tool_used=selected_tool,
            context=retrieved_context
        )
        
        # Also log tool usage specifically
        if intermediate_steps:
            for action, obs in intermediate_steps:
                memory.log_tool_usage(
                    tool_name=action.tool,
                    input_query=str(action.tool_input),
                    output_summary=str(obs)[:100] + "..." if obs else None, # Truncate ther result
                    success=True
                )
        else:
             # Log the default LLM usage
             memory.log_tool_usage(
                 tool_name="LLM",
                 input_query=request.question,
                 success=True
             )

        return ChatResponse(
            selected_tool=selected_tool,
            response=bot_output,
            retrieved_context=retrieved_context
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
def get_health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



