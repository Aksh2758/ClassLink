# 🎓 ClassLink – Smart College Management Portal

A modern, full-stack academic management system that streamlines administration and enhances communication between **Students**, **Faculty**, and **Admins** — all in one unified portal.

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active_Development-green" />
  <img src="https://img.shields.io/badge/License-MIT-blue" />
</p>

---

## 🚀 What is ClassLink?

**ClassLink** is a role-based college ERP portal built to digitize and automate core academic workflows such as:

- Timetables  
- Attendance  
- Notes & Circulars  
- Marks Management  
- Real-time Notifications  

It provides **separate dashboards** for Students, Faculty & Admins with a clean and responsive UI.

---

## 🛠 Tech Stack

### **Frontend**
- ⚛ React.js  
- 🎨 TailwindCSS / CSS  
- 🔗 Axios  
- 🔔 Socket.IO Client  

### **Backend**
- 🐍 Flask (Python) — REST API  
- 🔌 Flask-SocketIO  
- 🛢 PyMySQL  
- 🔐 JWT Authentication  

### **Database**
- 🗄 MySQL  

---

## ✨ Core Features

### 🔔 Real-Time Notifications
- Timetable updates  
- Notes uploads  
- Circular announcements  

---

### 👨‍🏫 Faculty Portal Features
- Profile management  
- Timetable view  
- Attendance marking  
- Internal Assessment (IA) marks entry  
- Upload notes (PDF, PPT, Images)  
- Post circulars (department-wise or global)  

---

### 👨‍🎓 Student Portal Features
- Dashboard overview  
- Attendance analytics (Green / Yellow / Red)  
- Download notes & materials  
- View IA marks & results  
- View circulars & announcements  
- Profile update & password management  

---

## 📁 Project Structure

```
ClassLink/
├── backend/               
│   ├── app.py               # App entry point
│   ├── config.py            # DB credentials & secrets
│   ├── uploads/             # Notes, images, circulars
│   ├── models/              # SQL query layer
│   ├── routes/              # Modular API blueprints
│   └── utils/               # JWT, DB helpers
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       │   ├── faculty/
│       │   └── student/
│       └── App.js
│
└── README.md
```

---

## 🧩 Getting Started

### ✔ Prerequisites
- Python **3.8+**
- Node.js **16+**
- MySQL Server

---

## 🔧 1. Database Setup

1. Open MySQL Workbench / CLI  
2. Create database:

```sql
CREATE DATABASE classlink_db;
```

3. Import schema that includes:
- Users  
- Students  
- Faculty  
- Attendance  
- Marks  
- Notes  
- Circulars  
- Timetable  

---

## 🐍 2. Backend Setup

```bash
cd backend

# Create virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

Update **config.py**:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "classlink_db"
```

Start the server:

```bash
python app.py
```

Backend URL → **http://localhost:5000**

---

## 🌐 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend URL → **http://localhost:3000**

---

## 🔌 API Routes

| Module      | Endpoint        | Description |
|-------------|-----------------|-------------|
| Auth        | /api/auth     | Login, tokens |
| Profile     | /api/profile  | View/update profile |
| Notes       | /api/notes    | Upload & fetch notes |
| Attendance  | /api/attendance | Mark/view attendance |
| Marks       | /api/marks    | IA scores |
| Circulars   | /api/circulars | Announcements |
| Timetable   | /api/timetable | Manage schedules |

---

## 🤝 Contributing

1. Fork the repo  
2. Create a branch:  
   ```bash
   git checkout -b feature/newFeature
   ```
3. Commit changes  
4. Push and create a Pull Request  

---

## 📜 License
Distributed under the **MIT License**.

---

## 🧑‍💻 Developed By
**Aksh2758**