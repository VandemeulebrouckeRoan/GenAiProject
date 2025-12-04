# AI Career Coach – Roan Task Overview

This markdown file summarizes **exactly what you (Roan)** need to do to start the AI Career Coach project.

---

## ✅ Your Responsibilities (From the Project Proposal)

### **1. Data Collection & Processing**

You are responsible for collecting and preparing the data needed for both the RAG system and the fine-tuning process.

You need:

* **20–30 job descriptions** (software engineer, marketing, HR, finance, etc.)
* **10–20 CV samples or bullet points**
* **A skills taxonomy** (public skill list such as ESCO)

These will be stored in:

```
data/job_descriptions/
data/cv_samples/
data/skills_taxonomy/
```

---

## ✅ 2. Build the Interview Practice Module

This is your main technical task.

You will build a small module that:

* Takes a **job title or job description** as input
* Generates **5 interview questions**
* Generates example answers using **STAR structure**

The module will later integrate into the system but for now can be a simple Python script.

Suggested folder:

```
interview_module/generator.py
```

Basic functions:

* `generate_questions(job_title)`
* `generate_star_answers(questions)`

---

## ✅ 3. Help With Evaluation & Testing (Shared)

Later in the project, both you and Robin will:

* Test rewritten CV bullet points
* Test interview questions
* Run small user surveys
* Collect feedback from students or recruiters

This will be done after the first prototype works.

---

# 📌 What You Should Do First

### **1️⃣ Create the data folders**

```
mkdir -p data/job_descriptions
mkdir -p data/cv_samples
mkdir -p data/skills_taxonomy
```

### **2️⃣ Collect data and put it into the folders**

* Copy/paste job descriptions into `.txt` files
* Add CV bullet points into `.txt` files
* Add a skill list into the taxonomy folder

### **3️⃣ Start creating the Interview Generator**

You can ask ChatGPT to generate the Python script for you.

---

# 🎯 Simple To-Do List

* [ ] Create data folder structure
* [ ] Add 20–30 job descriptions
* [ ] Add 10–20 CV bullet points
* [ ] Add a skills taxonomy file
* [ ] Create `generator.py` for interview Q&A

---

If you want, I can generate:

* Starter Python files
* Folder structure
* The interview generator code
* The prompts for Q&A

Just ask: **"Generate the starter code"**.
