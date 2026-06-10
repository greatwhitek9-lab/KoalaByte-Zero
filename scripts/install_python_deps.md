# Install Python Dependencies

Follow the steps below to set up Python and install required dependencies for the project.

---

### Step 1: Update Package Lists
Ensure your package lists are up-to-date:
```bash
sudo apt-get update
```

---

### Step 2: Install Required System Packages
Install `pip` and Python development libraries required for the project:
```bash
sudo apt-get install -y python3-pip python3-dev
```

---

### Step 3: Install Python Dependencies
1. Navigate to the project directory that contains `requirements.txt`:
   ```bash
   cd /path/to/project
   ```
2. Install dependencies from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the Arducam library required for the IMX708 camera module:
   ```bash
   pip install arducam-py==1.0.3
   ```

---

### Optional: Use a Virtual Environment
To prevent dependency conflicts, it's recommended to use a virtual environment:
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install the dependencies within the virtual environment:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the Arducam library:
   ```bash
   pip install arducam-py==1.0.3
   ```

### Troubleshooting
- **Missing `requirements.txt`:**
   If the `requirements.txt` file isn't present, create one by listing all project dependencies. You can generate it using:
   ```bash
   pip freeze > requirements.txt
   ```
- **Permissions Issues with `pip`:**
   If you encounter issues, try:
   ```bash
   python3 -m pip install --upgrade pip
   ```

---
