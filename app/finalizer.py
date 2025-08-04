from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages.utils import count_tokens_approximately
import dotenv
import os
import logging
import json

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

chat = ChatOpenAI(model="gpt-3.5-turbo", 
                  temperature=0.2, 
                  openai_api_key=openai_api_key)


def finalize_summary(summaries: dict[str, str], analysis: dict[str, str]) -> dict:
    prompt = """
    You are an expert research assistant. Combine the summaries and critical analysis
    of each section, finalize the scientific paper review in 300 words.

    Return in the following JSON format:
    {{'final_summary': final summary (string), 'final_analysis': final analysis (string)}}
    """
    
    # combine summaries and analysis for each section
    context_parts = []
    for section in summaries:
        summary_section = summaries[section]
        analysis_section = analysis.get(section, "")

        #summary_text = summary_section[:500] if len(summary_section) > 500 else summary_section
        #analysis_text = analysis_section[:500] if len(analysis_section) > 500 else analysis_section

        context_parts.append(f"Section: {section}\nSummary: {summary_section}\nAnalysis: {analysis_section}")
        logging.info(f"<{section}> summary length: {len(summary_section)}, summary_tokens: {count_tokens_approximately(analysis_section)}, analysis length: {len(analysis_section)}, analysis_tokens: {count_tokens_approximately(analysis_section)}")

    context = "\n".join(context_parts)
    logging.info(f"Total finalizer context length: {len(context)}, tokens: {count_tokens_approximately(context)}")

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=context)
    ]

    response = chat.invoke(messages)

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        logger.warning("Failed to parse finalizer response as JSON")
        return {
            'final_summary': response.content,
            'final_analysis': ""
        }
    
    


