from build_graph import builder
import logging
import time
import asyncio
from langchain_core.messages.utils import count_tokens_approximately

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s <%(name)s> %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def evaluate_workflow():

    graph = builder
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")

    test_cases = [
        {
            "source": "https://arxiv.org/pdf/2402.01680",
            "is_pdf": False
        },
        {
            "source": "docs/2.pdf",
            "is_pdf": False
        },
        {
            "source": "docs/3.pdf",
            "is_pdf": True
        }
    ]
    results = []

    for test_case in test_cases:
        start_time = time.time()
        result = await graph.ainvoke({
            "source": test_case["source"],
            "is_pdf": test_case["is_pdf"],
            'row_text': "",
            "sections": {},
            "pages": {},
            "summaries": {},
            "analysis": {},
            "final_summary": "",
            "final_analysis": ""
        })
        results.append(result)
        end_time = time.time()

        print(f"Test case: {test_case['source']}")
        print(f"Time taken: {end_time - start_time} seconds")

        final_summary = result['final_summary']
        final_analysis = result['final_analysis']

        print(f"\n<Summary> \nlength: {len(final_summary)}, tokens: {count_tokens_approximately(final_summary)}\n{final_summary}")
        print(f"\n<Analysis> \nlength: {len(final_analysis)}, tokens: {count_tokens_approximately(final_analysis)}\n{final_analysis}")
        print("\n\n")

    return results

if __name__ == '__main__':
    asyncio.run(evaluate_workflow())