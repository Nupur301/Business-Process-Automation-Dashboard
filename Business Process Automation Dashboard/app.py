import streamlit as st
import pandas as pd

st.set_page_config(page_title="Automation Dashboard", layout="wide")

st.title("📊 Business Process Automation Dashboard")

# -----------------------------
# INPUT
# -----------------------------
st.sidebar.header("⚙️ Controls")
option = st.sidebar.radio("Input Method", ["Manual Entry", "Upload CSV"])

tasks = []

st.subheader("📥 Task Input")

if option == "Manual Entry":
    user_input = st.text_area("Enter tasks (one per line)")
    if user_input:
        tasks = [t.strip() for t in user_input.split("\n") if t.strip()]

elif option == "Upload CSV":
    file = st.file_uploader("Upload CSV")
    if file:
        df_input = pd.read_csv(file)
        tasks = df_input.iloc[:, 0].astype(str).tolist()

# -----------------------------
# FUNCTIONS
# -----------------------------
def categorize_task(task):
    task = task.lower()
    if any(x in task for x in ["invoice", "payment"]):
        return "Finance"
    elif any(x in task for x in ["server", "bug", "error"]):
        return "IT"
    elif any(x in task for x in ["email", "meeting"]):
        return "Communication"
    return "Operations"


def get_priority(task):
    task = task.lower()

    if any(x in task for x in ["urgent", "critical", "asap"]):
        return "🔴 High"

    if "crash" in task:
        return "🔴 High"

    if "bug" in task or "error" in task:
        return "🟡 Medium"

    if "follow-up" in task:
        return "🟡 Medium"

    return "🟢 Low"


# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "df" not in st.session_state:
    st.session_state.df = None

# Create dataframe
if tasks:
    st.session_state.df = pd.DataFrame([{
        "Task": t,
        "Category": categorize_task(t),
        "Priority": get_priority(t),
        "Status": "Pending",
        "Done": False
    } for t in tasks])

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
if st.session_state.df is not None:

    # IMPORTANT: do NOT use .copy()
    df = st.session_state.df

    st.subheader("📋 Task Manager")

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key="editor"
    )

    # -----------------------------
    # FIX: STATUS UPDATE FROM CHECKBOX
    # -----------------------------
    edited_df["Status"] = edited_df["Done"].map(
        {True: "Completed", False: "Pending"}
    )

    # SAVE BACK (IMPORTANT)
    st.session_state.df = edited_df

    # -----------------------------
    # SORT COMPLETED LAST
    # -----------------------------
    st.session_state.df["order"] = st.session_state.df["Status"].apply(
        lambda x: 0 if x == "Pending" else 1
    )

    st.session_state.df = st.session_state.df.sort_values(by="order")

    df = st.session_state.df

    # -----------------------------
    # METRICS
    # -----------------------------
    st.subheader("📈 Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tasks", len(df))
    col2.metric("High Priority", len(df[df["Priority"].str.contains("High")]))
    col3.metric("Completed", len(df[df["Status"] == "Completed"]))

    st.divider()

    # -----------------------------
    # SMART SUGGESTION
    # -----------------------------
    pending = df[df["Status"] == "Pending"]

    if not pending.empty:
        high = pending[pending["Priority"].str.contains("High")]

        if not high.empty:
            st.warning(f"🔥 Focus: {high.iloc[0]['Task']}")
        else:
            st.info(f"👉 Next: {pending.iloc[0]['Task']}")

    # -----------------------------
    # EXPORT
    # -----------------------------
    st.subheader("📥 Export")

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "tasks.csv",
        "text/csv"
    )

else:
    st.info("🚀 Enter tasks to begin")