
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="CITYNEXUS AI | Command Center", page_icon="🏙️", layout="wide")

zones = pd.read_csv("data/city_zones_ml.csv")
complaints = pd.read_csv("data/complaints.csv")

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.hero {padding: 22px 26px; border-radius: 18px; background: linear-gradient(135deg,#172554,#0f172a); color:white; margin-bottom:18px;}
.hero h1 {margin:0; font-size:2.1rem;}
.hero p {margin:5px 0 0 0; opacity:.82;}
.kpi {padding:18px; border:1px solid #e5e7eb; border-radius:16px; background:white; min-height:105px;}
.kpi .label {font-size:.82rem; color:#64748b;}
.kpi .value {font-size:1.65rem; font-weight:700; margin-top:4px;}
.alert {padding:14px 16px; border-radius:14px; background:#fff7ed; border:1px solid #fed7aa;}
.section {font-size:1.05rem; font-weight:700; margin-top:14px; margin-bottom:8px;}
.small {color:#64748b; font-size:.84rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
<h1>🏙️ CITYNEXUS AI</h1>
<p>AI-Powered Smart City Governance & SDG Impact Intelligence · Command Center</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Command Center")
    module = st.radio("Module", [
        "Overview", "Flood Intelligence", "Urban Mobility",
        "Waste Intelligence", "Citizen Services", "Governance Copilot", "SDG Impact"
    ])
    selected = st.selectbox("Focus Zone", zones["zone"])
    demo_mode = st.toggle("3-Minute Demo Mode", True)
    st.divider()
    st.caption("Prototype data is simulated for demonstration.")

z = zones[zones.zone == selected].iloc[0]

def kpi(label, value, note=""):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="small">{note}</div></div>', unsafe_allow_html=True)

# ---------- Overview ----------
if module == "Overview":
    st.markdown('<div class="section">City-wide situation awareness</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    vals = [
        ("High-risk zones", int((zones.risk_level=="HIGH").sum()), "Immediate attention"),
        ("Avg flood risk", f"{zones.flood_risk.mean():.0f}%", "Predictive model"),
        ("Traffic pressure", f"{zones.traffic_score.mean():.0f}%", "Network indicator"),
        ("Waste overflow", f"{zones.predicted_overflow.mean():.0f}%", "Predicted demand"),
        ("P1 complaints", int((complaints.priority=="P1").sum()), "Needs routing"),
    ]
    for c,(a,b,d) in zip(cols,vals):
        with c: kpi(a,b,d)

    st.markdown('<div class="section">Priority alert</div>', unsafe_allow_html=True)
    high = zones.sort_values("flood_risk", ascending=False).iloc[0]
    st.markdown(f'<div class="alert">⚠️ <b>{high.zone} is the current highest-priority zone.</b> Flood probability {high.flood_risk}%, population exposure {high.population_exposure}%. Recommended: deploy nearest emergency team and issue a citizen warning.</div>', unsafe_allow_html=True)

    c1,c2 = st.columns([1.35,1])
    with c1:
        st.markdown("### 🗺️ Urban Risk Map")
        m = folium.Map(location=[zones.lat.mean(), zones.lon.mean()], zoom_start=12, tiles="CartoDB positron")
        for _,r in zones.iterrows():
            color = "red" if r.risk_level=="HIGH" else "orange" if r.risk_level=="MEDIUM" else "green"
            folium.CircleMarker(
                [r.lat,r.lon], radius=11, color=color, fill=True, fill_opacity=.75,
                popup=f"{r.zone}<br>Flood risk: {r.flood_risk}%",
                tooltip=f"{r.zone} · {r.risk_level}"
            ).add_to(m)
        st_folium(m, height=430, width=None)
    with c2:
        st.markdown("### 📊 Risk profile")
        chart = zones.set_index("zone")[["flood_risk","traffic_score","predicted_overflow"]]
        st.bar_chart(chart)
        st.markdown("**Decision loop:** Sense → Understand → Predict → Decide → Act → Measure → Learn")

# ---------- Flood ----------
elif module == "Flood Intelligence":
    st.header("🌊 Predictive Disaster & Flood Management")
    cols=st.columns(4)
    for c,(a,b,d) in zip(cols,[
        ("Flood probability",f"{z.flood_risk}%","AI prediction"),
        ("Risk status",z.risk_level,"Priority level"),
        ("Water level",f"{z.water_level}%","Current indicator"),
        ("Rainfall",f"{z.rainfall_mm} mm","Simulated reading")]):
        with c: kpi(a,b,d)
    st.markdown("### Explainable AI factors")
    factors=pd.DataFrame({
        "Factor":["Rainfall intensity","Water level","Low drainage capacity","Population exposure"],
        "Contribution":[z.rainfall_mm/1.3,z.water_level,100-z.drainage_capacity,z.population_exposure]
    }).set_index("Factor")
    st.bar_chart(factors)
    st.success(f"Recommended action — {z.zone}: Deploy nearest emergency team → divert traffic → issue citizen warning.")

# ---------- Mobility ----------
elif module == "Urban Mobility":
    st.header("🚦 Intelligent Urban Mobility")
    cols=st.columns(4)
    for c,(a,b,d) in zip(cols,[
        ("Predicted congestion",f"{z.traffic_score}%","AI forecast"),
        ("Emergency delay risk","HIGH" if z.traffic_score>70 else "MEDIUM","Operational impact"),
        ("Alternative route","Route B → D","Optimization result"),
        ("Method","Dijkstra / A*","Routing engine")]):
        with c: kpi(a,b,d)
    hours=["08:00","10:00","12:00","14:00","17:00","19:00"]
    values=[48,61,55,52,min(100,int(z.traffic_score)+8),min(100,int(z.traffic_score)+3)]
    st.markdown("### Congestion forecast")
    st.line_chart(pd.DataFrame({"Congestion %":values},index=hours))
    st.info("Decision recommendation: use the alternative route when the predicted congestion threshold is exceeded.")

# ---------- Waste ----------
elif module == "Waste Intelligence":
    st.header("🗑️ AI-Based Waste Management")
    cols=st.columns(4)
    status="HIGH" if z.predicted_overflow>=70 else "MEDIUM" if z.predicted_overflow>=40 else "LOW"
    for c,(a,b,d) in zip(cols,[
        ("Overflow probability",f"{z.predicted_overflow}%","AI prediction"),
        ("Priority",status,"Collection urgency"),
        ("Collection route","Route C → Market → Zone A","Optimization result"),
        ("Vision result","Mixed waste","Simulated CV")]):
        with c: kpi(a,b,d)
    st.markdown("### Computer-vision simulation")
    st.info("Image analysis: garbage accumulation detected · category: mixed waste · hotspot confidence: 91%")
    st.progress(min(100,int(z.predicted_overflow)))
    st.success("Recommended action: prioritize collection before predicted overflow.")

# ---------- Citizen ----------
elif module == "Citizen Services":
    st.header("📱 AI-Powered Citizen Services")
    st.caption("Text → AI classification → department → priority → action → feedback")
    text=st.text_area("Citizen complaint", "Large pothole near the bus stop. Vehicles are struggling to pass.")
    if st.button("Analyze with AI", type="primary"):
        t=text.lower()
        if any(k in t for k in ["pothole","road","traffic"]): cat,dept,sev="Road/Pothole","Roads","High"
        elif any(k in t for k in ["garbage","waste","bin","dump"]): cat,dept,sev="Waste","Sanitation","High"
        elif any(k in t for k in ["water","flood","rain"]): cat,dept,sev="Flood","Disaster Management","High"
        else: cat,dept,sev="General","Municipality","Medium"
        pri="P1" if sev=="High" else "P2"
        cols=st.columns(4)
        for c,(a,b,d) in zip(cols,[("Category",cat,"NLP classification"),("Severity",sev,"AI assessment"),("Department",dept,"Automatic routing"),("Priority",pri,"Resource queue")]):
            with c:kpi(a,b,d)
        st.success("Complaint routed successfully.")
    st.markdown("### Recent complaints")
    st.dataframe(complaints[["id","category","severity","department","priority","text"]],use_container_width=True,hide_index=True)

# ---------- Copilot ----------
elif module == "Governance Copilot":
    st.header("🤖 AI Governance Copilot")
    q=st.text_input("Ask the city", "Which zone needs immediate attention?")
    if st.button("Generate decision brief", type="primary"):
        high=zones.sort_values(["flood_risk","population_exposure"],ascending=False).iloc[0]
        st.markdown(f"## {high.zone} — HIGH PRIORITY")
        st.write("**Why:**")
        st.write(f"• Flood probability: {high.flood_risk}%")
        st.write(f"• Water level: {high.water_level}%")
        st.write(f"• Population exposure: {high.population_exposure}%")
        st.write(f"• Resource availability: {high.resource_availability}%")
        st.write("**Recommended action:** Deploy nearest emergency team → Divert traffic → Issue citizen warning.")
        st.info("Data → Insight → Decision")

# ---------- SDG ----------
else:
    st.header("🎯 SDG Impact Intelligence")
    cols=st.columns(3)
    for c,(a,b,d) in zip(cols,[
        ("SDG 11","Primary","Sustainable cities"),
        ("SDG 3 / 6 / 7","Supporting","Health, water, energy"),
        ("SDG 12 / 13 / 16","Supporting","Waste, climate, institutions")]):
        with c:kpi(a,b,d)
    st.markdown("### Simulated impact indicators")
    impact=pd.DataFrame({
        "Indicator":["Emergency response readiness","Waste collection efficiency","Citizen routing","Climate preparedness"],
        "Before":[58,61,54,49],
        "CITYNEXUS":[84,82,91,79]
    }).set_index("Indicator")
    st.bar_chart(impact)
    st.success("CITYNEXUS converts city data into measurable governance and SDG impact indicators.")

st.divider()
st.caption("CITYNEXUS AI · Nexus Innovators · Prototype demonstration · All displayed operational data is simulated.")
