# E-Health: Legacy System Enhancement Project

This project is a Django-based healthcare application designed to demonstrate the integration of machine learning into a legacy system. I cloned this repository as a learning exercise to analyze existing codebases, refactor inefficient patterns, and implement new, value-driven features.

The application allows patients to register, predict their diabetes status based on health indicators, and track their medical history.

## Project Journey & Enhancements

As part of my professional development, I performed the following enhancements to the original system:

### 1. Architectural Refactoring (ML Flow)
- **Problem**: The original system re-trained the machine learning model on every prediction request, causing significant latency and server-side overhead.
- **Solution**: Decoupled the training logic. I implemented a Django management command to handle model training asynchronously, ensuring the web application remains fast and responsive by only loading pre-trained models.

### 2. Role-Based Access Control (RBAC)
- **Added**: A specialized **Doctor Dashboard** to provide a clinical view of patient metrics.
- **Feature**: Dynamic user experiences where the interface adapts based on whether the user is a Patient or a healthcare provider (Staff/Doctor).

### 3. Data Visualization & Health Insights
- **Added**: Interactive health trend charts using Chart.js.
- **Goal**: To provide patients with visual feedback on their health markers (like BMI and Glucose) over time, moving beyond simple tabular data.

## Features

- **Diabetes Risk Prediction**: Utilizes a Scikit-learn model trained on clinical health indicators.
- **Secure Medical History**: Patients can securely view and download their assessment history in PDF/CSV formats.
- **Clinical Oversight**: Staff can monitor patient health trends and latest assessments via a dedicated dashboard.

## Technical Stack

- **Backend**: Django (Python)
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **Frontend**: Bootstrap 5, Javascript, Chart.js
- **Reporting**: ReportLab (PDF generation)

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd E-Health-Django-Machine-Learning
   ```

2. **Environment Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Initialize Application**:
   - Create a `secret_key.txt` file in the root directory and paste a Django secret key.
   - Run migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```
   - Train the ML model:
     ```bash
     python manage.py train_model
     ```

4. **Run Server**:
   ```bash
   python manage.py runserver
   ```
   Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---
*Note: This project was enhanced as an exercise in software maintenance, performance optimization, and UI/UX design.*