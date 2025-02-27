import streamlit as st
from agno.agent import Agent as AgnoAgent
from agno.models.openai import OpenAIChat as AgnoOpenAIChat
import asyncio
from playwright.async_api import async_playwright

st.set_page_config(page_title="PyGame Code Generator", layout="wide")

# Initialize session state
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {"openai": ""}

if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""

# Sidebar for API key
with st.sidebar:
    st.title("API Key Configuration")
    st.session_state.api_keys["openai"] = st.text_input(
        "OpenAI API Key", type="password", value=st.session_state.api_keys["openai"]
    )
    
    st.markdown("---")
    st.info("""
    📝 How to use:
    1. Enter your OpenAI API key
    2. Describe your PyGame visualization
    3. Click 'Generate Code' to get the code
    4. Click 'Run on Trinket' to execute the code automatically
    """)

# Main UI
st.title("🎮 AI PyGame Code Generator with GPT-4o")
example_query = "Create a particle system simulation where 100 particles emit from the mouse position and respond to keyboard-controlled wind forces"
query = st.text_area("Enter your PyGame query:", height=70, placeholder=f"e.g.: {example_query}")

col1, col2 = st.columns(2)
generate_code_btn = col1.button("Generate Code")
run_on_trinket_btn = col2.button("Run on Trinket")

if generate_code_btn and query:
    if not st.session_state.api_keys["openai"]:
        st.error("Please provide your OpenAI API key")
        st.stop()

    # Initialize OpenAI agent
    openai_agent = AgnoAgent(
        model=AgnoOpenAIChat(id="gpt-4o", api_key=st.session_state.api_keys["openai"]),
        show_tool_calls=True,
        markdown=True
    )

    system_prompt = """You are a PyGame and Python expert who generates high-quality Python code for PyGame-based visualizations. 
    Your responses must contain only Python code without explanations or markdown backticks."""

    try:
        with st.spinner("Generating code..."):
            response = openai_agent.run(f"{system_prompt}\nUser query: {query}")
            extracted_code = response.content

        # Store and display the generated code
        st.session_state.generated_code = extracted_code
        with st.expander("Generated PyGame Code", expanded=True):      
            st.code(extracted_code, language="python")
            
        st.success("Code generated successfully! Click 'Run on Trinket' to execute.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif run_on_trinket_btn:
    if not st.session_state.generated_code:
        st.warning("Generate code first before running on Trinket")
    else:
        async def run_on_trinket(code: str):
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()

                # Open Trinket.io PyGame editor
                await page.goto("https://trinket.io/features/pygame")

                # Wait for the code editor
                await page.wait_for_selector("textarea")
                
                # Select and clear existing code
                await page.click("textarea")
                await page.keyboard.press("Control+A")  # Select all text
                await page.keyboard.press("Backspace")  # Delete
                
                # Paste new code
                await page.keyboard.type(code, delay=0.02)  # Simulate typing
                
                # Click the "Run" button
                await page.click("text=Run")  
                
                st.success("Code is running on Trinket! Check your browser.")
                
                # Keep the page open for interaction
                await asyncio.sleep(30)
                await browser.close()

        asyncio.run(run_on_trinket(st.session_state.generated_code))
