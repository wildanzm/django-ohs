# PPE & Temperature Detection Attendance System

This web application is a research prototype designed to automatically detect Personal Protective Equipment (PPE) and body temperature when an employee checks in. The system uses a machine learning model for real-time image processing to ensure workplace safety compliance.

## 🚀 Key Features

-   **Functional Admin Panel:** A customized Django admin interface to manage employees, PPE types, and attendance records.
-   **PPE Detection:** Utilizes a YOLOv8 model to detect `Hardhat`, `Mask`, and `Safety Vest` from images.
-   **Face & Temperature Detection:** Employs an OpenCV DNN model for face detection, which serves as the basis for a simulated temperature check.
-   **Data Management:** Full CRUD (Create, Read, Update, Delete) capabilities for all data through the admin panel.
-   **Responsive Design:** The front-end is styled with Bootstrap 5 for a clean and responsive user experience.

## 🛠️ Tech Stack

-   **Backend:** Django
-   **Database:** MySQL
-   **Machine Learning:** PyTorch, YOLOv8, OpenCV
-   **Frontend:** HTML, CSS, Bootstrap 5

## ⚙️ Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

-   Python 3.8+
-   PIP & Venv
-   MySQL Database Server

### 2. Installation Guide

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/wildanzm/django-ohs.git
    cd django-ohs
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the venv
    python -m venv venv

    # Activate on macOS/Linux
    source venv/bin/activate
    
    # Activate on Windows
    .\venv\Scripts\activate
    ```

3.  **Install all dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    -   Create a new file named `.env` in the project's root directory.
    -   Add the following configuration, replacing the placeholder values with your actual credentials.
        ```env
        SECRET_KEY='replace_with_a_strong_and_unique_secret_key'
        DEBUG=True
        DATABASE_URL='mysql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME'
        ```
        Example `DATABASE_URL`: `mysql://user:password@127.0.0.1:3306/db_name`

5.  **Database Setup:**
    -   Ensure you have created an empty database in MySQL that matches the name in your `.env` file.

6.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Create a Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create your admin username and password.

8.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```

### 3. Usage

-   **Admin Panel:** Access the admin interface at `http://127.0.0.1:8000/admin/` to manage all application data.
-   **Main Dashboard:** Visit `http://127.0.0.1:8000/` to see the main application dashboard.