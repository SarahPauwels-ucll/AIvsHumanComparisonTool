import streamlit as st
from components.teeth import load_teeth_circle
from AIOutput.teethSet import teeth as teethAI

load_teeth_circle(teethAI)


