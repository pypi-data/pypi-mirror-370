# 🎓 UMAT Kit - Complete Student Portal Toolkit

[![PyPI version](https://badge.fury.io/py/umat-kit.svg)](https://badge.fury.io/py/umat-kit)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**UMAT Kit** is a comprehensive Python toolkit designed for UMAT (University of Mines and Technology) students to interact with the student portal programmatically. It provides a rich CLI interface, automated course assessment bot, API client, and utilities for seamless student portal management.

## ✨ Features

### 🤖 **Automated Course Assessment Bot**
- **Smart Rating System**: Automatically rates courses with realistic scores (3-5 range)
- **Bulk Submission**: Submit all course assessments at once (matches web interface)
- **Manual Mode**: Course-by-course assessment with full control
- **Progress Tracking**: Real-time progress indicators and success statistics

### 📊 **Academic Management**
- **Results Viewer**: View current and historical academic results
- **GPA Calculator**: Automatic GPA and CGPA calculations
- **Transcript Export**: Download and export academic transcripts

### 💰 **Financial Management**
- **Bills Overview**: View outstanding fees and payment history
- **Payment Tracking**: Monitor payment status and due dates
- **Fee Breakdown**: Detailed breakdown of all charges

### 📚 **Course Management**
- **Registration Status**: View registered courses and schedules
- **Course Details**: Access detailed course information
- **Assessment Progress**: Track course assessment completion

### 👤 **Profile Management**
- **Profile Updates**: Update contact information and email
- **Session Management**: Secure authentication and session handling
- **Data Export**: Export personal and academic data

### 🖥️ **Rich CLI Interface**
- **Interactive Menus**: Beautiful, intuitive command-line interface
- **Progress Bars**: Visual feedback for long-running operations
- **Colored Output**: Rich formatting with emojis and colors
- **Error Handling**: Graceful error handling with helpful messages

## 🚀 Installation

### Install from PyPI (Recommended)
```bash
pip install umat-kit
```

### Install from Source
```bash
git clone https://github.com/yourusername/umat-kit.git
cd umat-kit
pip install -e .
```

## 🎯 Quick Start

### CLI Interface
```bash
# Launch the interactive CLI
umat-kli ui

# Direct login
umat-kli login --username your_student_id

# View help
umat-kli --help
```

### Python API
```python
from umat_kit.student_portal import StudentPortal

# Initialize portal
portal = StudentPortal()

# Login
portal.login("your_student_id", "your_password")

# Get academic results
results = portal.get_academic_results()
print(f"Current GPA: {results['current_gpa']}")

# Automated course assessment
portal.automated_course_assessment()

# View bills
bills = portal.get_student_bills()
```

## 🤖 Automated Course Assessment

The standout feature of UMAT Kit is the **Automated Course Assessment Bot**:

```python
# Quick automated assessment
portal.automated_course_assessment()
```

**What it does:**
- 🎯 Finds all pending course assessments
- 🎲 Generates realistic random ratings (3-5: Average to Very Good)
- 📝 Applies optional general comments to all courses
- 📦 Submits all assessments in one bulk request (matches web interface)
- 📊 Provides detailed success statistics

**Assessment Flow:**
```
🤖 Automated Course Assessment
📚 Found 8 pending courses
🎲 Generating random ratings...
📊 Assessment Summary:
┌─────────┬──────────────────────┬───────────┬─────────────┐
│ Course  │ Course Name          │ Questions │ Avg Rating  │
├─────────┼──────────────────────┼───────────┼─────────────┤
│ CS 101  │ Programming Basics   │    21     │   4.2/5.0   │
│ MA 201  │ Advanced Mathematics │    21     │   3.8/5.0   │
└─────────┴──────────────────────┴───────────┴─────────────┘

✅ All assessments submitted successfully!
📈 Success Rate: 100% (8/8 courses)
```

## 📋 Available Commands

### CLI Commands
```bash
# Authentication
umat-kli login                    # Interactive login
umat-kli logout                   # Logout current session

# Academic
umat-kli results                  # View academic results
umat-kli courses                  # View registered courses

# Assessment
umat-kli assess                   # Launch course assessment
umat-kli assess --auto            # Automated assessment
umat-kli assess --manual          # Manual assessment

# Financial
umat-kli bills                    # View bills and payments

# Profile
umat-kli profile                  # View/update profile
umat-kli profile --update-email   # Update email address

# Utilities
umat-kli export --results         # Export academic results
umat-kli export --bills           # Export financial data
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in your project directory:

```env
# Optional: Auto-login credentials
UMAT_USERNAME=your_student_id
UMAT_PASSWORD=your_password

# Optional: API Configuration
UMAT_API_TIMEOUT=30
UMAT_MAX_RETRIES=3
```

### Configuration File
```python
# config.py
UMAT_CONFIG = {
    'api_base_url': 'https://student.umat.edu.gh/api',
    'timeout': 30,
    'max_retries': 3,
    'auto_assessment_range': (3, 5),  # Rating range for auto assessment
}
```

## 🛡️ Security Features

- **🔐 Secure Authentication**: Encrypted credential storage
- **🔒 Session Management**: Automatic session timeout and renewal
- **🛡️ Data Protection**: Secure handling of sensitive student data
- **🚫 Rate Limiting**: Built-in API rate limiting to prevent abuse

## 📊 API Reference

### StudentPortal Class
```python
class StudentPortal:
    def login(username: str, password: str) -> bool
    def get_academic_results() -> Dict[str, Any]
    def get_student_bills() -> Dict[str, Any]
    def get_registered_courses() -> Dict[str, Any]
    def automated_course_assessment(comment: str = "") -> Dict[str, Any]
    def manual_course_assessment() -> None
    def update_profile(data: Dict[str, Any]) -> bool
    def export_data(data_type: str, format: str = "json") -> str
```

### API Manager
```python
class APIManager:
    def submit_all_course_assessments(assessments: List[Dict], remarks: str) -> Dict
    def get_course_assessments() -> Dict[str, Any]
    def get_academic_results() -> Dict[str, Any]
    def get_student_bills() -> Dict[str, Any]
```

## 🎨 Examples

### Automated Assessment with Custom Comments
```python
from umat_kit.student_portal import StudentPortal

portal = StudentPortal()
portal.login("your_id", "your_password")

# Automated assessment with custom comment
result = portal.automated_course_assessment(
    comment="Great semester! Learned a lot from all courses."
)

print(f"✅ Assessed {result['courses_submitted']} courses")
print(f"📊 Success Rate: {result['success_rate']}%")
```

### Export Academic Data
```python
# Export results to JSON
results_file = portal.export_data("results", format="json")
print(f"Results exported to: {results_file}")

# Export bills to CSV
bills_file = portal.export_data("bills", format="csv")
print(f"Bills exported to: {bills_file}")
```

### Batch Operations
```python
# Check multiple students (if you have admin access)
students = ["student1", "student2", "student3"]
for student_id in students:
    portal.login(student_id, get_password(student_id))
    portal.automated_course_assessment()
    portal.logout()
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/yourusername/umat-kit.git
cd umat-kit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](https://umat-kit.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/umat-kit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/umat-kit/discussions)

## 🎯 Roadmap

- [ ] **Mobile App Integration**: React Native/Flutter companion app
- [ ] **Telegram Bot**: Interactive Telegram bot interface
- [ ] **Web Dashboard**: Web-based dashboard for portal management
- [ ] **Notification System**: Email/SMS notifications for important updates
- [ ] **Analytics**: Advanced analytics and reporting features
- [ ] **Multi-University Support**: Extend support to other universities

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/umat-kit&type=Date)](https://star-history.com/#yourusername/umat-kit&Date)

---

**Made with ❤️ for UMAT students by students**

*Simplifying student life, one API call at a time.* 🚀