Restura

AI-Powered Voice-Based Restaurant Ordering System

Restura is a voice-enabled restaurant ordering system designed to simplify communication between waiters and kitchen staff. It uses Gnani AI speech technology to convert spoken Malayalam and Manglish orders into text and announce incoming orders to the kitchen.

Live Application: https://restura.streamlit.app

Repository: https://github.com/sajinkrishna14/Restura

---

1. Problem Statement

Traditional restaurant order management often relies on manual communication between waiters and kitchen staff.

This can lead to:

- Miscommunication during order placement.
- Delays in transmitting orders to the kitchen.
- Errors in recording menu items and quantities.
- Inefficient coordination between restaurant staff.
- Language barriers when entering orders.

Restura aims to address these challenges through an AI-powered voice ordering workflow.

2. Our Solution

Restura introduces a voice-based ordering system that allows waiters to communicate customer orders naturally in Malayalam or Manglish.

Using Gnani AI's speech technology, spoken orders are converted into text, processed into structured order information and sent to the kitchen through a centralised database.

The kitchen staff can receive and hear incoming orders, confirm them, and send confirmation updates back to the waiter.

3. Key Features

- Voice-Based Ordering: Waiters can record customer orders using their voice.
- Malayalam and Manglish Support: Designed for natural regional-language ordering.
- AI Speech-to-Text: Gnani AI converts spoken orders into text.
- Order Processing: Extracts relevant menu items and quantities from the recognised order.
- Order Review: Waiters can review and confirm orders before submission.
- Kitchen Dashboard: Displays incoming restaurant orders.
- AI Text-to-Speech: Gnani AI announces incoming orders to kitchen staff.
- Order Confirmation: Kitchen staff can confirm orders, and the waiter receives the confirmation update.
- Database Synchronisation: Supabase stores and synchronises restaurant order information.

4. System Architecture

The following diagram illustrates the overall Restura workflow and communication between its interfaces.

"Restura System Architecture" (assets/restura-system-architecture.png)

5. Application Screenshots

Owner Dashboard

"Owner Interface" (assets/screenshots/owner-interface.png)

Waiter Interface

"Waiter Interface" (assets/screenshots/waiter-interface.png)

Kitchen Interface

"Kitchen Interface" (assets/screenshots/kitchen-interface.png)

Order Confirmation

"Order Confirmation" (assets/screenshots/order-confirmation.png)

6. System Workflow

1. The waiter opens the waiter interface and records the customer's order.
2. Gnani AI Speech-to-Text processes the audio and generates a text transcript.
3. The application processes the recognised text and identifies menu items and quantities.
4. The waiter reviews the order and confirms it.
5. The order is stored in Supabase.
6. The kitchen interface receives the incoming order.
7. Gnani AI Text-to-Speech announces the order to the kitchen staff.
8. Kitchen staff confirm the order.
9. The confirmation status is updated and communicated back to the waiter.

7. Technology Stack

Technology| Purpose
Python| Core application development
Streamlit| User interface and dashboards
Gnani AI| Speech-to-Text and Text-to-Speech
Supabase| Database and order synchronisation
Git and GitHub| Version control and source code management

8. Project Structure

Restura/
│
├── app.py
├── auth_service.py
├── order_parser.py
├── restaurant_service.py
├── ui.py
├── voice_service.py
│
├── pages/
│   ├── kitchen.py
│   ├── owner.py
│   └── waiter.py
│
├── assets/
│   ├── restura-system-architecture.png
│   └── screenshots/
│       ├── owner-interface.png
│       ├── waiter-interface.png
│       ├── kitchen-interface.png
│       └── order-confirmation.png
│
├── docs/
│   └── Restura_One_Page_Project_Pitch.pdf
│
├── requirements.txt
└── README.md

9. Installation and Setup

Prerequisites

- Python 3.10 or later
- Git
- Gnani AI API credentials
- Supabase project and credentials

Step 1: Clone the repository

git clone https://github.com/sajinkrishna14/Restura.git
cd Restura

Step 2: Create a virtual environment

python -m venv venv

Activate it:

Windows

venv\Scripts\activate

macOS / Linux

source venv/bin/activate

Step 3: Install dependencies

pip install -r requirements.txt

Step 4: Configure credentials

Configure the required Gnani AI and Supabase credentials using the application's expected environment variables or Streamlit secrets configuration.

Do not commit API keys, passwords or private credentials to GitHub.

Step 5: Run the application

streamlit run app.py

10. Project Demonstration

Experience the application through the live deployment:

"Open Restura" (https://restura.streamlit.app)

11. Project Documentation

The one-page project pitch and system architecture diagram are included in this repository.

- "System Architecture" (assets/restura-system-architecture.png)
- "One-Page Project Pitch" (docs/Restura_One_Page_Project_Pitch.pdf)

12. Project Team

Abhiram B A
Lead Developer

Responsible for application development, system implementation, architecture, AI integration, database integration and user interface development.

Sajin Krishna
Project Assistance

13. Project Objective

Restura demonstrates how AI-powered speech technologies can be integrated into real-world business workflows to improve communication, reduce manual effort and make restaurant operations more efficient.

---

Developed as part of the Gnani AI Great Indian AI Internship Challenge.
