import asyncio
from datetime import datetime

import httpx
import streamlit as st

from api.models_service import models_service
from pages.stream_app.utils import setup_page

setup_page("🎙️ Podcasts", only_check_mandatory_models=False)

# API base URL
API_BASE = "http://localhost:5055/api"

@st.dialog("Confirm Delete Episode")
def confirm_delete_episode(episode_id, episode_name):
    st.warning(f"Are you sure you want to delete episode **{episode_name}**?")
    st.write("This action will:")
    st.write("• Delete the episode from the database")
    st.write("• Delete the audio file from disk (if it exists)")
    st.error("**This action cannot be undone!**")
    
    col_confirm1, col_confirm2 = st.columns(2)
    with col_confirm1:
        if st.button("✅ Yes, Delete", type="primary"):
            success = asyncio.run(delete_episode(episode_id))
            if success:
                st.success("Episode deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete episode")
    
    with col_confirm2:
        if st.button("❌ Cancel"):
            st.rerun()

@st.dialog("Confirm Delete Speaker Profile")
def confirm_delete_speaker_profile(profile_id, profile_name):
    st.warning(f"Are you sure you want to delete speaker profile **{profile_name}**?")
    st.write("This action cannot be undone.")
    
    col_confirm1, col_confirm2 = st.columns(2)
    with col_confirm1:
        if st.button("✅ Yes, Delete", type="primary"):
            success = asyncio.run(delete_speaker_profile(profile_id))
            if success:
                st.success("Speaker profile deleted!")
                st.rerun()
            else:
                st.error("Failed to delete speaker profile")
    
    with col_confirm2:
        if st.button("❌ Cancel"):
            st.rerun()

@st.dialog("Confirm Delete Episode Profile")
def confirm_delete_episode_profile(profile_id, profile_name):
    st.warning(f"Are you sure you want to delete episode profile **{profile_name}**?")
    st.write("This action cannot be undone.")
    
    col_confirm1, col_confirm2 = st.columns(2)
    with col_confirm1:
        if st.button("✅ Yes, Delete", type="primary"):
            success = asyncio.run(delete_episode_profile(profile_id))
            if success:
                st.success("Episode profile deleted!")
                st.rerun()
            else:
                st.error("Failed to delete episode profile")
    
    with col_confirm2:
        if st.button("❌ Cancel"):
            st.rerun()

