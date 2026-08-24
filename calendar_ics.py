import streamlit as st
import datetime
from datetime import timedelta
from core.translations import m4_labels

def render(current_lang):
    l4 = m4_labels.get(current_lang, m4_labels["English"])
    st.markdown(l4["title"])
    st.caption(l4["caption"])
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        appt_date = st.date_input(l4["date_label"], datetime.date.today() + timedelta(days=14))
    with col2:
        appt_time = st.time_input(l4["time_label"], datetime.time(10, 0))

    location = st.text_input(l4["location_label"], l4["location_placeholder"])

    if st.button(l4["btn_generate"], type="primary"):
        dt_start = datetime.datetime.combine(appt_date, appt_time)
        dt_end = dt_start + timedelta(hours=1)

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Medicare Compass//SHIP Appointment//EN
BEGIN:VEVENT
SUMMARY:🩺 SHIP Medicare Official Counseling
DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}
DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}
LOCATION:{location}
DESCRIPTION:📌 Checklist for Counseling:\\n1. Bring your 1-Page Summary from Medicare Compass App.\\n2. Bring all current prescription drug bottles.\\n3. Bring your Medicare Red, White & Blue card.
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:SHIP Counseling tomorrow! Remember to bring your 1-Page Summary and drug bottles.
END:VALARM
END:VEVENT
END:VCALENDAR"""

        st.download_button(
            label=l4["btn_download"],
            data=ics_content,
            file_name="ship_appointment.ics",
            mime="text/calendar",
            use_container_width=True,
        )
        st.success(l4["success_msg"])