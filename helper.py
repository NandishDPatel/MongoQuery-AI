import streamlit as st
import pandas as pd
from typing import Dict, Any
from pymongo import MongoClient
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def apply_custom_css(file_name="./styles.css"):
    with open(file_name) as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    print("Custom CSS applied.")

@st.cache_resource(ttl="2h")
def configure_mongo(uri, db_name, collection_name):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        collection = db[collection_name]
        client.server_info()
        return collection
    except Exception as e:
        st.error(f"MongoDB connection error: {e}")
        return None

def get_collection_schema(collection, collection_name):
    try:
        sample_docs = list(collection.find().limit(1))
        if not sample_docs:
            return "Collection is empty.", []
        all_keys = set()
        for doc in sample_docs:
            all_keys.update(doc.keys())
        schema = {k: type(sample_docs[0][k]).__name__ for k in all_keys if k != "_id"}
        schema_info = f"\nCollection: {collection_name}\n\n Sample record:\n"
        for key, val in schema.items():
            schema_info += f"- `{key}`: `{val}`\n"
        return schema_info, sample_docs
    except Exception as e:
        return f"Error getting schema: {str(e)}", []

def query_mongodb(collection, query_dict: Dict[str, Any]):
    """Execute MongoDB query with proper sorting and formatting"""
    try:
        # Start with find operation
        query = collection.find(
            query_dict.get("filter", {}), query_dict.get("projection", {})
        )

        # Apply sort if specified and not empty
        if query_dict.get("sort"):
            query = query.sort(query_dict["sort"])

        # Apply skip if specified and > 0
        if query_dict.get("skip", 0) > 0:
            query = query.skip(query_dict["skip"])

        # Apply limit if specified and > 0
        limit = query_dict.get("limit", 0)
        if limit > 0:
            query = query.limit(limit)
        else:
            # Default limit to prevent huge outputs
            query = query.limit(100)

        results = list(query)

        # Convert ObjectId to string for JSON serialization
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])

        return results

    except Exception as e:
        st.error(f"Error querying MongoDB: {str(e)}")
        return []

def count_documents(collection, filter_dict=None):
    try:
        filter_dict = filter_dict or {}
        return collection.count_documents(filter_dict)
    except Exception as e:
        return f"Error counting documents: {str(e)}"

def process_user_query(user_input: str, llm) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
        You are an expert MongoDB query generator.
        You will be given natural language questions about the database collection.
        Return ONLY a valid JSON object in this flexible format:
        {{
            "filter": {{ ... }},
            "projection": {{ ... }},
            "sort": {{ ... }},
            "limit": number,
            "skip": number
        }}
        Rules:
        - "filter": for query conditions (use {{}} for empty filter)
        - "projection": for fields to show (use {{}} for all fields)
        - "sort": field and direction (1 for ascending, -1 for descending) - ONLY include if sorting is needed
        - "limit": maximum number of documents - ONLY include if limiting is needed  
        - "skip": number of documents to skip - ONLY include if skipping is needed
        - Only include fields that are actually needed for the query
        - For empty values, use empty objects {{}}
        - Always return valid JSON that can be parsed by json.loads()
        - Support all MongoDB operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, $and, $or, $regex, etc.

        Examples:
        User: "find students with GPA above 3.5"
        Response: {{"filter": {{"gpa": {{"$gt": 3.5}}}}, "projection": {{}}}}

        User: "get top 5 students by GPA"
        Response: {{"filter": {{}}, "projection": {{}}, "sort": {{"gpa": -1}}, "limit": 5}}

        User: "show me names and emails of students from CS department"
        Response: {{"filter": {{"department": "CS"}}, "projection": {{"name": 1, "email": 1}}}}

        User: "find students who failed any course (GPA < 2.0) and sort by name"
        Response: {{"filter": {{"gpa": {{"$lt": 2.0}}}}, "projection": {{}}, "sort": {{"name": 1}}}}

        User: "get second page of 10 students, skip first 10"
        Response: {{"filter": {{}}, "projection": {{}}, "skip": 10, "limit": 10}}
        """,
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    try:
        response = chain.invoke({"input": user_input})

        # Clean the response - extract JSON if it's wrapped in markdown or other text
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            response = json_match.group()

        # Parse and validate JSON
        query_dict = json.loads(response)

        # Set default values for missing optional fields
        default_query = {
            "filter": {},
            "projection": {},
            "sort": {},
            "limit": 0,
            "skip": 0,
        }

        for key in default_query:
            if key not in query_dict:
                query_dict[key] = default_query[key]

        return query_dict

    except Exception as e:
        return default_query

def display_unified_results(results, query_dict=None):
    if not results:
        st.info("No documents found matching your query.")
        return
    with st.container():
        if results and isinstance(results[0], dict):
            try:
                df = pd.DataFrame(results)
                # Remove _id column if user didn't specifically ask for it
                if "_id" in df.columns and not (
                    query_dict
                    and query_dict.get("projection")
                    and "_id" in query_dict.get("projection", {})
                ):
                    df = df.drop("_id", axis=1)
                # Display the dataframe
                st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.warning("Could not display as table. Showing raw data:")
                st.json(results)
        else:
            st.json(results)


def display_compact_query_analysis(query_dict):
    with st.container():
        st.markdown("**Query Analysis**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if query_dict.get("filter"):
                st.metric("Filters", "Applied", delta=None)
            else:
                st.metric("Filters", "None", delta=None)
        with col2:
            if query_dict.get("projection"):
                st.metric("Fields", "Selected", delta=None)
            else:
                st.metric("Fields", "All", delta=None)
        with col3:
            if query_dict.get("sort"):
                st.metric("Sorting", "Applied", delta=None)
            else:
                st.metric("Sorting", "None", delta=None)
        with col4:
            limit = query_dict.get("limit", 0)
            skip = query_dict.get("skip", 0)
            if limit > 0:
                st.metric("Limit", limit, delta=None)
            elif skip > 0:
                st.metric("Skip", skip, delta=None)
            else:
                st.metric("Paging", "None", delta=None)

        with st.expander("View Query Details", expanded=False):
            st.json(query_dict)


def display_chat_message(role, content, query_dict=None, results=None):
    if role == "user":
        st.chat_message("user").write(content)
    else:
        if isinstance(content, dict) and "type" in content:
            if content["type"] == "schema":
                st.chat_message("assistant").markdown("### 📋 Collection Schema")
                st.chat_message("assistant").markdown(content["data"])

            elif content["type"] == "count":
                st.chat_message("assistant").markdown(
                    f"### Total documents: **{content['data']}**"
                )

            elif content["type"] == "query_results":
                # Unified display for query results
                # st.chat_message("assistant").markdown("### Query Results")
                display_compact_query_analysis(content["query_dict"])
                display_unified_results(content["results"], content["query_dict"])

            elif content["type"] == "all_documents":
                st.chat_message("assistant").markdown("### 📄 All Documents")
                display_unified_results(content["results"], content["query_dict"])

            elif content["type"] == "error":
                st.chat_message("assistant").error(f"❌ {content['data']}")

            else:
                st.chat_message("assistant").write(content["data"])
        else:
            st.chat_message("assistant").write(content)