<div align="center">

# 🏸 Badminton AI LangGraph Analysis 🏸

**✨ A Multi-Agent AI System for Advanced Badminton Match Analysis ✨**

[![Made with AI](https://img.shields.io/badge/Made_with-AI_&_Python-blueviolet?style=for-the-badge&logo=python)](https://www.python.org/)
![Framework](https://img.shields.io/badge/Framework-LangGraph-orange?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDI1NiAyNTYiPgo8cGF0aCBmaWxsPSIjZmZmZmZmIiBkPSJNMTE3LjIsMjU2bC0zMy45LTYwLjJMMTMyLjgsMTc1TDExNy4yLDI1NnoiLz4KPHBhdGggZmlsbD0iI2ZmZmZmZiIgZD0iTTk3LjMsMTY4LjRsLTM0LjgsNjEuNkwyOC42LDE3NWwzMy45LDYwLjJMOTcuMywxNjh6Ii8+CjxwYXRoIGZpbGw9IiNmZmZmZmYiIGQ9Ik0xMzguOCwyNTZsMzMuOS02MC4yTDEyMy4yLDE3NWwxNS42LDgwLjZMMTM4LjgsMjU2eiIvPgo8cGF0aCBmaWxsPSIjZmZmZmZmIiBkPSJNMTE3LjIsMGwzMy45LDYwLjJMODMuMiw4MS4yTDExNy4yLDB6Ii8+CjxwYXRoIGZpbGw9IiNmZmZmZmYiIGQ9Ik0xNTguNyw5Ny4zbDM0LjgtNjEuNkwxMjUuMyw4MS4ybDY4LjIsMTUuOEwxNTguNyw5Ny4zeiIvPgo8cGF0aCBmaWxsPSIjZmZmZmZmIiBkPSJNNzguOCwwTDQ0LjksNjAuMkw5NC40LDgxLjJMNzguOCwweiIvPgo8L3N2Zz4K)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)

</div>

## 🎯 **Project Overview**

This project is an advanced, multi-agent system designed to analyze badminton matches. It combines **parallel processing**, **computer vision**, and **large language models** to extract deep strategic insights from match footage. The entire system is orchestrated by **LangGraph**, allowing for a clear and robust flow of data between specialized AI agents.


```
🧠 Computer Vision for Pose & Shuttlecock Tracking
📄 LLM-Powered Text & Strategy Analysis
⚡ Parallel Data Processing with Dask & Ray
🤖 Agentic Architecture with LangGraph
💻 Runs entirely on CPU
```

--- 

## 📊 **System Architecture**

The system uses a modular, agent-based architecture where each component has a specific task. Data flows from the initial video download through a parallel pipeline and into the LangGraph-managed agent core, which generates the final analysis.

<div align="center">

```mermaid
flowchart TD
    A[Input: YouTube Video] --> B[Parallel Data Pipeline (Dask)]
    B --> C[Video Frame Extraction]
    C --> D[LangGraph Orchestrator]
    
    subgraph Agentic Core
        E[Video Analysis Agent]
        F[Strategy Analysis Agent]
        G[Report Generation Agent]
    end
    
    D --> E
    E --> F
    F --> G
    G --> H[Final Analysis Report]
```

</div>


</div>

--- 

## 🚀 **Getting Started**

Follow these steps to get the project up and running on your local machine.

### **1. Prerequisites**

- Python 3.8+
- `ffmpeg` (for creating dummy video files if YouTube download fails)

### **2. Setup**

```bash
# Clone the repository
git clone <your-repo-url>
cd badminton-analysis-system

# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

### **3. Environment Variables**

Create a file named `.env` in the project root and add your Google Gemini API key:

```env
# Replace with your actual key from Google AI Studio
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### **4. Run the Analysis**

```bash
python main.py
```

The script will print a step-by-step log of its progress, from downloading the video to generating the final report.

<div align="center">

### 🤖 **Built with Intelligence, Designed for Insight** 🤖

</div>
