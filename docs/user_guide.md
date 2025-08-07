BusinAI: AI Policy Advisor for Small Businesses
By: Mohammed Hanees M

Live Application Link
You can access the deployed application here:
[Link Here]

1. Project Overview & Use Case
BusinAI is an intelligent chatbot designed to solve a critical problem for small business owners: navigating the complex world of legal and regulatory compliance. The application serves as a "first-line" AI advisor, capable of answering specific questions from business documents and providing general guidance using up-to-date web search results.

This project was built to fulfill the creative and technical requirements of the NeoStats "Chatbot Blueprint" challenge.

2. Core Features
Hybrid Conversational AI: Intelligently switches between document-based answers (RAG) and live web search to provide the most accurate response.

High-Accuracy RAG: Utilizes semantic chunking via langchain to ensure document context is preserved, leading to highly accurate answers from uploaded files.

Multi-Format Document Upload: Supports .pdf, .docx, and image files, with text extraction handled by a robust processing pipeline.

Live Web Search: Answers general knowledge questions by searching the web and prioritizing trusted sources like .gov and .org domains.

User-Centric UI: Features a clean, intuitive interface with full chat management (New, Delete, Star) and customizable response modes (Concise vs. Detailed).

Accessibility: Includes a text-to-speech feature with an interactive audio player for every AI response.

3. System Architecture & Tech Stack
The application is built on a modular and scalable Python backend, ensuring clean code and easy maintenance.

Frontend: Streamlit

Core AI Model: Google Gemini 1.5 Flash

Key Libraries:

langchain (for semantic chunking)

sentence-transformers & faiss-cpu (for the RAG pipeline)

duckduckgo-search (for live web search)

gTTS (for text-to-speech)

4. How to Run the Project Locally
Prerequisites:

Python 3.9+

An environment that can run bash scripts (like Git Bash on Windows)

Setup Instructions:

Clone the repository:

git clone [Your GitHub Repository URL]
cd [ Repository Name]

Create a .env file in the root directory and add your API key:

GEMINI_API_KEY="ABCD"

Run the setup script to create the virtual environment and install dependencies:

bash scripts/setup_env.sh

Activate the virtual environment:

source .venv/bin/activate

Run the application:

streamlit run src/app.py

5. Challenges & Solutions
Challenge: Initial RAG answers were inaccurate.

Solution: Implemented semantic chunking with langchain instead of a basic text splitter. This preserved the meaning of the text and dramatically improved accuracy.

Challenge: Multiple library version conflicts caused critical errors.

Solution: Created a stable, pinned requirements.txt file and rebuilt the virtual environment to guarantee a conflict-free and reproducible setup.