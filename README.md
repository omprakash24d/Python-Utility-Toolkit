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
git clone [https://github.com/your-username/Python-Utility-Toolkit.git](https://github.com/your-username/Python-Utility-Toolkit.git)
cd Python-Utility-Toolkit
