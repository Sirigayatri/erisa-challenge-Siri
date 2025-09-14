
# ERISA Recovery – Claims Management Dashboard  

A Django-based web application to manage healthcare claims and track underpayments.  

🔗 **Live Demo:** [sirigayatri16.pythonanywhere.com](https://sirigayatri16.pythonanywhere.com/)  
💻 **GitHub Repo:** [erisa-challenge-Siri](https://github.com/Sirigayatri/erisa-challenge-Siri)  


## Overview

This is a web-based application built with Django that helps manage healthcare claims and track underpayments. The system allows users to view, filter, and manage claims data with an intuitive dashboard interface.

## What This System Does

- **Claims Management**: View and manage healthcare claims in a table format
- **Data Filtering**: Filter claims by insurer, status, and flagged items
- **Search Functionality**: Search through claims using patient names, claim IDs, or insurer names
- **Status Tracking**: Track claim statuses (Denied, Paid, Under Review, Underpaid)
- **Flagging System**: Mark important claims for follow-up
- **Notes System**: Add notes to individual claims
- **CSV Upload**: Upload new claims data from CSV files
- **Analytics Report**: Interactive charts and data visualizations
- **Report Generation**: Generate comprehensive reports for analysis

## Technical Requirements

- Python 3.8 or higher
- Django 4.2.7
- SQLite database
- Modern web browser
- Chart.js (loaded via CDN for report page only)

## Installation

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd erisa_recovery
   ```

2. **Create a virtual environment**
   ```
python -m venv .venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```
.venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
source .venv/bin/activate
```

4. **Install dependencies**
   ```
   pip install django
   ```

5. **Run database migrations**
   ```
python manage.py migrate
```

6. **Load sample data**
   ```
   python manage.py load_claims
   ```

7. **Start the development server**
   ```
python manage.py runserver
```

8. **Open your browser**
   Navigate to `http://127.0.0.1:8000`



## 🖼 Screenshots

<img width="1920" height="1080" alt="dashboard" src="https://github.com/user-attachments/assets/3284faa9-3387-406b-a699-b230f39301e2" />




<img width="1920" height="1080" alt="report" src="https://github.com/user-attachments/assets/b6562efc-71e1-4cab-9c14-8c2c8f7e7075" />


## Project Structure


erisa_recovery/
├── database/                 # Database models and migrations
│   ├── models.py            # Claim, ClaimDetail, Flag, Note models
│   ├── migrations/          # Database migration files
│   └── management/          # Custom Django commands
├── frontend/                # Frontend templates and static files
│   ├── templates/           # HTML templates
│   │   └── claims/          # Claims-specific templates
│   │       ├── dashboard.html  # Main dashboard
│   │       └── report.html     # Analytics report page
│   └── static/              # CSS and JavaScript files
│       ├── css/
│       │   ├── dashboard-system.css  # Main dashboard styles
│       │   └── report.css            # Report page styles
│       └── js/
│           └── report.js             # Chart.js for report page only
├── backend/                 # Backend views and URL routing
│   ├── views.py             # Main application views
│   ├── urls.py              # URL patterns
│   └── admin.py             # Django admin configuration
├── erisa_recovery/          # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   └── production_settings.py
├── claim_list_data.csv      # Sample claims data
├── claim_detail_data.csv    # Sample claim details data
├── requirements.txt         # Python dependencies
└── manage.py                # Django management script


## Key Features

### Dashboard Interface
- Clean, modern design with a search bar and filter options
- Claims table showing all relevant information
- Status sidebar for quick filtering
- Responsive layout that works on different screen sizes

### Filtering System
- **Insurer Filter**: Filter by insurance companies (Aetna, Blue Cross, Cigna, etc.)
- **Status Filter**: Filter by claim status (Denied, Paid, Under Review, Underpaid)
- **Flagged Filter**: Show only flagged claims that need attention
- **Search**: Real-time search across claim IDs, patient names, and insurers

### Data Management
- **CSV Upload**: Upload new claims data from CSV files
- **Smart Merge**: Preserves existing user data (flags, notes) when uploading new data
- **Data Validation**: Ensures data integrity and proper formatting

### User Interactions
- **Flagging**: Mark important claims for follow-up
- **Notes**: Add detailed notes to individual claims
- **Status Updates**: Track claim status changes
- **Export**: Generate reports for analysis

### Analytics Report Page
- **Interactive Charts**: Three Chart.js visualizations
  - Claims by Status (Doughnut Chart)
  - Billed vs Paid by Insurer (Grouped Bar Chart)
  - Average Underpayment by Insurer (Horizontal Bar Chart)
- **Financial Summary**: Key metrics and totals
- **Top Underpayments**: Table of highest underpayment cases
- **Analysis Summary**: Flagged claims, notes, and averages
- **Responsive Design**: Works on desktop, tablet, and mobile

## Database Models

### Claim
- Primary model storing claim information
- Fields: claim_id, patient_name, insurer, status, billed_amount, paid_amount, underpayment
- Relationships: One-to-many with ClaimDetail, Flag, and Note

### ClaimDetail
- Additional claim information
- Fields: claim, description, date_of_service, provider
- Foreign key relationship to Claim

### Flag
- Mark claims for special attention
- Fields: claim, reason, created_at
- Foreign key relationship to Claim

### Note
- Add comments and observations
- Fields: claim, content, created_at
- Foreign key relationship to Claim

## API Endpoints

- `/` - Main dashboard
- `/report/` - Analytics report page with interactive charts
- `/csv_upload/` - CSV file upload endpoint
- `/flag_claim/<claim_id>/` - Flag a claim
- `/unflag_claim/<claim_id>/` - Remove flag from claim
- `/add_note/<claim_id>/` - Add note to claim
- `/delete_note/<note_id>/` - Delete a note

## Technical Implementation

### Frontend Architecture
- **Main Dashboard**: Pure Django templates with minimal CSS/JavaScript
- **Report Page**: Django templates + Chart.js for interactive visualizations
- **Responsive Design**: CSS Grid and Flexbox for modern layouts
- **Font Consistency**: Inter font family throughout the application

### JavaScript Usage
- **Dashboard**: No JavaScript required - follows challenge requirements
- **Report Page Only**: Chart.js for interactive charts and data visualizations
- **CDN Loading**: Chart.js loaded dynamically to avoid affecting main dashboard performance

### Backend Architecture
- **Django Views**: Server-side rendering for all pages
- **Database ORM**: Efficient queries with aggregation and filtering
- **API Endpoints**: RESTful endpoints for AJAX operations
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## Configuration

### Settings
- Database: SQLite (default)
- Static files: Served from frontend/static/
- Templates: Located in frontend/templates/
- Debug mode: Enabled for development

### Environment Variables
No additional environment variables required for basic functionality.

## Usage

### Viewing Claims
1. Open the dashboard in your browser
2. Use the search bar to find specific claims
3. Apply filters to narrow down results
4. Click on claim rows to view details

### Managing Claims
1. **Flag a claim**: Click the flag icon next to any claim
2. **Add notes**: Click the notes icon and enter your comment
3. **Filter flagged claims**: Use the "Show Flagged Only" checkbox

### Uploading Data
1. Click the "Upload CSV" button
2. Select your CSV file
3. The system will automatically process and merge the data
4. Existing flags and notes will be preserved

### Viewing Analytics Report
1. Click the "Generate Report" button on the dashboard
2. View interactive charts showing:
   - Claims distribution by status
   - Billed vs paid amounts by insurer
   - Average underpayment analysis
3. Review financial summary and top underpayments
4. Charts are responsive and work on all devices

## Troubleshooting

### Common Issues

1. **No data showing**: Run `python manage.py load_claims` to load sample data
2. **Filter not working**: Check browser console for JavaScript errors
3. **CSV upload failing**: Ensure CSV file has correct format and column headers
4. **Database errors**: Run `python manage.py migrate` to apply migrations

### Getting Help

If you encounter issues:
1. Check the Django console for error messages
2. Verify all dependencies are installed
3. Ensure database migrations are applied
4. Check file permissions for uploads

## Development

### Adding New Features
1. Create new models in `database/models.py`
2. Run migrations: `python manage.py makemigrations` and `python manage.py migrate`
3. Add views in `backend/views.py`
4. Update URL patterns in `backend/urls.py`
5. Create templates in `frontend/templates/`

### Code Style
- Follow Django best practices
- Use meaningful variable and function names
- Add comments for complex logic
- Keep templates clean and readable

## License

This project is part of the ERISA Recovery Dev Challenge and is intended for demonstration purposes.

## Copyright

**Developer:** Siri Gayatri Chodavarapu  
**Email:** sirigayatri16@gmail.com

## License
This project is licensed for **demonstration purposes only** as part of the ERISA Recovery Dev Challenge.


=======