@st.dialog("Configure Speaker Profile", width="large")
def speaker_configuration_dialog(mode="create", profile_id=None, episode_context=None):
    """Unified dialog for speaker profile create/edit/select"""
    
    # Initialize session state for dialog
    if "dialog_speakers" not in st.session_state:
        st.session_state.dialog_speakers = [{"name": "", "voice_id": "", "backstory": "", "personality": ""}]
    
    if mode == "create":
        st.subheader("🎤 Create New Speaker Profile")
    elif mode == "edit":
        st.subheader("✏️ Edit Speaker Profile")
        # Load existing profile data
        if profile_id and "dialog_loaded" not in st.session_state:
            speaker_profiles = asyncio.run(fetch_speaker_profiles())
            profile = next((p for p in speaker_profiles if p['id'] == profile_id), None)
            if profile:
                st.session_state.dialog_loaded = True
                st.session_state.dialog_speakers = profile.get('speakers', [])
                st.session_state.dialog_name = profile.get('name', '')
                st.session_state.dialog_description = profile.get('description', '')
                st.session_state.dialog_tts_provider = profile.get('tts_provider', '')
                st.session_state.dialog_tts_model = profile.get('tts_model', '')
    elif mode == "select":
        st.subheader("⚙️ Configure Speaker for Episode")
        st.info("Select mode coming in Phase 5")
        return
    
    # TTS Provider/Model selection outside form for reactivity
    col1, col2 = st.columns(2)
    with col1:
        default_provider = st.session_state.get("dialog_tts_provider", list(tts_provider_models.keys())[0])
        provider_idx = list(tts_provider_models.keys()).index(default_provider) if default_provider in tts_provider_models else 0
        tts_provider = st.selectbox("TTS Provider*", list(tts_provider_models.keys()), index=provider_idx, key="dialog_tts_provider")
    with col2:
        default_model = st.session_state.get("dialog_tts_model", "")
        model_idx = 0
        if default_model in tts_provider_models[tts_provider]:
            model_idx = tts_provider_models[tts_provider].index(default_model)
        tts_model = st.selectbox("TTS Model*", tts_provider_models[tts_provider], index=model_idx, key="dialog_tts_model")
    
    with st.form("speaker_config_dialog_form"):
        col3, col4 = st.columns(2)
        
        with col3:
            sp_name = st.text_input("Profile Name*", value=st.session_state.get("dialog_name", ""), placeholder="e.g., tech_experts")
        
        with col4:
            sp_description = st.text_area("Description", value=st.session_state.get("dialog_description", ""), placeholder="Brief description of this speaker configuration")
        
        # Speakers configuration
        st.subheader("🎙️ Speakers (1-4 speakers)")
        
        # Display current speakers
        for i, speaker in enumerate(st.session_state.dialog_speakers):
            with st.container(border=True):
                st.write(f"**Speaker {i+1}:**")
                col_spk1, col_spk2 = st.columns(2)
                
                with col_spk1:
                    speaker["name"] = st.text_input(f"Name*", value=speaker.get("name", ""), key=f"dialog_speaker_{i}_name")
                    speaker["voice_id"] = st.text_input(f"Voice ID*", value=speaker.get("voice_id", ""), key=f"dialog_speaker_{i}_voice")
                
                with col_spk2:
                    speaker["backstory"] = st.text_area(f"Backstory*", value=speaker.get("backstory", ""), key=f"dialog_speaker_{i}_backstory")
                    speaker["personality"] = st.text_area(f"Personality*", value=speaker.get("personality", ""), key=f"dialog_speaker_{i}_personality")
        
        # Buttons to add/remove speakers
        col5, col6 = st.columns(2)
        with col5:
            if st.form_submit_button("➕ Add Speaker") and len(st.session_state.dialog_speakers) < 4:
                st.session_state.dialog_speakers.append({"name": "", "voice_id": "", "backstory": "", "personality": ""})
                st.rerun()
        
        with col6:
            if st.form_submit_button("➖ Remove Speaker") and len(st.session_state.dialog_speakers) > 1:
                st.session_state.dialog_speakers.pop()
                st.rerun()
        
        # Submit buttons
        col7, col8 = st.columns(2)
        with col7:
            submit_label = "💾 Save Changes" if mode == "edit" else "✅ Create Profile"
            if st.form_submit_button(submit_label):
                # Validate speakers
                valid_speakers = []
                for speaker in st.session_state.dialog_speakers:
                    if speaker.get("name") and speaker.get("voice_id") and speaker.get("backstory") and speaker.get("personality"):
                        valid_speakers.append(speaker)
                
                if sp_name and valid_speakers:
                    profile_data = {
                        "name": sp_name,
                        "description": sp_description,
                        "tts_provider": tts_provider,
                        "tts_model": tts_model,
                        "speakers": valid_speakers
                    }
                    
                    if mode == "create":
                        success = asyncio.run(create_speaker_profile(profile_data))
                        if success:
                            st.success("Speaker profile created successfully!")
                            # Clear session state
                            for key in ["dialog_speakers", "dialog_name", "dialog_description", "dialog_tts_provider", "dialog_tts_model", "dialog_loaded"]:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error("Failed to create speaker profile")
                    elif mode == "edit":
                        success = asyncio.run(update_speaker_profile(profile_id, profile_data))
                        if success:
                            st.success("Speaker profile updated successfully!")
                            # Clear session state
                            for key in ["dialog_speakers", "dialog_name", "dialog_description", "dialog_tts_provider", "dialog_tts_model", "dialog_loaded"]:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error("Failed to update speaker profile")
                else:
                    st.error("Please fill in all required fields (*) for at least one speaker")
        
        with col8:
            if st.form_submit_button("❌ Cancel"):
                # Clear session state
                for key in ["dialog_speakers", "dialog_name", "dialog_description", "dialog_tts_provider", "dialog_tts_model", "dialog_loaded"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def get_status_emoji(status: str) -> str:
    """Get emoji for job status"""
    status_map = {
        "completed": "✅",
        "running": "🔄",
        "processing": "🔄", 
        "failed": "❌",
        "error": "❌",
        "pending": "⏳",
        "submitted": "⏳"
    }
    return status_map.get(status, "❓")

def format_relative_time(created_str: str) -> str:
    """Format creation time as relative time"""
    try:
        # Parse ISO format datetime
        if created_str.endswith('Z'):
            created_str = created_str[:-1] + '+00:00'
        created = datetime.fromisoformat(created_str)
        
        # Simple relative time calculation
        now = datetime.now(created.tzinfo)
        diff = now - created
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except Exception:
        return "Unknown"

async def fetch_episodes():
    """Fetch episodes from API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/podcasts/episodes")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to fetch episodes: {response.status_code}")
                return []
    except Exception as e:
        st.error(f"Error fetching episodes: {str(e)}")
        return []

async def fetch_episode_profiles():
    """Fetch episode profiles from API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/episode-profiles")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to fetch episode profiles: {response.status_code}")
                return []
    except Exception as e:
        st.error(f"Error fetching episode profiles: {str(e)}")
        return []

async def fetch_speaker_profiles():
    """Fetch speaker profiles from API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/speaker-profiles")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to fetch speaker profiles: {response.status_code}")
                return []
    except Exception as e:
        st.error(f"Error fetching speaker profiles: {str(e)}")
        return []

async def create_episode_profile(profile_data):
    """Create new episode profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/episode-profiles", json=profile_data)
            return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"Error creating episode profile: {str(e)}")
        return False

