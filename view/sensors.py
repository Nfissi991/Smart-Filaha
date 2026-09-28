# view/sensors.py
import streamlit as st
import pandas as pd
from services.sensor_service import get_my_sensors, create_sensor, add_reading, get_readings
from database.db import SessionLocal
from database.models import Parcel


def render_sensors():
    st.title("🌱 Mes capteurs")

    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Utilisateur non connecté.")
        return

    sensors = get_my_sensors(user_id)

    online = sum(1 for s in sensors if s.last_seen)
    offline = len(sensors) - online

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🌱 Capteurs", len(sensors))
    with c2: st.metric("🟢 En ligne", online)
    with c3: st.metric("🔴 Hors ligne", offline)

    st.divider()

    with st.expander("➕ Ajouter un capteur"):
        name = st.text_input("Nom du capteur", placeholder="Capteur Tomates A", key="sensor_name_input")
        device_uid = st.text_input("ID du capteur", placeholder="SENSOR-001", key="sensor_uid_input")
        sensor_type = st.selectbox("Type", ["multi", "soil", "weather"], key="sensor_type_input")

        db = SessionLocal()
        try:
            parcels = db.query(Parcel).filter(Parcel.owner_id == user_id).all()
        finally:
            db.close()

        parcel_options = {"Aucune parcelle": None}
        for p in parcels:
            parcel_options[f"{p.name} — {p.location or ''}"] = p.id
        parcel_label = st.selectbox("Parcelle", list(parcel_options.keys()), key="sensor_parcel_input")

        if st.button("Ajouter le capteur", use_container_width=True, key="btn_add_sensor"):
            if not name or not device_uid:
                st.warning("Nom et ID du capteur obligatoires.")
            else:
                create_sensor(
                    owner_id=user_id, name=name, device_uid=device_uid,
                    sensor_type=sensor_type, parcel_id=parcel_options[parcel_label],
                )
                st.success("Capteur ajouté.")
                st.rerun()

    st.divider()

    if not sensors:
        st.info("Aucun capteur connecté pour le moment.")
        return

    for sensor in sensors:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(f"🌱 {sensor.name}")
                st.caption(f"ID: {sensor.device_uid}")
                if sensor.last_seen:
                    st.success("🟢 Capteur actif")
                else:
                    st.warning("🔴 Pas encore de données")
                st.write(f"🔋 Batterie: {sensor.battery_level:.0f}%")
            with col2:
                if st.button("Voir", key=f"sensor_view_{sensor.id}"):
                    st.session_state["selected_sensor_id"] = sensor.id
                    st.rerun()

    selected_id = st.session_state.get("selected_sensor_id")
    if not selected_id:
        return

    sensor = next((s for s in sensors if s.id == selected_id), None)
    if not sensor:
        return

    st.divider()
    st.header(f"📡 {sensor.name}")

    readings = get_readings(sensor.id, limit=50)

    with st.expander("🧪 Ajouter une mesure de test"):
        c1, c2 = st.columns(2)
        with c1:
            soil = st.number_input("Humidité du sol (%)", min_value=0.0, max_value=100.0, value=60.0, key="test_soil")
            temperature = st.number_input("Température (°C)", value=24.0, key="test_temp")
        with c2:
            air = st.number_input("Humidité air (%)", min_value=0.0, max_value=100.0, value=60.0, key="test_air")
            ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=6.8, key="test_ph")

        if st.button("Enregistrer la mesure", key="btn_add_reading"):
            add_reading(sensor.id, soil_moisture=soil, temperature=temperature, air_humidity=air, ph=ph)
            st.success("Mesure enregistrée.")
            st.rerun()

    if not readings:
        st.info("Aucune mesure disponible.")
        return

    latest = readings[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💧 Sol", f"{latest.soil_moisture:.1f}%" if latest.soil_moisture is not None else "-")
    with c2: st.metric("🌡 Température", f"{latest.temperature:.1f} °C" if latest.temperature is not None else "-")
    with c3: st.metric("💨 Humidité air", f"{latest.air_humidity:.1f}%" if latest.air_humidity is not None else "-")
    with c4: st.metric("🧪 pH", f"{latest.ph:.2f}" if latest.ph is not None else "-")

    rows = list(reversed(readings))
    df = pd.DataFrame({
        "Date": [r.recorded_at for r in rows],
        "Humidité sol": [r.soil_moisture for r in rows],
        "Température": [r.temperature for r in rows],
        "pH": [r.ph for r in rows],
    })

    st.subheader("💧 Évolution de l'humidité du sol")
    st.line_chart(df.set_index("Date")[["Humidité sol"]])

    st.subheader("🌡 Évolution de la température")
    st.line_chart(df.set_index("Date")[["Température"]])

    st.subheader("🧪 Évolution du pH")
    st.line_chart(df.set_index("Date")[["pH"]])

    if latest.soil_moisture is not None and latest.soil_moisture < 30:
        st.error("⚠️ Humidité du sol faible. Vérifiez l'irrigation.")
    if latest.temperature is not None and latest.temperature > 38:
        st.warning("🌡 Température élevée détectée.")