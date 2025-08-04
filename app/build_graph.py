from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
import logging
import asyncio

from ingester import load_doc, load_text, load_pdf_and_split_sections, load_and_split_pages
from parser import split_sections
from summarizer import summarize_section, analyze_section
from finalizer import finalize_summary
from langchain_core.messages.utils import count_tokens_approximately

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    source: str
    is_pdf: bool
    raw_text: str
    sections: dict[str, str]
    pages: dict[int, str]
    summaries: dict[str, str]
    analysis: dict[str, str]
    final_summary: str
    final_analysis: str


# --- Nodes ---

# ingest node that loads the document
def ingest_node(state: WorkflowState) -> WorkflowState:
    source, is_pdf = state["source"], state["is_pdf"]
    content = load_text(load_doc(source, is_pdf))
    logger.info(f"From {source} Ingested content length: {len(content)}, tokens: {count_tokens_approximately(content)}")
    return {**state, "raw_text": content}

# section parse node that splits the document into sections
def section_parse_node(state: WorkflowState) -> WorkflowState:
    sections = split_sections(state["raw_text"])
    logger.info(f"Parsed sections: {sections.keys()}")
    return {**state, "sections": sections}

# (not in use)ingest and split node that loads the document and splits it into sections
def ingest_and_split_node(state: WorkflowState) -> WorkflowState:
    source, is_pdf = state["source"], state["is_pdf"]
    sections = load_pdf_and_split_sections(source, is_pdf)
    logger.info(f"Ingested and split sections: {sections.keys()}")
    return {**state, "sections": sections}

# (not in use) page parse node that splits the document into pages
def page_parse_node(state: WorkflowState) -> WorkflowState:
    pages = load_and_split_pages(state["raw_text"], state["is_pdf"])
    logger.info(f"Parsed pages: {pages.keys()}")
    return {**state, "pages": pages}

# summarize node that summarizes the document
async def summarize_node(state: WorkflowState) -> WorkflowState:
    summaries = {}
    for section_name, section_text in state["sections"].items():
        summaries[section_name] = await summarize_section(section_name, section_text)
    return {**state, "summaries": summaries}

# analyze node that analyzes the document
async def analyze_node(state: WorkflowState) -> WorkflowState:
    analysis = {}
    for section_name, section_text in state["sections"].items():
        analysis[section_name] = await analyze_section(section_name, section_text)
    return {**state, "analysis": analysis}

# parallel summarize and analyze node that summarizes and analyzes the document in parallel
async def parallel_summarize_and_analyze(state: WorkflowState) -> WorkflowState:
    summary_task = asyncio.create_task(summarize_node(state))
    analyze_task = asyncio.create_task(analyze_node(state))

    summary_result, analyze_result = await asyncio.gather(summary_task, analyze_task)

    summaries = summary_result["summaries"]
    analysis = analyze_result["analysis"]
    
    return {**state, "summaries": summaries, "analysis": analysis}

# output node that finalizes the process
def output_node(state: WorkflowState) -> WorkflowState:
    result  = finalize_summary(state["summaries"], state["analysis"])
    return {**state, "final_summary": result.get("final_summary", ""), 
            "final_analysis": result.get("final_analysis", "")}


# --- Graph ---
builder = StateGraph(WorkflowState)

builder.add_node("ingest", RunnableLambda(ingest_node))
builder.add_node("parse", RunnableLambda(section_parse_node))
builder.add_node("summarize_and_analyze", RunnableLambda(parallel_summarize_and_analyze))
builder.add_node("output", RunnableLambda(output_node))

builder.set_entry_point("ingest")
builder.add_edge("ingest", "parse")
builder.add_edge("parse", "summarize_and_analyze")
builder.add_edge("summarize_and_analyze", "output")

builder.set_finish_point("output")
builder = builder.compile()



