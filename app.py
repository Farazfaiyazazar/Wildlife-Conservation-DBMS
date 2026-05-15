import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONNECTION & STYLING ---
URL = "https://unmvdngsvdbaxujfvyaz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVubXZkbmdzdmRiYXh1amZ2eWF6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzMzkzMzMsImV4cCI6MjA5MTkxNTMzM30.5YX7LpwdNBXD5RMlybOopWZIM2ZfshteIa_Pg8jK-lk"
db = create_client(URL, KEY)

st.set_page_config(page_title="Wildlife Registry Pro", page_icon="🌿", layout="wide")

st.markdown("""<style>
    .main { background-color: #f0f2f6; }
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 10px; padding: 15px; border-bottom: 4px solid #2e7d32; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; }
    </style>""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. LOGIN INTERFACE ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.2, 1])
    with cols[1]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://ciu.edu.tr/themes/custom/ciu/logo.svg", width=300)
        st.title("🐾 Wildlife Registry Login")
        with st.container(border=True):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            if st.button("Access Database", use_container_width=True, type="primary"):
                res = db.table("users").select("*").eq("username", user_input).eq("password", pass_input).execute()
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = res.data[0]
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

# --- 4. MAIN APPLICATION (THE PROTECTED AREA) ---
else:
    user_role = st.session_state.user_data.get('role_id')
    username = st.session_state.user_data.get('username')

    # --- SIDEBAR LOGIC (Updated for 5 screens) ---
    with st.sidebar:
        st.image("https://ciu.edu.tr/themes/custom/ciu/logo.svg", width=160)
        st.markdown("## CIU DBMS PROJECT")
        
        if user_role == 1: # Director
            options = ["📊 Dashboard", "📝 Field Observations", "🌍 Habitat Registry", "🦁 Species Manager", "🛡️ Equipment Logs"]
        elif user_role == 2: # Analyst
            options = ["📊 Dashboard", "📝 Field Observations", "🌍 Habitat Registry"]
        else: # Ranger (Role 3)
            options = ["📝 Field Observations", "🌍 Habitat Registry", "🛡️ Equipment Logs"]
            
        page = st.radio("Navigation Menu", options)
        
        st.divider()
        st.write(f"Logged in as: :green[**{username}**]")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- PAGE ROUTING ---
    if page == "📊 Dashboard":
        st.title("📊 Wildlife Analytics")
        species_data = db.table("species").select("*").execute().data
        obs_data = db.table("observations").select("*").execute().data
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Cataloged Species", len(species_data))
        m2.metric("Total Observations", len(obs_data))
        total_pop = sum((s.get('population') or 0) for s in species_data)
        m3.metric("Global Population Est.", f"{total_pop:,}")
        m4.metric("Cloud Status", "Synchronized")

        if species_data:
            df = pd.DataFrame(species_data)
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.subheader("Population Distribution")
                chart_df = df.dropna(subset=['population']).sort_values(by="population", ascending=False)
                st.bar_chart(chart_df.set_index("common_name")["population"], color="#2e7d32")
            with c_right:
                st.subheader("Threat Levels")
                st.dataframe(df[['common_name', 'conservation_status']], use_container_width=True, hide_index=True)

    elif page == "📝 Field Observations":
        st.title("📝 Data Entry Portal")
        species_list = db.table("species").select("species_id, common_name").execute().data
        habitat_list = db.table("habitats").select("habitat_id, area_name").execute().data
        s_map = {s['common_name']: s['species_id'] for s in species_list}
        h_map = {h['area_name']: h['habitat_id'] for h in habitat_list}

        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                sel_s = st.selectbox("Select Species", options=list(s_map.keys()))
                sel_h = st.selectbox("Select Habitat", options=list(h_map.keys()))
            with c2:
                count = st.number_input("Count Sighted", min_value=1)
                date_obs = st.date_input("Observation Date")
            
            if st.button("Submit to Registry", type="primary", use_container_width=True):
                db.table("observations").insert({
                    "species_id": s_map[sel_s], "habitat_id": h_map[sel_h],
                    "population_count": count, "observer_id": st.session_state.user_data['user_id']
                }).execute()
                st.success("Sighting recorded successfully!")

    elif page == "🌍 Habitat Registry":
        st.title("🌍 Global Habitat Registry")
        h_res = db.table("habitats").select("*").execute().data
        if h_res:
            st.dataframe(pd.DataFrame(h_res)[["area_name", "location_coords", "climate_type"]], use_container_width=True, hide_index=True)

    elif page == "🦁 Species Manager":
        st.title("🦁 Wildlife Species Manager")
        
        # INSERT SPECIES
        with st.expander("➕ Add New Species"):
            with st.form("add_species"):
                c_name = st.text_input("Common Name")
                s_name = st.text_input("Scientific Name")
                pop = st.number_input("Initial Population", min_value=0)
                status = st.selectbox("Status", ["Least Concern", "Vulnerable", "Endangered", "Critically Endangered"])
                if st.form_submit_button("Add to Database"):
                    db.table("species").insert({"common_name": c_name, "scientific_name": s_name, "population": pop, "conservation_status": status}).execute()
                    st.success("Added!")
                    st.rerun()

        # DELETE SPECIES
        st.subheader("Manage Species")
        species_data = db.table("species").select("*").execute().data
        if species_data:
            df_s = pd.DataFrame(species_data)
            st.dataframe(df_s, use_container_width=True)
            sel_to_del = st.selectbox("Select Species to Delete", [s['common_name'] for s in species_data])
            if st.button("🗑️ Delete"):
                db.table("species").delete().eq("common_name", sel_to_del).execute()
                st.warning("Deleted!")
                st.rerun()

    elif page == "🛡️ Equipment Logs":
        st.title("🛡️ Equipment Tracker")
        e_data = db.table("equipment").select("*").execute().data
        if e_data:
            st.dataframe(pd.DataFrame(e_data), use_container_width=True)
            
            # UPDATE EQUIPMENT
            st.subheader("Update Gear Status")
            e_id = st.number_input("Equipment ID", min_value=1)
            new_stat = st.selectbox("Status", ["Operational", "Broken", "Maintenance"])
            if st.button("Update Status"):
                db.table("equipment").update({"status": new_stat}).eq("equip_id", e_id).execute()
                st.success("Updated!")
                st.rerun()