import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
# from openai import OpenAI
# from google import genai
import requests
import os
# import dotenv
from dotenv import load_dotenv

# Load environment variable 

class TravelPlannerAgent:
    def __init__(self,model_name,generation_config,safety_settings):
        # dotenv.load_dotenv()
        # # api_key = os.getenv('GOOGLE_API_KEY')
        # os.environ["GOOGLE_API_KEY"] = "GOOGLE_API_KEY"
        # genai.configure(api_key="GOOGLE_API_KEY")
        self.model = genai.GenerativeModel(model_name=model_name,
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)
        # self.tavily_client = tavily.TavilyClient(api_key="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")
    
    def extract_context(self, user_input):
        """Extract key travel details from user input"""
        context_prompt = f"""
        Carefully extract and analyze the travel details from the following user query:
        
        Identify and list these specific details:
        - Destination (location)
        - Intended Travel Dates
        - Budget Range
        - Travel Purpose
        - Specific User Preferences
        
        User Query: {user_input}
        
        Provide a structured response with clear categories for each detail.
        """
        # model_name = 'gemini-2.0-flash'
        response = self.model.generate_content(context_prompt)
        return response.text
    
    def search_destination(self, destination):
        """Conduct research about the destination"""
        research_prompt = f"""
        Comprehensive Travel Research for {destination}:
        
        Provide detailed information including:
        1. Top 5 Must-Visit Attractions
        2. Local Cultural Highlights
        3. Best Time to Visit
        4. Estimated Costs for Major Activities
        5. Local Transportation Options
        6. Unique Local Experiences
        7. Potential Travel Challenges or Considerations
        
        Format the information in a clear, informative manner.
        """
        # model_name = 'gemini-2.0-flash'
        response = self.model.generate_content(research_prompt)
        return response.text
    
    def generate_itinerary(self, context, destination_research):
        """Generate personalized travel itinerary"""
        itinerary_prompt = f"""
        Create a Detailed Travel Itinerary Based On:
        
        User Context:
        {context}
        
        Destination Research:
        {destination_research}
        
        Itinerary Guidelines:
        - Create a day-by-day breakdown
        - Include specific times for activities
        - Balance excitement and relaxation
        - Consider budget constraints
        - Provide approximate costs for each activity
        - Include backup/alternative options
        - Add local dining recommendations
        
        Desired Output Format:
        Day 1:
        - Morning: [Activity] (Cost: $X)
        - Afternoon: [Activity] (Cost: $X)
        - Evening: [Activity] (Cost: $X)
        
        Travel Tips & Notes:
        """
        # model_name = 'gemini-2.0-flash'
        response = self.model.generate_content(itinerary_prompt)
        return response.text

def main():
    st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
    
    st.title("🌍 Travel Planner")
    
    # Sidebar for user inputs
    st.sidebar.header("🧭 Travel Details")
    destination = st.sidebar.text_input("Destination", placeholder="e.g., Paris, France")
    travel_dates = st.sidebar.date_input("Travel Dates")
    budget = st.sidebar.selectbox(
        "Budget Range", 
        [
            "Budget (<$100/day)", 
            "Moderate ($100-$250/day)", 
            "Comfortable ($250-$500/day)", 
            "Luxury ($500+/day)"
        ]
    )
    
    # Optional image upload for destination inspiration
    uploaded_image = st.sidebar.file_uploader(
        "Upload Destination Inspiration Image (Optional)", 
        type=['png', 'jpg', 'jpeg']
    )
    
    # Travel purpose selection
    travel_purpose = st.sidebar.selectbox(
        "Trip Purpose",
        [
            "Leisure", 
            "Cultural Exploration", 
            "Adventure", 
            "Romantic Getaway", 
            "Family Vacation"
        ]
    )
    

# Configure Gemini API
    genai.configure(api_key="AIzaSyCxTWQNEYYpP_3AepcSqZcPDvhCy0hlMtk")
    
    
    generation_config = {
        "temperature": 0.4,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,    
    }
        # api_key = os.getenv("GEMINI_API_KEY")
    available_models = [m.name for m in genai.list_models()]
    # Find appropriate models for text and multimodal
    if "models/gemini-1.5-pro" in available_models:
        text_model_name = "models/gemini-1.5-pro"
        vision_model_name = "models/gemini-1.5-pro"
    elif "models/gemini-1.0-pro" in available_models:
        text_model_name = "models/gemini-1.0-pro"
        vision_model_name = "models/gemini-1.0-pro-vision"
    else:
        # Fallback to basic models
        text_model_name = [m for m in available_models if "text" in m.lower()][0]
        vision_model_name = [m for m in available_models if "vision" in m.lower()][0]
    
    travel_agent = TravelPlannerAgent(model_name=text_model_name,generation_config=generation_config,safety_settings=safety_settings)
    
    
    # Generate Itinerary Button
    if st.sidebar.button("✨ Generate Personalized Itinerary"):
        with st.spinner("Crafting Your Perfect Travel Experience..."):
            try:
                # Combine user inputs
                user_context = f"""
                Destination: {destination}
                Travel Dates: {travel_dates}
                Budget: {budget}
                Purpose: {travel_purpose}
                """
                
                # Extract context
                context_details = travel_agent.extract_context(user_context)
                
                # Research destination
                destination_research = travel_agent.search_destination(destination)
                
                # Generate itinerary
                itinerary = travel_agent.generate_itinerary(
                    context_details, 
                    destination_research
                )
                
                # Display results
                st.success("🎉 Your Personalized Travel Itinerary")
                st.markdown(itinerary)
                
                # Optional: If image was uploaded, use multimodal capabilities
                if uploaded_image:
                    # Process image with Gemini
                    image_model = genai.GenerativeModel('gemini-pro-vision')
                    image_response = image_model.generate_content([
                        "Analyze this destination image and provide additional travel insights.", 
                        uploaded_image
                    ])
                    st.info("🖼️ Image Insights: " + image_response.text)
                
            except Exception as e:
                st.error(f"Error generating itinerary: {e}")

if __name__ == "__main__":
    main()