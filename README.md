RESTURA

Malayalam Voice-Powered Restaurant Ordering System

"Live Application" (https://restura.streamlit.app)

Overview

Restura is a voice-powered restaurant ordering system designed to simplify communication between restaurant waiters and kitchen staff using Malayalam speech recognition and AI-powered voice synthesis.

The system enables waiters to place orders through voice input, process and verify them, and send confirmed orders to the kitchen through a connected digital workflow.

Problem Statement

Traditional restaurant order-taking relies heavily on manual communication between waiters and kitchen staff. This can lead to delays, communication errors and difficulties when handling regional-language orders.

Our Solution

Restura combines Gnani AI's speech technologies with a restaurant management workflow to enable Malayalam voice-based ordering and kitchen communication.

Key Features

- Voice-based ordering: Capture restaurant orders using Malayalam speech.
- Speech-to-Text: Convert spoken orders into text using Gnani AI.
- Order processing: Extract and match order information against restaurant menu items.
- Order verification: Review and modify orders before confirmation.
- Kitchen communication: Send confirmed orders to the kitchen interface.
- Voice announcements: Announce incoming kitchen orders using Gnani AI Text-to-Speech.
- Restaurant management: Provide an owner interface for restaurant operations.

System Workflow

1. Waiter records the customer's order.
2. Gnani AI converts speech into text.
3. The application processes and matches the order with menu items.
4. The waiter reviews and confirms the order.
5. Supabase stores and manages the order data.
6. The kitchen interface receives the order.
7. Gnani AI Text-to-Speech announces the order.

Technology Stack

Technology| Purpose
Python| Backend application logic
Streamlit| User interface
Gnani AI| Speech-to-Text and Text-to-Speech
Supabase| Database and order management
Requests| API communication

Application Structure

- "app.py" – Main application entry point
- "auth_service.py" – Authentication services
- "order_parser.py" – Order processing
- "restaurant_service.py" – Restaurant operations
- "ui.py" – User interface components
- "voice_service.py" – Voice and AI integration
- "pages/owner.py" – Owner interface
- "pages/waiter.py" – Waiter interface
- "pages/kitchen.py" – Kitchen interface

Getting Started

1. Clone the repository

git clone https://github.com/sajinkrishna14/livora.git
cd livora

2. Install dependencies

pip install -r requirements.txt

3. Configure credentials

Configure your Gnani AI and Supabase credentials using the required environment variables or Streamlit secrets.

Never commit API keys or private credentials.

4. Run the application

streamlit run app.py

Live Demo

https://restura.streamlit.app

Project Team

Abhiram B A — Lead Developer

Responsible for application development, system architecture, AI integrations, database integration and implementation.

Sajin Krishna — Project Assistance

Provided assistance during the project.

Project Context

Developed as part of the Gnani AI Great Indian AI Internship Challenge.
