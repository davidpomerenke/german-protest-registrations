"""Streamlit app."""

from importlib.metadata import version

import streamlit as st

st.title(f"german-protest-registrations v{version('german-protest-registrations')}")  # type: ignore[no-untyped-call]
