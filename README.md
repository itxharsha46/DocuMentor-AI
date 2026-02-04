# DocuMentor AI 🧠✨

![Status](https://img.shields.io/badge/Status-Production_Ready-success)
![Stack](https://img.shields.io/badge/Stack-React_|_FastAPI_|_Gemini_AI-blueviolet)
![License](https://img.shields.io/badge/License-MIT-blue)

**DocuMentor AI** is an intelligent, full-stack document analysis platform that transforms static files into interactive conversational partners. Leveraging an advanced **Agentic RAG (Retrieval-Augmented Generation)** pipeline, it allows users to upload documents and receive context-aware, cited answers in real-time.

**[➡️ View Live Demo](https://explain-my-doc.vercel.app/)**

---

![DocuMentor AI Demo](./docs/demo.gif)
*(Note: Ensure a `demo.gif` exists in a `docs` folder for this preview to appear)*

## 🚀 Key Features

* **📄 Universal Upload:** Seamlessly processes PDF, DOCX, and TXT files.
* **🧠 Agentic RAG Architecture:** A smart pipeline that retrieves context, drafts responses, and self-critiques for maximum accuracy.
* **⚡ Real-Time Streaming:** ChatGPT-style token streaming for immediate feedback.
* **📚 Transparent Citations:** Every answer includes a "Show Sources" button to verify facts against the original text.
* **💡 Proactive Suggestions:** Automatically suggests relevant follow-up questions to guide exploration.
* **📥 AI Summarization Export:** Generates and downloads a structured PDF summary of your entire conversation.
* **📱 Responsive Design:** A sleek, mobile-optimized interface built with TailwindCSS.

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React (Vite), TailwindCSS, Axios |
| **Backend** | FastAPI, Uvicorn |
| **AI & ML** | Google Gemini API (Embeddings & Generation), ChromaDB (Vector Store) |
| **Deployment** | Vercel (Frontend), Render (Backend), GitHub Actions |

---

## 💻 Getting Started Locally

Follow these steps to run DocuMentor AI on your local machine.

### Prerequisites
* **Node.js 18+** & **npm**
* **Python 3.10+** & **pip**
* **Git**

### 1. Clone & Setup Backend
```bash
# Clone the repository
git clone [https://github.com/your-github-username/your-repo-name.git](https://github.com/your-github-username/your-repo-name.git)
cd your-repo-name

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

```

### 2. Configure Environment Variables

Create a `.env` file in the root directory and add your Google API key:

```env
# .env
GOOGLE_API_KEY=AIzaSy...your_key_here...

```

*(Get your key from [Google AI Studio](https://aistudio.google.com/))*

### 3. Setup Frontend

Open a new terminal and navigate to the frontend folder:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# Create a .env.local file inside /frontend
echo "VITE_API_BASE_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)" > .env.local

```

### 4. Run the Application

You need two terminals running simultaneously:

**Terminal 1 (Backend):**

```bash
# From root directory
uvicorn backend.main:app --reload

```

**Terminal 2 (Frontend):**

```bash
# From frontend directory
npm run dev

```

Open **`http://localhost:5173`** to start using DocuMentor AI!

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

```

```