![CI](https://github.com/nexapytech/django-cbt-platform/actions/workflows/ci.yml/badge.svg)

# NexapyCBT  Python Django Computer-Based Testing Platform


## 🛠 Tech Stack
- **Language:** Python 3
- **Backend Framework:** Django
- **Database:** MySQL, sqlite3
- **Containerization:** Docker
- **NLP & AI:** spaCy (text similarity)
- **OS Tested On:** Linux (Ubuntu recommended)

---

## 🔥 Overview
NexapyCBT is a cutting-edge platform designed to revolutionize the way exams are taken.  
With the flexibility to create, manage, and participate in Computer-Based Tests (CBTs), NexapyCBT provides a seamless, efficient, and secure testing experience for both educators and learners.

---

## 🚀 Features
- Create unlimited exams
- Unlimited questions per exam
- Delete exams
- Upload questions via Excel
- Publish unlimited exams
- Enable feedback for exams
- Role-based access: admin, instructor, student
- Automated grading and result tracking
- Secure exam delivery
- NLP-powered features using spaCy

---

## 🧠 NLP & spaCy Integration
NexapyCBT integrates spaCy to enhance evaluation of non-multiple-choice (theory/subjective) questions.

**How it works:**
1. Theory answers are processed using text similarity techniques.
2. Student responses are compared with expected answers.
3. spaCy’s pretrained language model enables semantic similarity matching.

This allows fair grading even when students use different wording.  
Instructors can still review or override results when necessary.  
This approach improves automated assessment while keeping human oversight where required.

---

## ⚙️ Make Commands
To make your repo **easy to run and test**, we provide a Makefile:
### Run the API locally
make run

### Run all tests
make test

---

### Static Files (Production)
Static files are generated using: 
 python manage.py collectstatic

## ⚙️ Local Setup (Linux / Windows)

### 1. Clone the repo
git clone https://github.com/nexapytech/django-cbt-platform.git.

cd django-cbt-platform  

### Docker Setup (Recommended)
```bash
docker build -t nexapycbt .
docker run -p 8000:8000 nexapycbt







