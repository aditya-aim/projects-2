import streamlit as st
import openai

# Streamlit App Configuration
st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to call GPT-4o API
def call_gpt4o(api_key, system_prompt, user_message):
    """Calls GPT-4o API using OpenAI's updated client API."""
    client = openai.Client(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# Function to display dietary plan
def display_dietary_plan(plan_content):
    with st.expander("📋 Your Personalized Dietary Plan", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Why this plan works")
            st.info(plan_content.get("why_this_plan_works", "Information not available"))
            st.markdown("### 🍽️ Meal Plan")
            st.write(plan_content.get("meal_plan", "Plan not available"))

        with col2:
            st.markdown("### ⚠️ Important Considerations")
            considerations = plan_content.get("important_considerations", "").split("\n")
            for consideration in considerations:
                if consideration.strip():
                    st.warning(consideration)

# Function to display fitness plan
def display_fitness_plan(plan_content):
    with st.expander("💪 Your Personalized Fitness Plan", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Goals")
            st.success(plan_content.get("goals", "Goals not specified"))
            st.markdown("### 🏋️‍♂️ Exercise Routine")
            st.write(plan_content.get("routine", "Routine not available"))

        with col2:
            st.markdown("### 💡 Pro Tips")
            tips = plan_content.get("tips", "").split("\n")
            for tip in tips:
                if tip.strip():
                    st.info(tip)

# Main function
def main():
    if "dietary_plan" not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.title("🏋️‍♂️ AI Health & Fitness Planner")
    st.markdown("""
        <div style='background-color: #00008B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; color: white;'>
        Get personalized dietary and fitness plans tailored to your goals and preferences.
        Our AI-powered system considers your unique profile to create the perfect plan for you.
        </div>
    """, unsafe_allow_html=True)

    # Sidebar: API Configuration
    with st.sidebar:
        st.header("🔑 API Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")

        if not openai_api_key:
            st.warning("⚠️ Please enter your OpenAI API Key to proceed")
            return
        st.success("API Key accepted!")

    # User Input Section
    if openai_api_key:
        st.header("👤 Your Profile")

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Age", min_value=10, max_value=100, step=1)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1)
            activity_level = st.selectbox(
                "Activity Level",
                options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]
            )
            dietary_preferences = st.selectbox(
                "Dietary Preferences",
                options=["Vegetarian", "Keto", "Gluten-Free", "Low Carb", "Dairy-Free"]
            )

        with col2:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.1)
            sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
            fitness_goals = st.selectbox(
                "Fitness Goals",
                options=["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training"]
            )

        if st.button("🎯 Generate My Personalized Plan"):
            with st.spinner("Creating your perfect health and fitness routine..."):
                try:
                    user_profile = f"""
                    Age: {age}
                    Weight: {weight}kg
                    Height: {height}cm
                    Sex: {sex}
                    Activity Level: {activity_level}
                    Dietary Preferences: {dietary_preferences}
                    Fitness Goals: {fitness_goals}
                    """

                    # Get dietary plan from GPT-4o
                    dietary_prompt = "You are a nutrition expert. Provide a detailed dietary plan for the user based on their profile."
                    dietary_response = call_gpt4o(openai_api_key, dietary_prompt, user_profile)

                    dietary_plan = {
                        "why_this_plan_works": "Balanced macronutrients and tailored calorie intake.",
                        "meal_plan": dietary_response,
                        "important_considerations": """
                        - Hydration: Drink plenty of water throughout the day.
                        - Include fiber-rich foods for digestion.
                        - Ensure adequate intake of vitamins and minerals.
                        """
                    }

                    # Get fitness plan from GPT-4o
                    fitness_prompt = "You are a fitness coach. Provide a personalized workout routine based on the user's profile."
                    fitness_response = call_gpt4o(openai_api_key, fitness_prompt, user_profile)

                    fitness_plan = {
                        "goals": "Improve strength, endurance, and overall fitness.",
                        "routine": fitness_response,
                        "tips": """
                        - Track progress weekly.
                        - Maintain proper form in exercises.
                        - Stay consistent and allow for recovery days.
                        """
                    }

                    st.session_state.dietary_plan = dietary_plan
                    st.session_state.fitness_plan = fitness_plan
                    st.session_state.plans_generated = True

                    # Display plans
                    display_dietary_plan(dietary_plan)
                    display_fitness_plan(fitness_plan)

                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

        # Q&A Section
        if st.session_state.plans_generated:
            st.header("❓ Questions about your plan?")
            question_input = st.text_input("Ask something about your plan:")

            if st.button("Get Answer"):
                if question_input:
                    with st.spinner("Finding the best answer for you..."):
                        context = f"Dietary Plan: {st.session_state.dietary_plan.get('meal_plan', '')}\n\nFitness Plan: {st.session_state.fitness_plan.get('routine', '')}"
                        answer = call_gpt4o(openai_api_key, "You are a fitness and diet expert. Answer user questions.", f"{context}\nUser Question: {question_input}")
                        st.session_state.qa_pairs.append((question_input, answer))
                        st.markdown(f"**Q:** {question_input}")
                        st.markdown(f"**A:** {answer}")

if __name__ == "__main__":
    main()
