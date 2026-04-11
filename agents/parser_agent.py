from crewai import Agent

def get_parser(llm_val): # llm_val ab ek string ("groq/...") hogi
    return Agent(
        role='Data Extraction Specialist',
        goal='Extract technical data.',
        backstory='Expert resume parser.',
        llm=llm_val, # CrewAI ise khud identify kar lega
        verbose=True,
        allow_delegation=False
    )