async def update_episode_profile(profile_id, profile_data):
    """Update episode profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{API_BASE}/episode-profiles/{profile_id}", json=profile_data)
            return response.status_code == 200
    except Exception as e:
        st.error(f"Error updating episode profile: {str(e)}")
        return False

async def delete_episode_profile(profile_id):
    """Delete episode profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_BASE}/episode-profiles/{profile_id}")
            return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting episode profile: {str(e)}")
        return False

async def duplicate_episode_profile(profile_id):
    """Duplicate episode profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/episode-profiles/{profile_id}/duplicate")
            return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"Error duplicating episode profile: {str(e)}")
        return False

async def create_speaker_profile(profile_data):
    """Create new speaker profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/speaker-profiles", json=profile_data)
            return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"Error creating speaker profile: {str(e)}")
        return False

async def update_speaker_profile(profile_id, profile_data):
    """Update speaker profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{API_BASE}/speaker-profiles/{profile_id}", json=profile_data)
            return response.status_code == 200
    except Exception as e:
        st.error(f"Error updating speaker profile: {str(e)}")
        return False

async def delete_speaker_profile(profile_id):
    """Delete speaker profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_BASE}/speaker-profiles/{profile_id}")
            return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting speaker profile: {str(e)}")
        return False

async def duplicate_speaker_profile(profile_id):
    """Duplicate speaker profile"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/speaker-profiles/{profile_id}/duplicate")
            return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"Error duplicating speaker profile: {str(e)}")
        return False

async def delete_episode(episode_id):
    """Delete podcast episode and its audio file"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_BASE}/podcasts/episodes/{episode_id}")
            return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting episode: {str(e)}")
        return False

def analyze_speaker_usage(speakers, episodes):
    """Analyze which speaker profiles are used by episode profiles"""
    usage_map = {}
    for speaker in speakers:
        speaker_name = speaker.get('name', '')
        usage_map[speaker_name] = 0
    
    for episode in episodes:
        speaker_config = episode.get('speaker_config', '')
        if speaker_config in usage_map:
            usage_map[speaker_config] += 1
    
    return usage_map

def render_speaker_info_inline(speaker_config, speaker_profiles):
    """Render speaker information inline within episode profile cards"""
    if not speaker_config:
        st.warning("⚠️ No speaker profile assigned")
        return
    
    # Find the matching speaker profile
    speaker_profile = None
    for profile in speaker_profiles:
        if profile.get('name') == speaker_config:
            speaker_profile = profile
            break
    
    if not speaker_profile:
        st.error(f"❌ Speaker profile '{speaker_config}' not found")
        return
    
    # Display speaker info
    st.write(f"**🎤 Speaker Profile:** {speaker_config}")
    st.write(f"**TTS:** {speaker_profile.get('tts_provider', 'N/A')}/{speaker_profile.get('tts_model', 'N/A')}")
    
    speakers = speaker_profile.get('speakers', [])
    if speakers:
        st.write(f"**Speakers ({len(speakers)}):**")
        for i, speaker in enumerate(speakers, 1):
            st.caption(f"{i}. {speaker.get('name', 'Unknown')} - {speaker.get('voice_id', 'N/A')}")

