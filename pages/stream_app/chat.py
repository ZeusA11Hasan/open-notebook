import asyncio
from typing import Union

import humanize
import nest_asyncio
import streamlit as st
from langchain_core.runnables import RunnableConfig
from loguru import logger

nest_asyncio.apply()

from open_notebook.domain.base import ObjectModel
from open_notebook.domain.notebook import ChatSession, Note, Notebook, Source
from open_notebook.graphs.chat import graph as chat_graph
from open_notebook.plugins.podcasts import PodcastConfig
from open_notebook.utils import parse_thinking_content, token_count
from pages.stream_app.utils import (
    convert_source_references,
    create_session_for_notebook,
)

from .note import make_note_from_chat


# todo: build a smarter, more robust context manager function
def build_context(notebook_id):
    from api.context_service import context_service

    # Convert context_config format for API
    context_config = {"sources": {}, "notes": {}}

    for id, status in st.session_state[notebook_id]["context_config"].items():
        if not id:
            continue

        item_type, item_id = id.split(":")
        if item_type not in ["note", "source"]:
            continue

        if item_type == "source":
            context_config["sources"][item_id] = status
        elif item_type == "note":
            context_config["notes"][item_id] = status

    # Get context via API
    result = context_service.get_notebook_context(
        notebook_id=notebook_id, context_config=context_config
    )

    # Store in session state for compatibility
    st.session_state[notebook_id]["context"] = {
        "note": result["notes"],
        "source": result["sources"],
    }

    return st.session_state[notebook_id]["context"]


async def execute_chat(txt_input, context, current_session):
    current_state = st.session_state[current_session.id]
    current_state["messages"] += [txt_input]
    current_state["context"] = context
    result = await chat_graph.ainvoke(
        input=current_state,
        config=RunnableConfig(configurable={"thread_id": current_session.id}),
    )
    await current_session.save()
    return result


def chat_sidebar(current_notebook: Notebook, current_session: ChatSession):
    context = build_context(notebook_id=current_notebook.id)
    tokens = token_count(
        str(context) + str(st.session_state[current_session.id]["messages"])
    )
    chat_tab, podcast_tab = st.tabs(["Chat", "Podcast"])
    with st.expander(f"Context ({tokens} tokens), {len(str(context))} chars"):
        st.json(context)
    with podcast_tab:
        with st.container(border=True):
            podcast_configs = asyncio.run(PodcastConfig.get_all())
            podcast_config_names = [pd.name for pd in podcast_configs]
            if len(podcast_configs) == 0:
                st.warning("No podcast configurations found")
            else:
                template = st.selectbox("Pick a template", podcast_config_names)
                selected_template = next(
                    filter(lambda x: x.name == template, podcast_configs)
                )
                episode_name = st.text_input("Episode Name")
                instructions = st.text_area(
                    "Instructions", value=selected_template.user_instructions
                )
                podcast_length = st.radio(
                    "Podcast Length",
                    ["Short (5-10 min)", "Medium (10-20 min)", "Longer (20+ min)"],
                )
                chunks = None
                min_chunk_size = None
                if podcast_length == "Short (5-10 min)":
                    longform = False
                elif podcast_length == "Medium (10-20 min)":
                    longform = True
                    chunks = 4
                    min_chunk_size = 600
                else:
                    longform = True
                    chunks = 8
                    min_chunk_size = 600

                if len(context.get("note", [])) + len(context.get("source", [])) == 0:
                    st.warning(
                        "No notes or sources found in context. You don't want a boring podcast, right? So, add some context first."
                    )
                else:
                    try:
                        if st.button("Generate"):
                            with st.spinner("Go grab a coffee, almost there..."):
                                selected_template.generate_episode(
                                    episode_name=episode_name,
                                    text=str(context),
                                    longform=longform,
                                    chunks=chunks,
                                    min_chunk_size=min_chunk_size,
                                    instructions=instructions,
                                )
                            st.success("Episode generated successfully")
                    except Exception as e:
                        st.error(f"Error generating episode - {str(e)}")
            st.page_link("pages/5_🎙️_Podcasts.py", label="🎙️ Go to Podcasts")
    with chat_tab:
        with st.expander(
            f"**Session:** {current_session.title} - {humanize.naturaltime(current_session.updated)}"
        ):
            new_session_name = st.text_input(
                "Current Session",
                key="new_session_name",
                value=current_session.title,
            )
            c1, c2 = st.columns(2)
            if c1.button("Rename", key="rename_session"):
                current_session.title = new_session_name
                current_session.save()
                st.rerun()
            if c2.button("Delete", key="delete_session_1"):
                current_session.delete()
                st.session_state[current_notebook.id]["active_session"] = None
                st.rerun()
            st.divider()
            new_session_name = st.text_input(
                "New Session Name",
                key="new_session_name_f",
                placeholder="Enter a name for the new session...",
            )
            st.caption("If no name provided, we'll use the current date.")
            if st.button("Create New Session", key="create_new_session"):
                new_session = create_session_for_notebook(
                    notebook_id=current_notebook.id, session_name=new_session_name
                )
                st.session_state[current_notebook.id]["active_session"] = new_session.id
                st.rerun()
            st.divider()
            sessions = asyncio.run(current_notebook.get_chat_sessions())
            if len(sessions) > 1:
                st.markdown("**Other Sessions:**")
                for session in sessions:
                    if session.id == current_session.id:
                        continue

                    st.markdown(
                        f"{session.title} - {humanize.naturaltime(session.updated)}"
                    )
                    if st.button(label="Load", key=f"load_session_{session.id}"):
                        st.session_state[current_notebook.id]["active_session"] = (
                            session.id
                        )
                        st.rerun()
        with st.container(border=True):
            request = st.chat_input("Enter your question")
            # removing for now since it's not multi-model capable right now
            if request:
                response = asyncio.run(
                    execute_chat(
                        txt_input=request,
                        context=context,
                        current_session=current_session,
                    )
                )
                st.session_state[current_session.id]["messages"] = response["messages"]

            for msg in st.session_state[current_session.id]["messages"][::-1]:
                if msg.type not in ["human", "ai"]:
                    continue
                if not msg.content:
                    continue

                with st.chat_message(name=msg.type):
                    if msg.type == "ai":
                        # Parse thinking content for AI messages
                        thinking_content, cleaned_content = parse_thinking_content(
                            msg.content
                        )

                        # Show thinking content in expander if present
                        if thinking_content:
                            with st.expander("🤔 AI Reasoning", expanded=False):
                                st.markdown(thinking_content)

                        # Show the cleaned regular content
                        if cleaned_content:
                            st.markdown(convert_source_references(cleaned_content))
                        elif (
                            msg.content
                        ):  # Fallback to original if cleaning resulted in empty content
                            st.markdown(convert_source_references(msg.content))

                        # New Note button for AI messages
                        if st.button("💾 New Note", key=f"render_save_{msg.id}"):
                            make_note_from_chat(
                                content=msg.content,
                                notebook_id=current_notebook.id,
                            )
                            st.rerun()
                    else:
                        # Human messages - display normally
                        st.markdown(convert_source_references(msg.content))
