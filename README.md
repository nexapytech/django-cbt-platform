# NexapyCBT  Django Computer-Based Testing Platform

NexapyCBT is a cutting-edge platform designed to revolutionize the way exams are taken.  
With the flexibility to create, manage, and participate in Computer-Based Tests (CBTs), NexapyCBT provides a seamless, efficient, and secure testing experience for both educators and learners.

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

## NLP & spaCy Integration

NexapyCBT integrates spaCy to enhance evaluation of non-multiple-choice (theory/subjective) questions.

How it works:

Theory answers are processed using text similarity techniques

Student responses are compared with expected answers

spaCy’s pretrained language model enables semantic similarity matching

This allows fair grading even when students use different wording

Instructors can still review or override results when necessary

This approach improves automated assessment while keeping human oversight where required.

## 🛠 Tech Stack

- Python 3.11
- Django
- MySQL
- Docker
- spaCy
- Python Decouple
-spaCy (NLP for text similarity)

## 🐧 Tested On  Linux(recommended)

- Ubuntu 24.04 (Linux)

---

## ⚙️ Local Setup (Linux / Windows)

Follow these steps to run the project locally:

### 1. Clone the repo

```bash
git clone https://github.com/nexapytech/django-cbt-platform.git
cd django-cbt-platform



### Docker Setup (Recommended)
docker build -t nexapycbt .
docker run -p 8000:8000 nexapycbt