def render_episode_profiles_section():
    """Render episode profiles in the main area"""
    st.subheader("📺 Episode Profiles")
    
    # Fetch data
    episode_profiles = asyncio.run(fetch_episode_profiles())
    speaker_profiles = asyncio.run(fetch_speaker_profiles())
    
    # Create new episode profile section
    with st.expander("➕ Create New Episode Profile", expanded=False):
        # AI Model Configuration outside form for reactivity
        st.subheader("🤖 AI Model Configuration")
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            outline_provider = st.selectbox("Outline Provider*", list(transcript_provider_models.keys()), key="new_outline_provider")
            outline_model = st.selectbox("Outline Model*", transcript_provider_models[outline_provider], key="new_outline_model")
        
        with col_ai2:
            transcript_provider = st.selectbox("Transcript Provider*", list(transcript_provider_models.keys()), key="new_transcript_provider")
            transcript_model = st.selectbox("Transcript Model*", transcript_provider_models[transcript_provider], key="new_transcript_model")
        
        with st.form("create_episode_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                ep_name = st.text_input("Profile Name*", placeholder="e.g., tech_discussion")
                ep_description = st.text_area("Description", placeholder="Brief description of this profile")
                ep_segments = st.number_input("Number of Segments", min_value=3, max_value=20, value=5)
            
            with col2:
                # Speaker config dropdown
                speaker_names = [sp["name"] for sp in speaker_profiles] if speaker_profiles else []
                
                if speaker_names:
                    ep_speaker_config = st.selectbox("Speaker Configuration*", speaker_names)
                else:
                    st.warning("No speaker profiles available. Create a speaker profile first.")
                    ep_speaker_config = None
            
            # Default briefing
            ep_briefing = st.text_area(
                "Default Briefing*",
                placeholder="Enter the default briefing template for this episode type...",
                height=150
            )
            
            submitted = st.form_submit_button("Create Episode Profile")
            
            if submitted:
                if ep_name and ep_speaker_config and ep_briefing:
                    success = asyncio.run(create_episode_profile({
                        "name": ep_name,
                        "description": ep_description,
                        "speaker_config": ep_speaker_config,
                        "outline_provider": outline_provider,
                        "outline_model": outline_model,
                        "transcript_provider": transcript_provider,
                        "transcript_model": transcript_model,
                        "default_briefing": ep_briefing,
                        "num_segments": ep_segments
                    }))
                    if success:
                        st.success("Episode profile created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create episode profile")
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Display existing episode profiles
    if episode_profiles:
        st.write(f"**{len(episode_profiles)} Episode Profile(s):**")
        
        for profile in episode_profiles:
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.subheader(profile.get('name', 'Unknown'))
                    st.write(f"**Description:** {profile.get('description', 'N/A')}")
                    st.write(f"**Segments:** {profile.get('num_segments', 'N/A')}")
                    st.write(f"**Outline Model:** {profile.get('outline_provider', 'N/A')}/{profile.get('outline_model', 'N/A')}")
                    st.write(f"**Transcript Model:** {profile.get('transcript_provider', 'N/A')}/{profile.get('transcript_model', 'N/A')}")
                    
                    # Inline speaker information
                    st.divider()
                    render_speaker_info_inline(profile.get('speaker_config'), speaker_profiles)
                
                with col_actions:
                    if st.button("⚙️ Configure Speaker", key=f"config_speaker_{profile['id']}", help="Configure speaker profile"):
                        st.info("Speaker configuration coming in Phase 5")
                    
                    if st.button("✏️ Edit", key=f"edit_ep_{profile['id']}"):
                        st.session_state[f"edit_episode_{profile['id']}"] = True
                        st.rerun()
                    
                    if st.button("📋 Duplicate", key=f"dup_ep_{profile['id']}"):
                        success = asyncio.run(duplicate_episode_profile(profile['id']))
                        if success:
                            st.success("Profile duplicated!")
                            st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"del_ep_{profile['id']}"):
                        confirm_delete_episode_profile(profile['id'], profile['name'])
                
                # Show briefing
                st.text_area(
                    "Default Briefing:",
                    value=profile.get('default_briefing', ''),
                    height=100,
                    disabled=True,
                    key=f"briefing_display_{profile['id']}"
                )
                
                # Edit form (if in edit mode)
                if st.session_state.get(f"edit_episode_{profile['id']}", False):
                    st.subheader("✏️ Edit Episode Profile")
                    
                    # AI models outside form for reactivity
                    col5, col6 = st.columns(2)
                    with col5:
                        current_outline_provider = profile.get('outline_provider', list(transcript_provider_models.keys())[0])
                        outline_idx = list(transcript_provider_models.keys()).index(current_outline_provider) if current_outline_provider in transcript_provider_models else 0
                        edit_outline_provider = st.selectbox("Outline Provider", list(transcript_provider_models.keys()), index=outline_idx, key=f"edit_outline_provider_{profile['id']}")
                        
                        current_outline_model = profile.get('outline_model', '')
                        outline_model_idx = 0
                        if current_outline_model in transcript_provider_models[edit_outline_provider]:
                            outline_model_idx = transcript_provider_models[edit_outline_provider].index(current_outline_model)
                        edit_outline_model = st.selectbox("Outline Model", transcript_provider_models[edit_outline_provider], index=outline_model_idx, key=f"edit_outline_model_{profile['id']}")
                    
                    with col6:
                        current_transcript_provider = profile.get('transcript_provider', list(transcript_provider_models.keys())[0])
                        transcript_idx = list(transcript_provider_models.keys()).index(current_transcript_provider) if current_transcript_provider in transcript_provider_models else 0
                        edit_transcript_provider = st.selectbox("Transcript Provider", list(transcript_provider_models.keys()), index=transcript_idx, key=f"edit_transcript_provider_{profile['id']}")
                        
                        current_transcript_model = profile.get('transcript_model', '')
                        transcript_model_idx = 0
                        if current_transcript_model in transcript_provider_models[edit_transcript_provider]:
                            transcript_model_idx = transcript_provider_models[edit_transcript_provider].index(current_transcript_model)
                        edit_transcript_model = st.selectbox("Transcript Model", transcript_provider_models[edit_transcript_provider], index=transcript_model_idx, key=f"edit_transcript_model_{profile['id']}")
                    
                    with st.form(f"edit_episode_form_{profile['id']}"):
                        # Form fields with current values
                        edit_name = st.text_input("Profile Name", value=profile.get('name', ''))
                        edit_description = st.text_area("Description", value=profile.get('description', ''))
                        edit_segments = st.number_input("Segments", min_value=3, max_value=20, value=profile.get('num_segments', 5))
                        
                        # Speaker config
                        speaker_names = [sp["name"] for sp in speaker_profiles] if speaker_profiles else []
                        current_speaker = profile.get('speaker_config', '')
                        speaker_idx = speaker_names.index(current_speaker) if current_speaker in speaker_names else 0
                        edit_speaker_config = st.selectbox("Speaker Configuration", speaker_names, index=speaker_idx)
                        
                        edit_briefing = st.text_area("Default Briefing", value=profile.get('default_briefing', ''), height=150)
                        
                        col7, col8 = st.columns(2)
                        with col7:
                            if st.form_submit_button("💾 Save Changes"):
                                success = asyncio.run(update_episode_profile(profile['id'], {
                                    "name": edit_name,
                                    "description": edit_description,
                                    "speaker_config": edit_speaker_config,
                                    "outline_provider": edit_outline_provider,
                                    "outline_model": edit_outline_model,
                                    "transcript_provider": edit_transcript_provider,
                                    "transcript_model": edit_transcript_model,
                                    "default_briefing": edit_briefing,
                                    "num_segments": edit_segments
                                }))
                                if success:
                                    st.success("Profile updated!")
                                    st.session_state[f"edit_episode_{profile['id']}"] = False
                                    st.rerun()
                        
                        with col8:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_episode_{profile['id']}"] = False
                                st.rerun()
    else:
        st.info("No episode profiles found. Create your first episode profile above.")

