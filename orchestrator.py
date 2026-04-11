import os
import concurrent.futures
from crewai import Agent, Task, Crew, Process
from agents.parser_agent import get_parser
from agents.normalizer_agent import get_normalizer
from agents.matcher_agent import get_matcher
from agents.inquisitor_agent import get_inquisitor

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("Set the GROQ_API_KEY environment variable before starting Alpha-Logic.")

llm_model = "groq/llama-3.1-8b-instant"

def _run_crew(resume_text, jd_text):
    p_agent = get_parser(llm_model)
    n_agent = get_normalizer(llm_model)
    m_agent = get_matcher(llm_model)
    i_agent = get_inquisitor(llm_model)

    analysis_task = Task(
        description=(
            f"CRITICAL MISSION: Compare Resume vs JD.\n"
            f"Resume: {resume_text}\n"
            f"JD: {jd_text}\n\n"
            "SCORING RULES:\n"
            "1. If skills and role match exactly, score MUST be 100.\n"
            "2. If experience is missing, score below 60.\n"
            "3. RETURN ONLY RAW JSON. NO MARKDOWN. NO BACKTICKS.\n"
            'Format: {"score": 100, "skills": ["list"], "insight": "text", "questions": ["q1"]}'
        ),
        expected_output="A single raw JSON object string.",
        agent=m_agent
    )

    sentinel_crew = Crew(
        agents=[p_agent, n_agent, m_agent, i_agent],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True
    )
    return sentinel_crew.kickoff()

def run_sentinel_analysis(resume_text, jd_text):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_crew, resume_text, jd_text)
        return future.result(timeout=120)
