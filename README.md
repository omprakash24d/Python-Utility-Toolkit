# Python-Utility-Toolkit

A collection of useful Python scripts designed to simplify common daily tasks.

---

### Duplicate File Finder

The first tool in this toolkit is a powerful and flexible **Duplicate File Finder**. It helps you identify and manage duplicate files on your computer to free up valuable disk space.

#### Features

* **Two-Pass Scan:** A highly efficient two-pass system that first groups files by size before using multiprocessing to hash potential duplicates.
* **Multiprocessing:** Utilizes all available CPU cores to perform hashing, ensuring fast performance on large directories.
* **Flexible CLI & Interactive Mode:** Run the tool with command-line arguments for automation or use the guided, interactive prompt for a user-friendly experience.
* **Safe Deletion:** Offers a `dry-run` mode to preview which files will be deleted and requires user confirmation on a per-group basis before removal.
* **Detailed Reporting:** Generates a CSV report of all found duplicates for further analysis.

#### How to Use

**1. Clone the Repository**

```bash
git clone https://github.com/omprakash24d/Python-Utility-Toolkit.git
cd Python-Utility-Toolkit
````

**2. Run the Script**

You can run the tool in two ways:

  * **Interactive Mode (User-Friendly):**
    Simply run the script with no arguments. It will guide you through the process.

    ```bash
    python duplicates.py
    ```

  * **Command-Line Interface (CLI):**
    Use the following arguments for more control:

    ```bash
    python duplicates.py [path] [-o OUTPUT] [-d] [--dry-run] [--hash-algo {md5,sha256}]
    ```

    **Example:**

    ```bash
    # Scan a folder and save the report
    python duplicates.py "C:\Users\YourName\Documents" -o duplicate_files_report.csv

    # Scan and run a dry-run for deletion
    python duplicates.py "C:\Users\YourName\Desktop" --delete --dry-run
    ```

#### Upcoming Tools

This repository will be expanded with more useful scripts, including:

  - Automated File Organizer
  - Personal Finance Tracker

Stay tuned for more updates\!

-----

### Contributions

If you have an idea for a useful tool or an improvement to an existing one, feel free to open an issue or submit a pull request.