def render_speaker_profiles_sidebar():
    """Render speaker profiles in the sidebar with usage indicators"""
    st.subheader("🎤 Speaker Profiles")
    
    # New Speaker Profile button
    if st.button("➕ New Speaker Profile", use_container_width=True):
        speaker_configuration_dialog("create")
    
    # Fetch speaker profiles and episode profiles for usage analysis
    speaker_profiles = asyncio.run(fetch_speaker_profiles())
    episode_profiles = asyncio.run(fetch_episode_profiles())
    
    if not speaker_profiles:
        st.info("No speaker profiles found. Create your first speaker profile above.")
        return
    
    # Analyze usage
    usage_map = analyze_speaker_usage(speaker_profiles, episode_profiles)
    
    st.write(f"**{len(speaker_profiles)} Speaker Profile(s):**")
    
    for profile in speaker_profiles:
        profile_name = profile.get('name', 'Unknown')
        usage_count = usage_map.get(profile_name, 0)
        
        # Usage indicator
        if usage_count > 0:
            usage_indicator = f"✅ Used ({usage_count})"
        else:
            usage_indicator = "⭕ Unused"
        
        with st.expander(f"🎤 {profile_name} {usage_indicator}", expanded=False):
            # Speaker profile summary
            st.write(f"**Description:** {profile.get('description', 'N/A')}")
            st.write(f"**TTS:** {profile.get('tts_provider', 'N/A')}/{profile.get('tts_model', 'N/A')}")
            
            speakers = profile.get('speakers', [])
            st.write(f"**Speakers:** {len(speakers)}")
            for i, speaker in enumerate(speakers[:2], 1):  # Show first 2 speakers only
                st.caption(f"{i}. {speaker.get('name', 'Unknown')} ({speaker.get('voice_id', 'N/A')})")
            if len(speakers) > 2:
                st.caption(f"... and {len(speakers) - 2} more")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✏️", key=f"edit_sp_sidebar_{profile['id']}", help="Edit"):
                    speaker_configuration_dialog("edit", profile['id'])
            with col2:
                if st.button("📋", key=f"dup_sp_sidebar_{profile['id']}", help="Duplicate"):
                    success = asyncio.run(duplicate_speaker_profile(profile['id']))
                    if success:
                        st.success("Profile duplicated!")
                        st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_sp_sidebar_{profile['id']}", help="Delete"):
                    confirm_delete_speaker_profile(profile['id'], profile['name'])

# Main page title
st.title("🎙️ Podcast Generator")
st.markdown("Manage your podcast episodes and configurations")

# Create tabs
episodes_tab, templates_tab = st.tabs(["Episodes", "Templates"])

