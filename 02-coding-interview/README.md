# Online Coding Interview Platform

This repository contains an end-to-end real-time collaborative coding interview platform, developed as part of the **ML Zoomcamp – Coding Interview App Homework**.

The application allows interviewers and candidates to join a shared session, collaboratively edit code with real-time synchronization, switch programming languages, and execute JavaScript and Python code **securely inside the browser** using WebAssembly.

---

## 📌 Features

### ✔ Real-Time Collaboration
- Multiple users can join the same interview session.
- Code updates propagate instantly using **Socket.IO**.
- Shared state for both code and selected language.

### ✔ Code Execution (Browser-Only)
- **JavaScript** execution using a browser sandbox.
- **Python** execution through **Pyodide (Python compiled to WebAssembly)**.
- No server-side code execution for security and isolation.

### ✔ Syntax Highlighting
- Implemented using **@monaco-editor/react**.
- Supports JavaScript and Python syntax highlighting.

### ✔ Backend API
- Built with **Express.js**.
- REST endpoint for generating interview session links.
- Real-time communication powered by WebSockets.

### ✔ Modern Frontend
- Built with **React + Vite**.
- Simple UI for creating and joining interview sessions.
- Collaborative editor with output console.

### ✔ Full Containerization
- Single Dockerfile using **node:20-alpine**.
- Builds and serves both frontend and backend from one container.

---

## 📁 Project Structure

