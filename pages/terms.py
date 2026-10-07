import streamlit as st
from legal_common import (page_setup, apply_theme, render_header, placeholder_warning, render_footer,
                          OPERATOR, CONTACT_EMAIL, JURISDICTION, LAST_UPDATED)

page_setup("Terms and conditions")
apply_theme()
render_header()

st.title("Terms and conditions")
st.caption(f"Last updated: {LAST_UPDATED}")
placeholder_warning()

st.markdown(f"""
By using the EmergeRoute dashboard you agree to these terms. The dashboard is operated by {OPERATOR}. If you do not agree, please do not use it.

## What the dashboard is

EmergeRoute proposes traffic-control policies, tests each one in a SUMO simulation and ranks the results. It is decision support. Its output comes from simulated traffic, and the built-in network is synthetic. The traffic demand in the real-area tool is a setting you choose, not a measurement of that place.

## Not for operating real signals

Do not use the output to change, control or time real traffic signals, or to make safety-critical decisions, without independent engineering review. Recommendations are never applied to real signals by this dashboard.

## Your content

You may upload only videos you have the right to use. Do not upload content that is unlawful, that infringes someone else's rights, or that shows identifiable people or number plates without a lawful basis. You keep your rights in your videos. You give us permission to store and process them to provide the analysis, as described in the privacy policy.

## Acceptable use

Do not misuse the dashboard. That includes attempting to disrupt it, accessing it by automated means at a volume that harms the service, or sending bulk requests through it to OpenStreetMap services, which have their own usage limits.

## Accuracy and availability

Results depend on the simulation, the scenario and the model, and they can be wrong. Vehicle counts come from an automated detector and can miss or double-count vehicles. We provide the dashboard as it is, we do not promise it will always be available, and we may change or remove features.

## Liability

To the extent the law allows, we are not liable for losses that result from using the dashboard or relying on its results. Nothing in these terms limits liability that cannot be limited by law.

## Governing law

These terms are governed by the law of {JURISDICTION}.

## Changes

We may update these terms. The date at the top shows the latest version. Continued use after a change means you accept it.

## Contact

{OPERATOR}, {CONTACT_EMAIL}
""")

render_footer()