with episodes_tab:
    st.header("📻 Episodes")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh", help="Refresh episode status"):
            st.rerun()
    
    # Fetch and display episodes
    episodes = asyncio.run(fetch_episodes())
    
    if not episodes:
        st.info("No episodes found. Generate your first episode in the chat interface!")
    else:
        st.write(f"Found {len(episodes)} episode(s)")
        
        # Group episodes by status
        status_groups = {
            "running": [],
            "completed": [], 
            "failed": [],
            "pending": []
        }
        
        for episode in episodes:
            status = episode.get("job_status", "unknown")
            if status in ["running", "processing"]:
                status_groups["running"].append(episode)
            elif status == "completed":
                status_groups["completed"].append(episode)
            elif status in ["failed", "error"]:
                status_groups["failed"].append(episode)
            else:
                status_groups["pending"].append(episode)
        
        # Display running episodes first
        if status_groups["running"]:
            st.subheader("🔄 Currently Processing")
            for episode in status_groups["running"]:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{episode['name']}**")
                        st.caption(f"Profile: {episode['episode_profile'].get('name', 'Unknown')}")
                    
                    with col2:
                        if episode.get("created"):
                            st.caption(f"Started: {format_relative_time(episode['created'])}")
                    
                    with col3:
                        st.markdown(f"{get_status_emoji(episode.get('job_status', 'unknown'))} Processing...")
        
        # Display completed episodes
        if status_groups["completed"]:
            st.subheader("✅ Completed Episodes")
            for episode in status_groups["completed"]:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{episode['name']}**")
                        st.caption(f"Profile: {episode['episode_profile'].get('name', 'Unknown')}")
                        if episode.get("created"):
                            st.caption(f"Created: {format_relative_time(episode['created'])}")
                    
                    with col2:
                        st.markdown(f"{get_status_emoji('completed')} Complete")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_episode_{episode['id']}", help="Delete episode and audio file"):
                            confirm_delete_episode(episode['id'], episode['name'])
                
                # Audio player
                if episode.get("audio_file"):
                    try:
                        st.audio(episode["audio_file"], format="audio/mpeg")
                    except Exception as e:
                        st.error(f"Could not load audio: {str(e)}")
                
                # Episode details in separate expanders
                with st.expander(f"🎭 Profiles - {episode['name']}", expanded=False):
                    if episode.get("briefing"):
                        st.text_area(
                            "Briefing Used:",
                            value=episode["briefing"],
                            height=100,
                            disabled=True,
                            key=f"briefing_{episode['id']}"
                        )
                    
                    # Show episode profile info
                    if episode.get("episode_profile"):
                        st.subheader("📺 Episode Profile")
                        ep_profile = episode["episode_profile"]
                        st.write(f"**Name:** {ep_profile.get('name', 'Unknown')}")
                        st.write(f"**Description:** {ep_profile.get('description', 'N/A')}")
                        st.write(f"**Segments:** {ep_profile.get('num_segments', 'N/A')}")
                        st.write(f"**Outline Model:** {ep_profile.get('outline_provider', 'N/A')}/{ep_profile.get('outline_model', 'N/A')}")
                        st.write(f"**Transcript Model:** {ep_profile.get('transcript_provider', 'N/A')}/{ep_profile.get('transcript_model', 'N/A')}")
                    
                    # Show speaker configuration
                    if episode.get("speaker_profile"):
                        st.subheader("🎤 Speaker Profile")
                        sp_profile = episode["speaker_profile"]
                        st.write(f"**Name:** {sp_profile.get('name', 'Unknown')}")
                        st.write(f"**Description:** {sp_profile.get('description', 'N/A')}")
                        st.write(f"**TTS Provider:** {sp_profile.get('tts_provider', 'N/A')}/{sp_profile.get('tts_model', 'N/A')}")
                        
                        speakers = sp_profile.get("speakers", [])
                        st.write(f"**Speakers ({len(speakers)}):**")
                        for i, speaker in enumerate(speakers, 1):
                            st.markdown(f"**{i}. {speaker.get('name', 'Unknown')}**")
                            st.write(f"   - Voice: {speaker.get('voice_id', 'Unknown')}")
                            st.write(f"   - Personality: {speaker.get('personality', 'N/A')}")
                            if speaker.get('backstory'):
                                st.write(f"   - Background: {speaker['backstory']}")
                    
                    # Show transcript if available
                    if episode.get("transcript"):
                        with st.expander(f"📄 Transcript - {episode['name']}", expanded=False):
                            transcript_data = episode["transcript"]
                            if isinstance(transcript_data, dict) and "transcript" in transcript_data:
                                st.json(transcript_data["transcript"])
                            else:
                                st.json(transcript_data)
                    
                    # Show outline if available
                    if episode.get("outline"):
                        with st.expander(f"📋 Outline - {episode['name']}", expanded=False):
                            st.json(episode["outline"])
        
        # Display failed episodes
        if status_groups["failed"]:
            st.subheader("❌ Failed Episodes")
            for episode in status_groups["failed"]:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{episode['name']}**")
                        st.caption(f"Profile: {episode['episode_profile'].get('name', 'Unknown')}")
                        if episode.get("created"):
                            st.caption(f"Created: {format_relative_time(episode['created'])}")
                    
                    with col2:
                        st.markdown(f"{get_status_emoji('failed')} Failed")
                    
                    # Show error information
                    st.error("Episode generation failed. Check the logs for more details.")
        
        # Display pending episodes
        if status_groups["pending"]:
            st.subheader("⏳ Pending Episodes")
            for episode in status_groups["pending"]:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{episode['name']}**")
                        st.caption(f"Profile: {episode['episode_profile'].get('name', 'Unknown')}")
                        if episode.get("created"):
                            st.caption(f"Created: {format_relative_time(episode['created'])}")
                    
                    with col2:
                        st.markdown(f"{get_status_emoji('pending')} Pending")

