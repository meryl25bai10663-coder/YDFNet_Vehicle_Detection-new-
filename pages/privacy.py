import streamlit as st
from legal_common import (page_setup, apply_theme, render_header, placeholder_warning, render_footer,
                          OPERATOR, CONTACT_EMAIL, JURISDICTION, HOSTING, RETENTION, LAST_UPDATED)

page_setup("Privacy policy")
apply_theme()
render_header()

st.title("Privacy policy")
st.caption(f"Last updated: {LAST_UPDATED}")
placeholder_warning()

st.markdown(f"""
EmergeRoute is operated by {OPERATOR}. This page explains what information the dashboard handles and who else receives it.

## What the dashboard handles

**Videos you upload.** When you choose Analyze video, the file is saved on our server under its original file name and processed by a vehicle detection model. The tool produces a detected video, per-frame vehicle counts and a summary. We keep uploaded videos for {RETENTION}.

**Results are shared.** The detection output is stored as shared files, so the most recent analysis can be shown to other visitors until it is replaced. Do not upload videos that show identifiable people, number plates or other personal information.

**Places you search or draw.** When you search for a place or draw an area, the text or coordinates are sent to OpenStreetMap services, which return place matches and street data. We do not attach your name or account to these requests, because the dashboard has no accounts.

**Map images.** Your browser loads map tiles directly from OpenStreetMap. That means OpenStreetMap can see your IP address and browser details, as with any website you visit.

**Technical logs.** Our hosting provider, {HOSTING}, may log technical information such as your IP address and the time of each request, to run and secure the service.

## What we do not do

We do not sell personal information. We do not add advertising or analytics trackers to this site. The dashboard has no sign-up, so we do not collect names or email addresses unless you write to us.

## Who receives information

OpenStreetMap services, as described above, and {HOSTING}, which hosts the dashboard. Both handle data under their own policies.

## Your choices

You can ask us to delete a video you uploaded, or to tell you what we hold about you, by writing to {CONTACT_EMAIL}. Depending on where you live, you may have further rights to access, correct or erase your information. The law of {JURISDICTION} applies to this policy.

## Children

The dashboard is not aimed at children, and we do not knowingly collect information from them.

## Changes

If we change this policy, we will update the date at the top of this page.

## Contact

{OPERATOR}, {CONTACT_EMAIL}
""")

render_footer()
