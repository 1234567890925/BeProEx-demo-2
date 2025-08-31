from fastapi import FastAPI, HTTPException
#from .models.io import SupportQuery, SupportResponse
#from .agents.llm import LLMClient
#from .agents.triage import triage_rewrite
#from .agents.technical import draft_solution
#from .agents.communication import refine_for_customer


from fastapi import FastAPI, HTTPException
from app.models.io import SupportQuery, SupportResponse
from app.agents.llm import LLMClient
#from app.agents.triage import triage_query      
from app.agents.triage import triage_rewrite
from app.agents.technical import draft_solution
from app.agents.communication import refine_for_customer
#from app.agents.technical import technical_answer  
#from app.agents.communication import refine_answer 


app = FastAPI(title="BeProEx – AI Support Agent", version="1.0.0")

@app.post("/support-query", response_model=SupportResponse)
def support_query(body: SupportQuery) -> SupportResponse:
    try:
        llm = LLMClient()
        # Agent 1: triage
        technical_query = triage_rewrite(body.query, llm)

        # Agent 2: technical draft
        draft, sources = draft_solution(technical_query, llm)

        # Agent 3: communication
        sources_joined = "\n\n".join(sources)
        final_answer = refine_for_customer(body.query, draft, sources_joined, llm)

        return SupportResponse(final_answer=final_answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