# Get available providers and models using API service

# Load available models
text_to_speech_models = models_service.get_all_models(model_type="text_to_speech")
text_models = models_service.get_all_models(model_type="language")

# Build provider-model mappings
tts_provider_models = {}
for model in text_to_speech_models:
    if model.provider not in tts_provider_models:
        tts_provider_models[model.provider] = []
    tts_provider_models[model.provider].append(model.name)

transcript_provider_models = {}
for model in text_models:
    if model.provider not in transcript_provider_models:
        transcript_provider_models[model.provider] = []
    transcript_provider_models[model.provider].append(model.name)

# Check if we have required models
if len(text_to_speech_models) == 0:
    st.error("No text-to-speech models found. Please set one up in the Models page.")
    st.stop()

if len(text_models) == 0:
    st.error("No language models found. Please set one up in the Models page.")
    st.stop()

with templates_tab:
    # Header section with explanatory content
    st.header("📺 Episode Templates")
    
    # Explanatory header about relationships and workflow
    st.markdown("""
    #### Understanding Episode Profiles and Speaker Profiles
    
    **Episode profiles** define the format and AI models for podcast generation, including:
    - Number of segments, outline and transcript AI models
    - Default briefing templates
    
    **Speaker profiles** define the voices and personalities that will be used, including:
    - TTS provider and model settings
    - Individual speaker configurations (name, voice ID, personality, backstory)
    
    **Important**: Episode profiles reference speaker profiles by name. You can either:
    1. **Recommended workflow**: Create speaker profiles first, then create episode profiles that use them
    2. **Alternative**: Create episode profiles and add speaker profiles on-demand via configuration dialogs (coming in later phases)
    """)
    
    st.divider()
    
    # Main layout: Episode profiles (main area) + Speaker profiles (sidebar)
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_main:
        render_episode_profiles_section()
    
    with col_sidebar:
        render_speaker_profiles_sidebar()

