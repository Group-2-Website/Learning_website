# Learing Website for Kids
## 📝 Application Requirements

---

## Problem

Children often need additional practice outside of school to strengthen their skills in subjects such as vocabulary, mathematics, languages, and science. Traditional worksheets or homework exercises can be repetitive and do not provide immediate feedback or progress tracking.

Parents also want simple ways to support their children’s learning and understand their progress. However, it can be difficult to monitor learning results or provide structured practice at home.

This project aims to provide a simple interactive learning platform where children can practice educational exercises and receive immediate feedback while parents can observe their learning progress.

---

## Scenario

KidsLearn is a browser-based learning application designed for children practicing school subjects at home.

A child opens the application in the browser and selects a learning category such as vocabulary, French, math, or science. The system presents a question or exercise. The child enters an answer and immediately receives feedback indicating whether the answer is correct.

The application stores the results of each exercise. Parents can later review the stored results to understand the child’s learning progress and identify areas that may need more practice.

---

## User stories


1. As a child, I want to choose a learning category (vocabulary, French, math, or science) so that I can practice different subjects.
2. As a child, I want to answer questions and receive immediate feedback so that I know if my answer is correct.
3. As a child, I want the exercises to be simple and interactive so that learning feels engaging and fun.
4. As a child, I want to continue practicing with new questions so that I can improve my knowledge.
5. As a parent, I want to see my child’s learning results so that I can understand their progress.
6. As a parent, I want the exercises to be simple and child-friendly so that my child can learn independently.
7. As a parent, I want the system to store results so that I can review my child’s past performance.

---

### Technology
 
- Python 3.x
- Environment: GitHub Codespaces
- External libraries (NiceGUI, SQLAlchemy, Pydantic)
 
---

### 📂 Repository Structure
   pass
   
## How to Run

### Project Setup
- Create and activate a virtual environment:
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```powershell
      python -m venv .venv
      .venv\Scripts\Activate
      ```
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Launch
- Start the NiceGUI app (example):
   ```bash
   python main.py
   ```
