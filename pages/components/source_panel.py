import asyncio

import nest_asyncio
import streamlit as st
from humanize import naturaltime

from open_notebook.domain.models import model_manager
from open_notebook.domain.notebook import Source
from open_notebook.domain.transformation import Transformation
from open_notebook.graphs.transformation import graph as transform_graph
from pages.stream_app.utils import check_models

nest_asyncio.apply()


def source_panel(source_id: str, notebook_id=None, modal=False):
    check_models(only_mandatory=False)
    source: Source = asyncio.run(Source.get(source_id))
    if not source:
        raise ValueError(f"Source not found: {source_id}")

    current_title = source.title if source.title else "No Title"
    source.title = st.text_input("Title", value=current_title)
    if source.title != current_title:
        from api.sources_service import sources_service
        sources_service.update_source(source)
        st.toast("Saved new Title")

    process_tab, source_tab = st.tabs(["Process", "Source"])
    with process_tab:
        c1, c2 = st.columns([4, 2])
        with c1:
            title = st.empty()
            if source.title:
                title.subheader(source.title)
            if source.asset and source.asset.url:
                from_src = f"from URL: {source.asset.url}"
            elif source.asset and source.asset.file_path:
                from_src = f"from file: {source.asset.file_path}"
            else:
                from_src = "from text"
            st.caption(f"Created {naturaltime(source.created)}, {from_src}")
            for insight in asyncio.run(source.get_insights()):
                with st.expander(f"**{insight.insight_type}**"):
                    st.markdown(insight.content)
                    x1, x2 = st.columns(2)
                    if x1.button(
                        "Delete", type="primary", key=f"delete_insight_{insight.id}"
                    ):
                        insight.delete()
                        st.rerun(scope="fragment" if modal else "app")
                        st.toast("Source deleted")
                    if notebook_id:
                        if x2.button(
                            "Save as Note", icon="📝", key=f"save_note_{insight.id}"
                        ):
                            from api.notes_service import notes_service
                            notes_service.create_note(
                                content=insight.content,
                                title=f"{insight.insight_type} from source {source.title}",
                                note_type="ai",
                                notebook_id=notebook_id
                            )
                            st.toast("Saved as Note. Refresh the Notebook to see it.")

        with c2:
            transformations = Transformation.get_all(order_by="name asc")
            if transformations:
                with st.container(border=True):
                    transformation = st.selectbox(
                        "Run a transformation",
                        transformations,
                        key=f"transformation_{source.id}",
                        format_func=lambda x: x.name,
                    )
                    st.caption(transformation.description if transformation else "")
                    if st.button("Run"):
                        asyncio.run(
                            transform_graph.ainvoke(
                                input=dict(source=source, transformation=transformation)
                            )
                        )
                        st.rerun(scope="fragment" if modal else "app")
            else:
                st.markdown(
                    "No transformations created yet. Create new Transformation to use this feature."
                )

            if not model_manager.embedding_model:
                help = (
                    "No embedding model found. Please, select one on the Models page."
                )
            else:
                help = "This will generate your embedding vectors on the database for powerful search capabilities"

            if len(asyncio.run(source.get_embedded_chunks())) == 0 and st.button(
                "Embed vectors",
                icon="🦾",
                help=help,
                disabled=model_manager.embedding_model is None,
            ):
                from api.embedding_service import embedding_service
                result = embedding_service.embed_content(source.id, "source")
                st.success(result.get("message", "Embedding complete"))

            with st.container(border=True):
                st.caption(
                    "Deleting the source will also delete all its insights and embeddings"
                )
                if st.button(
                    "Delete", type="primary", key=f"bt_delete_source_{source.id}"
                ):
                    from api.sources_service import sources_service
                    sources_service.delete_source(source.id)
                    st.rerun()

    with source_tab:
        st.subheader("Content")
        st.markdown(source.full_text)
