import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
import os
import re
from helper import *

load_dotenv()

MONGO_STRING = os.environ["MONGODB_CONNECTION_STRING"]
GROQ_API = os.environ["GROQ_KEY"]

def apply_custom_css(file_name="./styles.css"):
    with open(file_name) as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    print("Custom CSS applied.")
apply_custom_css()

st.set_page_config(page_title="\n\nLangChain: Chat with MongoDB")
st.title("LangChain: Chat with MongoDB")

# --- Sidebar Input Section ---
st.sidebar.markdown(
    "<h1 style='text-align:center;color:black;'>MongoDB Setup</h1>",
    unsafe_allow_html=True,
)
mongo_uri = MONGO_STRING
mongo_db_name = st.sidebar.text_input(
    "Database Name", value=st.session_state.get("mongo_db_name", "")
)
mongo_collection_name = st.sidebar.text_input(
    "Collection Name", value=st.session_state.get("mongo_collection_name", "")
)
api_key = GROQ_API
submit_clicked = st.sidebar.button("Submit")

if submit_clicked:
    if not mongo_uri or not mongo_db_name or not mongo_collection_name or not api_key:
        st.warning("⚠️ Please fill in all fields before submitting.")
        st.stop()

    # Save in session_state so they persist
    st.session_state.mongo_uri = mongo_uri
    st.session_state.mongo_db_name = mongo_db_name
    st.session_state.mongo_collection_name = mongo_collection_name
    st.session_state.api_key = api_key

    st.session_state.llm = ChatGroq(
        groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True
    )

    collection = configure_mongo(mongo_uri, mongo_db_name, mongo_collection_name)
    if collection is None:
        st.error("❌ Failed to connect to MongoDB.")
        st.stop()

    st.session_state.mongo_collection = collection

    schema_info, sample_docs = get_collection_schema(collection, mongo_collection_name)
    st.session_state.schema_info = schema_info
    st.session_state.sample_docs = sample_docs

# --- Show Schema if Connection Exists ---
if "mongo_collection" in st.session_state:
    st.markdown(st.session_state.schema_info)

    # Display sample docs in a cleaner way
    with st.expander("Sample Document", expanded=False):
        if st.session_state.sample_docs:
            st.json(st.session_state.sample_docs[0])
        else:
            st.info("No sample documents available.")

    # --- Chat Section ---
    st.markdown("---")
    st.subheader("💬 Chat with MongoDB")

    # Initialize messages in session_state if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Connected to **{st.session_state.mongo_collection_name}**. Ask me anything about it!",
            }
        ]

    # Display all previous messages
    for msg in st.session_state.messages:
        if isinstance(msg["content"], dict) and "type" in msg["content"]:
            display_chat_message(
                msg["role"],
                msg["content"],
                msg["content"].get("query_dict"),
                msg["content"].get("results"),
            )
        else:
            display_chat_message(msg["role"], msg["content"])

    user_query = st.chat_input("Ask your question about the collection...")

    if user_query:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Display user message immediately
        st.chat_message("user").write(user_query)

        # Process the query and generate response
        with st.chat_message("assistant"):
            try:
                if "schema" in user_query.lower():
                    result_data = {
                        "type": "schema",
                        "data": st.session_state.schema_info,
                    }
                    display_chat_message("assistant", result_data)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": result_data}
                    )

                elif "all documents" in user_query.lower():
                    query_dict = {"filter": {}, "projection": {}, "limit": 50}
                    docs = query_mongodb(st.session_state.mongo_collection, query_dict)
                    result_data = {
                        "type": "all_documents",
                        "query_dict": query_dict,
                        "results": docs,
                    }
                    display_chat_message("assistant", result_data, query_dict, docs)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": result_data}
                    )

                elif "count" in user_query.lower() or "how many" in user_query.lower():
                    count = count_documents(st.session_state.mongo_collection)
                    result_data = {"type": "count", "data": count}
                    display_chat_message("assistant", result_data)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": result_data}
                    )

                else:
                    with st.spinner("Analyzing your query..."):
                        query_dict = process_user_query(
                            user_query, st.session_state.llm
                        )

                    with st.spinner("Executing query..."):
                        docs = query_mongodb(
                            st.session_state.mongo_collection, query_dict
                        )

                    result_data = {
                        "type": "query_results",
                        "query_dict": query_dict,
                        "results": docs,
                    }
                    display_chat_message("assistant", result_data, query_dict, docs)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": result_data}
                    )

            except Exception as e:
                error_data = {"type": "error", "data": f"Error: {str(e)}"}
                display_chat_message("assistant", error_data)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_data}
                )

        st.rerun()
else:
    st.info("👈 Enter MongoDB details in the sidebar and click **Submit** button.")
