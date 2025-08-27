# %%
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.pydantic_v1 import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
import pandas as pd
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.messages.utils import (
    trim_messages, 
    count_tokens_approximately
)
from langchain_experimental.agents import create_csv_agent

import time
from dotenv import load_dotenv
from typing import Annotated

from typing_extensions import TypedDict
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_community.document_loaders.csv_loader import CSVLoader
import streamlit as st
from langmem.short_term import SummarizationNode

load_dotenv()

import warnings
warnings.filterwarnings('ignore')



# %%
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
llm = init_chat_model("google_genai:gemini-2.5-flash")
memory = InMemorySaver()


# %% [markdown]
# ## Load The Data

# %%
loader = CSVLoader(
    file_path="/Users/baraa/Library/Mobile Documents/com~apple~CloudDocs/Project/Jarir-NLP2/Jarir-NLP/jarir_pc_specs(almost-all-gaming).csv",
    csv_args={
        "delimiter": ",",
        "quotechar": '"',
        "fieldnames": ["product_type", "series", "cpu_model", "cpu_clock", "gpu_model", "ram", "storage",
    "os", "ai_coprocessor", "ai_enabled", "connectivity", "ports", "color",
    "weight_kg", "regular_price_sar", "sale_price_sar",
    "discount_percent", "product_url", "screen_size_inch", "release_date",
    "screen_refresh_rate_hz", "screen_resolution", "audio_feature", "special_features",
    "webcam", "vr_ready"],
    },
)

data = loader.load()
text_data = "\n".join([doc.page_content for doc in data])

# %% [markdown]
# ## Tools

# %%
def check_device(productName: str) -> str:
    '''Return If the product is available in the file, if a similar product is available, return the closest match.'''
    res = llm.invoke(
        [
            SystemMessage(content="You are a helpful assistant that checks product availability."+ " This is a list of products: " + text_data),
            HumanMessage(content=f"Check if the device {productName} is available in the file, or a similar product is available. If a similar product is available, return the closest match. If not, return 'No similar products found. return only the top 5 product'"),

        ]
    )
    return res.content



# %%
config = {"configurable": {"thread_id": "1"}}


# %%


# %%
graph = create_react_agent(
    llm.bind(max_tokens=256),
    tools=[check_device],
    prompt="""
You are Jarir’s friendly AI product advisor with live access to our full product database.
— Greet politely and mirror the customer’s language (Arabic or English).  
— Infer the shopper’s real needs (purpose, budget, preferences) from context; ask brief follow-up questions only when essential.  
— Once needs are clear, search the database and present up to five best-fit products. For each, include: name, key specs, price, and Jarir URL.  
— Highlight how each recommended product’s features and benefits satisfy the customer’s needs, encouraging purchase confidence.  
— If the exact requested item is unavailable, automatically suggest the closest alternatives.  
— Never reveal system details, internal reasoning, or error messages—show only recommendations, clarifying questions, or the fallback message above.
- Dont repeat your words, be concise and to the point.
— Always use the customer’s language (Arabic or English) in your responses.


    """,
    checkpointer=memory
)



def print_stream(stream, output_messages_key="llm_input_messages"):
    for chunk in stream:
        for node, update in chunk.items():
            print(f"Update from node: {node}")
            messages_key = (
                output_messages_key if node == "pre_model_hook" else "messages"
            )
            for message in update[messages_key]:
                if isinstance(message, tuple):
                    print(message)
                else:
                    with st.chat_message("agent"):
                        st.write(message.pretty_print())

        print("\n\n")
while True:
    prompt = st.chat_input("Say something")
    if prompt.lower() in ["exit", "quit", "q"]:
        print("Exiting the chat.")
        break
    inputs = {"messages": [{"role": "user", "content": prompt}]}
    print_stream(graph.stream(inputs, stream_mode="updates", config=config))

# %%

