import os
import json
import re
import concurrent.futures
from crewai import Agent, Task, Crew, Process
from agents.parser_agent import get_parser
from agents.normalizer_agent import get_normalizer
from agents.matcher_agent import get_matcher
from agents.inquisitor_agent import get_inquisitor

# --- API KEY (Recommended: Use .env file) ---
os.environ["GROQ_API_KEY"] = "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"

llm_model = "groq/llama-3.1-8b-instant"

def _run_crew(resume_text, jd_text):
    # Agents Initialization
    p_agent = get_parser(llm_model)      # Node 1: Semantic Parser
    n_agent = get_normalizer(llm_model)  # Node 2: Ontology Normalizer
    m_agent = get_matcher(llm_model)     # Node 3: Matching Engine
    i_agent = get_inquisitor(llm_model)   # Node 4: The Inquisitor

    # --- NODE 1: Parsing Task ---
    task1 = Task(
        description=f"Extract structured technical skills and experience from this resume: {resume_text}",
        expected_output="A structured summary of skills and experience years.",
        agent=p_agent
    )

    # --- NODE 2: Normalization Task ---
    task2 = Task(
        description=f"Normalize the extracted skills to match industry standard terminology in this JD: {jd_text}",
        expected_output="A normalized list of skills ready for comparison.",
        agent=n_agent,
        context=[task1]
    )

    # --- NODE 3: Matching Task ---
    task3 = Task(
        description=(
            f"Compare the normalized profile against this JD: {jd_text}. "
            "SCORING: Exact match = 100. Missing experience = <60."
        ),
        expected_output="A percentage match score and brief insight.",
        agent=m_agent,
        context=[task2]
    )

    # --- NODE 4: Final Synthesis Task (RAW JSON OUTPUT) ---
    task4 = Task(
        description=(
            "Generate 3-4 critical interview questions based on the gaps found. "
            "CRITICAL: Combine everything into RAW JSON format only. NO MARKDOWN. "
            'Format: {"score": 85, "skills": ["Python", "SQL"], "insight": "...", "questions": ["..."]}'
        ),
        expected_output="A single raw JSON object string containing score, skills, insight, and questions.",
        agent=i_agent,
        context=[task3]
    )

    # Sequential process insures Node 1 -> Node 2 -> Node 3 -> Node 4
    sentinel_crew = Crew(
        agents=[p_agent, n_agent, m_agent, i_agent],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True
    )
    
    return sentinel_crew.kickoff()

def run_sentinel_analysis(resume_text, jd_text):
    # Max workers 1 because we want sequential execution for this pipeline
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_crew, resume_text, jd_text)
        # Timeout 120s is safe for Groq Llama 3.1
        return future.result(timeout=120)