import streamlit as st
import pandas as pd
import random
import time
import requests


# ================= CONFIG =================

st.set_page_config(
    page_title="AI Risk Dashboard",
    layout="wide"
)


# ================= SECRETS =================

ADMIN_USER = st.secrets["ADMIN_USER"]
ADMIN_PASS = st.secrets["ADMIN_PASS"]

SLACK_TOKEN = st.secrets["SLACK_TOKEN"]
SLACK_CHANNEL = st.secrets["SLACK_CHANNEL"]


# ================= SESSION =================

if "step" not in st.session_state:
    st.session_state.step = 1

if "auth" not in st.session_state:
    st.session_state.auth = False

if "otp" not in st.session_state:
    st.session_state.otp = None

if "otp_time" not in st.session_state:
    st.session_state.otp_time = None


# ================= SLACK =================

def send_otp(otp):

    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "channel": SLACK_CHANNEL,
        "text": f"🔐 OTP: *{otp}* (30s valid)"
    }

    requests.post(url, headers=headers, json=data)



# ================= LOGIN =================

def login():

    st.title("🔐 Secure Login")


    # Step 1
    if st.session_state.step == 1:

        st.subheader("Account Login")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):

            if u == ADMIN_USER and p == ADMIN_PASS:

                st.session_state.step = 2
                st.success("Account verified")
                st.rerun()

            else:
                st.error("Wrong credentials")


    # Step 2
    elif st.session_state.step == 2:

        st.subheader("Slack Token")

        token = st.text_input("Enter Token", type="password")

        if st.button("Verify"):

            if token == SLACK_TOKEN:

                otp = random.randint(100000, 999999)

                st.session_state.otp = str(otp)
                st.session_state.otp_time = time.time()

                send_otp(otp)

                st.session_state.step = 3

                st.success("OTP sent")
                st.rerun()

            else:
                st.error("Invalid token")


    # Step 3
    elif st.session_state.step == 3:

        st.subheader("OTP Verification")

        code = st.text_input("Enter OTP", type="password")

        now = time.time()

        if st.session_state.otp_time:

            remain = 30 - int(now - st.session_state.otp_time)

            if remain > 0:
                st.info(f"Expires in {remain}s")

            else:
                st.error("OTP expired")
                st.session_state.step = 2
                st.rerun()


        if st.button("Confirm"):

            if now - st.session_state.otp_time > 30:

                st.error("OTP expired")
                st.session_state.step = 2
                st.rerun()


            elif code == st.session_state.otp:

                st.session_state.auth = True
                st.session_state.otp = None

                st.success("Access granted")
                st.rerun()


            else:
                st.error("Wrong OTP")



# ================= DASHBOARD =================

def dashboard():

    st.title("🛡 AI Risk Dashboard")
    st.caption("Human-in-the-Loop System")


    if st.button("Logout"):

        st.session_state.step = 1
        st.session_state.auth = False
        st.rerun()


    if "data" not in st.session_state:
        st.session_state.data = []


    def gen():

        return {
            "txn_id": f"TXN{random.randint(1000,9999)}",
            "risk": random.choice(["Low","Medium","High","Critical"]),
            "status": "PENDING",
            "time": time.strftime("%H:%M:%S")
        }


    if st.button("➕ New Case"):
        st.session_state.data.append(gen())


    df = pd.DataFrame(st.session_state.data)


    # KPI
    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total", len(df))

    if not df.empty and "status" in df.columns:

        c2.metric("Pending", len(df[df["status"]=="PENDING"]))
        c3.metric("Approved", len(df[df["status"]=="APPROVED"]))
        c4.metric("Rejected", len(df[df["status"]=="REJECTED"]))

    else:

        c2.metric("Pending",0)
        c3.metric("Approved",0)
        c4.metric("Rejected",0)


    st.divider()


    st.subheader("Cases")

    if not df.empty:

        st.dataframe(df,use_container_width=True)

        selected = st.selectbox("Select TXN", df["txn_id"])

        colA,colB = st.columns(2)

        if colA.button("Approve"):

            df.loc[df["txn_id"]==selected,"status"]="APPROVED"
            st.session_state.data = df.to_dict("records")

        if colB.button("Reject"):

            df.loc[df["txn_id"]==selected,"status"]="REJECTED"
            st.session_state.data = df.to_dict("records")

    else:
        st.info("No data")



# ================= MAIN =================

if not st.session_state.auth:

    login()

else:

    dashboard()
