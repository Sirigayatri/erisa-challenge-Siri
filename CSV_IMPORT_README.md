# 📊 CSV Import Guide for ERISA Recovery Claims Management

## Overview
The ERISA Recovery Claims Management system now includes a powerful CSV import feature that allows you to upload claim data with flexible import modes. This feature is accessible through the Django admin interface and provides three different import strategies to meet your data management needs.

## 🚀 Quick Start

### 1. Access CSV Import
- Navigate to the Django admin: `/admin/`
- Click on **"📁 CSV Import"** button in the Quick Actions section
- Or go directly to: `/admin/claims/csv_upload/`

### 2. Prepare Your Files
You need **two CSV files** in pipe-delimited (|) format:

#### Claim List File (`claim_list.csv`)
```
id|patient_name|billed_amount|paid_amount|status|insurer_name|discharge_date
30001|John Doe|1500.00|1200.00|Denied|Aetna|2024-01-15
30002|Jane Smith|2000.00|0.00|Under Review|Blue Cross|2024-01-20
```

#### Claim Detail File (`claim_detail.csv`)
```
30001|30001|Insufficient documentation|99213
30002|30002|N/A|99214,99215
```

**Note:** The claim detail file has NO headers and uses the format: `detail_id|claim_id|denial_reason|cpt_codes`

## ⚙️ Import Modes

### 🧠 Smart Mode (Recommended)
- **What it does:** Updates existing claims and adds new ones
- **Best for:** Regular data updates, maintaining data integrity
- **Safety level:** ⭐⭐⭐⭐⭐ (Safest)

### ➕ Append Mode
- **What it does:** Only adds new claims and details
- **Best for:** Adding new data without modifying existing records
- **Safety level:** ⭐⭐⭐⭐⭐ (Very Safe)

### 🔄 Overwrite Mode
- **What it does:** Replaces ALL existing data with CSV content
- **Best for:** Complete data replacement, fresh starts
- **Safety level:** ⭐ (Use with extreme caution)

## 📋 Step-by-Step Import Process

### Step 1: Upload Files
1. Click **"Choose File"** for Claim List File
2. Select your `claim_list.csv` file
3. Click **"Choose File"** for Claim Detail File
4. Select your `claim_detail.csv` file

### Step 2: Choose Import Mode
- **Smart Mode:** Click on the Smart Mode option (recommended)
- **Append Mode:** Click on the Append Mode option
- **Overwrite Mode:** Click on Overwrite Mode (⚠️ shows warning)

### Step 3: Configure Options
- **Skip confirmation prompts:** Check this box to bypass safety checks
- **Note:** This option is useful for automated imports

### Step 4: Start Import
- Click **"🚀 Start Import"** button
- Wait for the import to complete
- Review the success/error messages

## 🔧 Command Line Usage

You can also use the CSV import from the command line:

```bash
# Smart mode (recommended)
python manage.py load_claims claim_list.csv claim_detail.csv --mode smart

# Append mode
python manage.py load_claims claim_list.csv claim_detail.csv --mode append

# Overwrite mode (with confirmation)
python manage.py load_claims claim_list.csv claim_detail.csv --mode overwrite

# Force mode (skip confirmations)
python manage.py load_claims claim_list.csv claim_detail.csv --mode overwrite --force

# Dry run (see what would happen without importing)
python manage.py load_claims claim_list.csv claim_detail.csv --mode smart --dry-run
```

## 📊 File Format Requirements

### Claim List CSV Format
| Column | Name | Type | Required | Example |
|--------|------|------|----------|---------|
| 1 | id | Integer | Yes | 30001 |
| 2 | patient_name | String | Yes | John Doe |
| 3 | billed_amount | Decimal | Yes | 1500.00 |
| 4 | paid_amount | Decimal | Yes | 1200.00 |
| 5 | status | String | Yes | Denied |
| 6 | insurer_name | String | Yes | Aetna |
| 7 | discharge_date | Date (YYYY-MM-DD) | Yes | 2024-01-15 |

### Claim Detail CSV Format
| Column | Name | Type | Required | Example |
|--------|------|------|----------|---------|
| 1 | detail_id | Integer | Yes | 30001 |
| 2 | claim_id | Integer | Yes | 30001 |
| 3 | denial_reason | String | No | Insufficient documentation |
| 4 | cpt_codes | String | No | 99213,99214 |

**Important Notes:**
- Use pipe (|) as delimiter, not comma
- Dates must be in YYYY-MM-DD format
- Decimal numbers should use period (.) as decimal separator
- Use "N/A" for empty denial reasons (will be converted to empty string)

## 🛡️ Safety Features

### Confirmation Prompts
- **Smart Mode:** Basic confirmation
- **Append Mode:** Basic confirmation
- **Overwrite Mode:** **Strong warning** with confirmation required

### Data Validation
- File format validation
- Data type checking
- Referential integrity (claim details must reference existing claims)
- Error reporting for invalid rows

### Transaction Safety
- All imports use database transactions
- If any part fails, the entire import is rolled back
- No partial data corruption possible

## 📈 Import Statistics

After each import, you'll see detailed statistics:

```
Successfully processed claims data:
  Claims: 150 total, 100 created, 50 updated, 0 skipped
  Details: 150 total, 100 created, 50 updated, 0 skipped
```

## 🚨 Troubleshooting

### Common Issues

#### "File not found" Error
- Ensure both CSV files are uploaded
- Check file extensions (.csv)
- Verify file permissions

#### "Invalid row format" Warnings
- Check delimiter (must be pipe |)
- Verify column count matches expected format
- Ensure no extra commas in text fields

#### "Claim not found" Warnings
- Claim detail references a claim ID that doesn't exist
- Import claim list first, then claim details
- Check for typos in claim IDs

#### Import Fails Completely
- Check CSV format matches requirements exactly
- Verify date formats (YYYY-MM-DD)
- Ensure decimal numbers use periods, not commas
- Check database connection and permissions

### Best Practices

1. **Always backup your data** before large imports
2. **Test with small files** first
3. **Use Smart Mode** for regular updates
4. **Validate CSV format** before uploading
5. **Check import statistics** after completion
6. **Review error messages** for data quality issues

## 🔄 Regular Import Workflow

### Daily Updates
1. Export updated data from your source system
2. Format as pipe-delimited CSV
3. Use **Smart Mode** to update existing claims
4. Review import statistics
5. Verify data in the dashboard

### Monthly Data Refresh
1. Prepare complete dataset
2. Use **Append Mode** to add new claims
3. Use **Smart Mode** to update existing claims
4. Review and validate results

### Complete Data Replacement
1. **⚠️ Backup your database first**
2. Prepare complete new dataset
3. Use **Overwrite Mode** with confirmation
4. Verify all data imported correctly

## 📞 Support

If you encounter issues:
1. Check the error messages in the admin interface
2. Review the command line output for detailed errors
3. Verify your CSV format matches the requirements
4. Check the Django logs for additional error details

## 🎯 Future Enhancements

Planned improvements:
- Excel file support (.xlsx, .xls)
- Drag-and-drop file upload
- Import scheduling
- Email notifications for large imports
- Data validation rules configuration
- Import history and rollback functionality

---

**Happy Importing! 🚀**