# Temporary placeholder for the old episode profiles tab content (will be moved to Templates tab in Phase 3)
# This content will be removed once migration is complete
if False:  # Disable this section for now
    st.subheader("📺 Episode Profiles")
    
    # Fetch episode profiles
    episode_profiles = asyncio.run(fetch_episode_profiles())
    
    # Create new episode profile
    with st.expander("➕ Create New Episode Profile", expanded=False):
        # AI Model Configuration outside form for reactivity
        st.subheader("🤖 AI Model Configuration")
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            outline_provider = st.selectbox("Outline Provider*", list(transcript_provider_models.keys()), key="new_outline_provider")
            outline_model = st.selectbox("Outline Model*", transcript_provider_models[outline_provider], key="new_outline_model")
        
        with col_ai2:
            transcript_provider = st.selectbox("Transcript Provider*", list(transcript_provider_models.keys()), key="new_transcript_provider")
            transcript_model = st.selectbox("Transcript Model*", transcript_provider_models[transcript_provider], key="new_transcript_model")
        
        with st.form("create_episode_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                ep_name = st.text_input("Profile Name*", placeholder="e.g., tech_discussion")
                ep_description = st.text_area("Description", placeholder="Brief description of this profile")
                ep_segments = st.number_input("Number of Segments", min_value=3, max_value=20, value=5)
            
            with col2:
                # Speaker config dropdown (will be populated with available speaker profiles)
                available_speaker_profiles = asyncio.run(fetch_speaker_profiles())
                speaker_names = [sp["name"] for sp in available_speaker_profiles] if available_speaker_profiles else []
                
                if speaker_names:
                    ep_speaker_config = st.selectbox("Speaker Configuration*", speaker_names)
                else:
                    st.warning("No speaker profiles available. Create a speaker profile first.")
                    ep_speaker_config = None
            
            # Default briefing
            ep_briefing = st.text_area(
                "Default Briefing*",
                placeholder="Enter the default briefing template for this episode type...",
                height=150
            )
            
            submitted = st.form_submit_button("Create Episode Profile")
            
            if submitted:
                if ep_name and ep_speaker_config and ep_briefing:
                    success = asyncio.run(create_episode_profile({
                        "name": ep_name,
                        "description": ep_description,
                        "speaker_config": ep_speaker_config,
                        "outline_provider": outline_provider,
                        "outline_model": outline_model,
                        "transcript_provider": transcript_provider,
                        "transcript_model": transcript_model,
                        "default_briefing": ep_briefing,
                        "num_segments": ep_segments
                    }))
                    if success:
                        st.success("Episode profile created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create episode profile")
                else:
                    st.error("Please fill in all required fields (*)")
    
    # Display existing episode profiles
    if episode_profiles:
        st.write(f"**{len(episode_profiles)} Episode Profile(s):**")
        
        for profile in episode_profiles:
            with st.expander(f"📺 {profile['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {profile.get('description', 'N/A')}")
                    st.write(f"**Speaker Config:** {profile.get('speaker_config', 'N/A')}")
                    st.write(f"**Segments:** {profile.get('num_segments', 'N/A')}")
                    st.write(f"**Outline Model:** {profile.get('outline_provider', 'N/A')}/{profile.get('outline_model', 'N/A')}")
                    st.write(f"**Transcript Model:** {profile.get('transcript_provider', 'N/A')}/{profile.get('transcript_model', 'N/A')}")
                
                with col2:
                    if st.button("📝 Edit", key=f"edit_ep_{profile['id']}"):
                        st.session_state[f"edit_episode_{profile['id']}"] = True
                        st.rerun()
                    
                    if st.button("📋 Duplicate", key=f"dup_ep_{profile['id']}"):
                        success = asyncio.run(duplicate_episode_profile(profile['id']))
                        if success:
                            st.success("Profile duplicated!")
                            st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"del_ep_{profile['id']}"):
                        confirm_delete_episode_profile(profile['id'], profile['name'])
                
                # Show briefing
                st.text_area(
                    "Default Briefing:",
                    value=profile.get('default_briefing', ''),
                    height=100,
                    disabled=True,
                    key=f"briefing_display_{profile['id']}"
                )
                
                # Edit form (if in edit mode)
                if st.session_state.get(f"edit_episode_{profile['id']}", False):
                    st.subheader("✏️ Edit Episode Profile")
                    
                    # AI models outside form for reactivity
                    col5, col6 = st.columns(2)
                    with col5:
                        current_outline_provider = profile.get('outline_provider', list(transcript_provider_models.keys())[0])
                        outline_idx = list(transcript_provider_models.keys()).index(current_outline_provider) if current_outline_provider in transcript_provider_models else 0
                        edit_outline_provider = st.selectbox("Outline Provider", list(transcript_provider_models.keys()), index=outline_idx, key=f"edit_outline_provider_{profile['id']}")
                        
                        current_outline_model = profile.get('outline_model', '')
                        outline_model_idx = 0
                        if current_outline_model in transcript_provider_models[edit_outline_provider]:
                            outline_model_idx = transcript_provider_models[edit_outline_provider].index(current_outline_model)
                        edit_outline_model = st.selectbox("Outline Model", transcript_provider_models[edit_outline_provider], index=outline_model_idx, key=f"edit_outline_model_{profile['id']}")
                    
                    with col6:
                        current_transcript_provider = profile.get('transcript_provider', list(transcript_provider_models.keys())[0])
                        transcript_idx = list(transcript_provider_models.keys()).index(current_transcript_provider) if current_transcript_provider in transcript_provider_models else 0
                        edit_transcript_provider = st.selectbox("Transcript Provider", list(transcript_provider_models.keys()), index=transcript_idx, key=f"edit_transcript_provider_{profile['id']}")
                        
                        current_transcript_model = profile.get('transcript_model', '')
                        transcript_model_idx = 0
                        if current_transcript_model in transcript_provider_models[edit_transcript_provider]:
                            transcript_model_idx = transcript_provider_models[edit_transcript_provider].index(current_transcript_model)
                        edit_transcript_model = st.selectbox("Transcript Model", transcript_provider_models[edit_transcript_provider], index=transcript_model_idx, key=f"edit_transcript_model_{profile['id']}")
                    
                    with st.form(f"edit_episode_form_{profile['id']}"):
                        # Form fields with current values
                        edit_name = st.text_input("Profile Name", value=profile.get('name', ''))
                        edit_description = st.text_area("Description", value=profile.get('description', ''))
                        edit_segments = st.number_input("Segments", min_value=3, max_value=20, value=profile.get('num_segments', 5))
                        
                        # Speaker config
                        current_speaker = profile.get('speaker_config', '')
                        speaker_idx = speaker_names.index(current_speaker) if current_speaker in speaker_names else 0
                        edit_speaker_config = st.selectbox("Speaker Configuration", speaker_names, index=speaker_idx)
                        
                        edit_briefing = st.text_area("Default Briefing", value=profile.get('default_briefing', ''), height=150)
                        
                        col7, col8 = st.columns(2)
                        with col7:
                            if st.form_submit_button("💾 Save Changes"):
                                success = asyncio.run(update_episode_profile(profile['id'], {
                                    "name": edit_name,
                                    "description": edit_description,
                                    "speaker_config": edit_speaker_config,
                                    "outline_provider": edit_outline_provider,
                                    "outline_model": edit_outline_model,
                                    "transcript_provider": edit_transcript_provider,
                                    "transcript_model": edit_transcript_model,
                                    "default_briefing": edit_briefing,
                                    "num_segments": edit_segments
                                }))
                                if success:
                                    st.success("Profile updated!")
                                    st.session_state[f"edit_episode_{profile['id']}"] = False
                                    st.rerun()
                        
                        with col8:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_episode_{profile['id']}"] = False
                                st.rerun()
    else:
        st.info("No episode profiles found. Create your first episode profile above.")