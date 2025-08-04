from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages.utils import count_tokens_approximately
import dotenv
import os
import logging

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

chat = ChatOpenAI(model="gpt-3.5-turbo", 
                  temperature=0.3, 
                  openai_api_key=openai_api_key)


async def summarize_section(section_name: str, section_text: str) -> str:

    prompt = """
    You are an expert research assistant. You are given a section of a research paper.
    Given a section, provide a summary of the section in 100 words.
    Do not lose any important information. Do not add any additional information.
    """

    context = f"""
    Section Title: {section_name}

    {section_text}
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=context)
    ]

    response = await chat.ainvoke(messages)
    logging.info(f"<{section_name}> raw length: {len(section_text)}, raw tokens: {count_tokens_approximately(section_text)}")
    return response.content


async def analyze_section(section_name: str, section_text: str) -> str:

    prompt = """
    You are an peer-reviewer for a scientific paper. Given a section of a research paper,
    analyze the section and provide below in 100 words.
    - The research questions, hypotheses, and/or arguments if mentioned.
    - Any logical flows or vague claims, if present.
    - Overal clarity, completeness, structure, and quality of the section.
    - if the section name is well representing the section content.
    Output format: string without any markdown formatting.
    """
    context = f"""
    Section Title: {section_name}

    {section_text}
    """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=context)
    ]

    response = await chat.ainvoke(messages)
    return response.content
