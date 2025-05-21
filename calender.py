
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import json

st.set_page_config(page_title="SRG Monthly Calendar", layout="wide")

if "events" not in st.session_state:
    st.session_state.events = []  # All shifts
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# Sidebar login
st.sidebar.title("SRG Roster Login")
role = st.sidebar.radio("Login as", ["Student", "Admin"])

if role == "Student":
    sid = st.sidebar.text_input("Student ID")
    name = st.sidebar.text_input("Full Name")
    if st.sidebar.button("Login / Register"):
        if sid and name:
            st.session_state.current_user = {"id": sid, "name": name}
            st.success(f"Logged in as {name}")

elif role == "Admin":
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login as Admin"):
        if user == "demo" and pwd == "demo":
            st.session_state.admin_mode = True
            st.success("Admin logged in")

# ---- Student View ----
if "current_user" in st.session_state:
    user = st.session_state.current_user
    st.title(f"📆 {user['name']}'s Shift Calendar")

    with st.form("new_shift_form"):
        st.subheader("Add Availability")
        date = st.date_input("Select date")
        start = st.time_input("Start time")
        end = st.time_input("End time")
        submitted = st.form_submit_button("Add Shift")
        if submitted:
            st.session_state.events.append({
                "title": f"{user['name']} (Pending)",
                "start": f"{date}T{start}",
                "end": f"{date}T{end}",
                "student_id": user["id"],
                "status": "Pending"
            })
            st.success("Shift added!")

    st.subheader("Your Calendar")
    calendar_events = [e for e in st.session_state.events if e["student_id"] == user["id"]]
    calendar(options={"initialView": "dayGridMonth"}, events=calendar_events)

# ---- Admin View ----
elif st.session_state.admin_mode:
    st.title("🧑‍🏫 Admin - Monthly Shift Calendar")

    calendar(options={"initialView": "dayGridMonth"}, events=st.session_state.events)

    st.subheader("Review Pending Shifts")
    for i, e in enumerate(st.session_state.events):
        if e["title"].endswith("(Pending)"):
            st.markdown(f"**{e['title']}** | {e['start']} to {e['end']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm", key=f"approve_{i}"):
                    st.session_state.events[i]["title"] = e["title"].replace(" (Pending)", " (Confirmed)")
                    st.session_state.events[i]["status"] = "Confirmed"
            with col2:
                if st.button("❌ Remove", key=f"remove_{i}"):
                    st.session_state.events.pop(i)
                    st.experimental_rerun()

    # Summary Table
    st.subheader("📊 Weekly Summary")
    df = pd.DataFrame(st.session_state.events)
    if not df.empty:
        df["Hours"] = pd.to_datetime(df["end"]) - pd.to_datetime(df["start"])
        df = df[df["status"] == "Confirmed"]
        df["Hours"] = df["Hours"].dt.total_seconds() / 3600
        summary = df.groupby("student_id")[["Hours"]].sum().reset_index()
        st.table(summary)
    else:
        st.info("No confirmed shifts yet.")
