# Google Sheets Utilities

A collection of Python utilities for converting between Google Sheets and Excel files, with Google Drive operations.

## 🚀 Features

- **XlsxToGSheets**: Convert Google Sheets to Google Sheets (copying with new names)
- **GSheetToXLSX**: Convert Google Sheets to Excel files (.xlsx)
- **Automatic Folder Creation**: Timestamp-based folder naming in Google Drive
- **Master Sheet Generation**: Automatic creation of index sheets with links
- **Comprehensive Logging**: Detailed logging with file rotation
- **Error Handling**: Robust error handling with fallback options

## 📋 Prerequisites

1. **Python 3.7+**
2. **Google Cloud Project** with Google Drive and Google Sheets APIs enabled
3. **Service Account** with appropriate permissions
4. **Required Python packages** (see Installation section)

## 🛠️ Installation

1. **Clone or download** the utilities to your project
2. **Install dependencies**:
   ```bash
   uv sync
   ```
3. **Set up Google Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Drive and Google Sheets APIs
   - Create a Service Account
   - Download the JSON key file
   - Place it in your project directory

## 🔧 Configuration

### Required Permissions

Your service account needs these scopes:
- `https://www.googleapis.com/auth/drive` - For file operations
- `https://www.googleapis.com/auth/spreadsheets` - For spreadsheet operations

### Service Account Setup

1. **Download your service account JSON file**
2. **Place it in your project directory**
3. **Update the file path** in your code to point to this JSON file


## 🛠️ Step-by-Step: How to Create a Google Service Account and Get the JSON Key

### 🔹 Step 1: Go to Google Cloud Console

* Visit: [https://console.cloud.google.com/](https://console.cloud.google.com/)
* Sign in with your Google account.

---

### 🔹 Step 2: Create a Project (or select an existing one)

* Click the project dropdown in the top left.
* Click **"New Project"**.
* Give it a name (e.g. `XlsxConverterProject`).
* Click **Create**.
* Make sure the new project is **selected**.

---

### 🔹 Step 3: Enable Required APIs

* Go to **APIs & Services > Library**.
* Search and enable:

  * ✅ **Google Drive API**
  * ✅ **Google Sheets API**

---

### 🔹 Step 4: Create a Service Account

* Go to **IAM & Admin > Service Accounts**
* Click **“+ CREATE SERVICE ACCOUNT”**
* Fill in:

  * **Service account name** (e.g. `xlsx-converter`)
  * Click **Create and Continue**

**Grant the account basic access** (optional for now):

* Click **Done** (no roles needed yet — we'll handle permissions separately)

---

### 🔹 Step 5: Create and Download the JSON Key

* After creating the service account, click on its name.
* Go to the **"Keys"** tab.
* Click **"Add Key" > "Create new key"**
* Choose **JSON**, then click **Create**
* A `.json` file will download to your computer (this is the key file you’ll use in your script).

> **Important**: Keep this file safe and never expose it publicly.

---

### 🔹 Step 6: Get the Service Account Email

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Make sure your project is selected.

3. Navigate to:
   **IAM & Admin > Service Accounts**
   (or search “Service Accounts” in the top bar)

4. You’ll see a list of your service accounts.
   Click on the name of the one you created (e.g. `xlsx-converter`).

5. On the **details page**, you’ll see something like this:

   ```
   Service account ID:
   xlsx-converter@your-project-id.iam.gserviceaccount.com
   ```

✅ **Copy this email** — it's the service account's identity.

---


### 🔹 Step 7: Create a shared Google Drive

On Google Drive mainpage:

1. Click on **"Shared Drives"**.
2. Then, click on **"+ New"**.
3. Set a name to your new drive and click **"Create"**.
4. Then, click on the name of you shared drive.
5. Click on "Manage Members".
4. Paste the service account email (e.g. `my-service-account@your-project-id.iam.gserviceaccount.com`)
5. Give it **Content Manager** access at least and click on **"Share"**.

Now your service account has permission to write files to that Drive.

---

## 📚 Usage

### XlsxToGSheets - Google Sheets to Google Sheets

This class copies Google Sheets from URLs found in a master sheet and creates new copies in a target folder:

```python
from urarovite.utils.xlsx_to_gsheets import XlsxToGSheets

converter = XlsxToGSheets(
    service_account_file="path/to/service-account.json",
    src_master_sheet_url="https://docs.google.com/spreadsheets/d/...",
    shared_drive_id="shared_drive_id",
    url_column_nr=2,  # Column containing URLs (0-indexed)
    base_folder_name="My Sheet Conversion",
    dest_master_sheet_name="Master Sheet"
)

converter.run()
```

### GSheetToXLSX - Google Sheets to Excel

This class exports Google Sheets to Excel (.xlsx) files in Google Drive:

```python
from urarovite.utils.gsheets_to_xlsx import GSheetToXlsx

exporter = GSheetToXlsx(
    service_account_file="path/to/service-account.json",
    src_master_sheet_url="https://docs.google.com/spreadsheets/d/...",
    shared_drive_id="shared_drive_id",
    url_column_nr=2,  # Column containing URLs (0-indexed)
    base_folder_name="My Excel Export",
    dest_master_sheet_name="Master Sheet"
)

exporter.run()
```

## ⚙️ Parameters

### XlsxToGSheets Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_account_file` | str | Yes | Path to service account JSON file |
| `src_master_sheet_url` | str | Yes | URL of the master sheet containing URLs to convert |
| `shared_drive_id` | str | Yes | Shared Drive ID for shared drive operations |
| `url_column_nr` | int | No | Column number containing URLs (0-indexed, default=2) |
| `base_folder_name` | str | No | Base name for target folder (default="XlsxToGSheets") |
| `dest_master_sheet_name` | str | No | Name for destination master sheet (default="Master Sheet") |

### GSheetToXLSX Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_account_file` | str | Yes | Path to service account JSON file |
| `src_master_sheet_url` | str | Yes | URL of the master sheet containing URLs to export |
| `shared_drive_id` | str | Yes | Shared Drive ID for shared drive operations |
| `url_column_nr` | int | No | Column number containing URLs (0-indexed, default=2) |
| `base_folder_name` | str | No | Base name for target folder (default="GSheetToXlsx") |
| `dest_master_sheet_name` | str | No | Name for destination master sheet (default="Master Sheet") |

## 📝 Logging

All operations are logged to both console and log files:

- **Console Output**: Real-time progress and status updates
- **Log Files**: Stored in `logs/` directory with timestamps
- **Log Rotation**: Automatic log file management

## 🔍 Troubleshooting

### Common flags

1. **Authentication Errors**
   - Verify service account JSON file path
   - Check API permissions and scopes
   - Ensure Google Drive/Sheets APIs are enabled

2. **Permission Errors**
   - Verify service account has access to target folders
   - Check shared drive permissions if using shared drives

3. **URL Parsing Errors**
   - Ensure master sheet URLs are valid Google Sheets URLs
   - Check that URLs in the specified column are properly formatted
   - Verify HYPERLINK formulas are correctly formatted

4. **Rate Limiting**
   - Google APIs have rate limits
   - Add delays between operations if processing many files

## 📋 How It Works

Both classes follow a similar workflow:

1. **Read Master Sheet**: Extract URLs from a specified column in a master Google Sheet
2. **Create Target Folder**: Generate a timestamped folder in Google Drive
3. **Process Files**: 
   - **XlsxToGSheets**: Copy Google Sheets to new locations
   - **GSheetToXLSX**: Export Google Sheets as Excel (.xlsx) files
4. **Generate Master Sheet**: Create an index sheet with links to all processed files
5. **Log Results**: Provide detailed logging of all operations

---

## 📁 DriveFolderDownloader

The `DriveFolderDownloader` class allows you to download entire Google Drive folders with their structure preserved. This is useful for backing up shared folders, migrating data, or creating local copies of cloud-stored files.

### Basic Usage

```python
from urarovite.utils.download_drive_folder import DriveFolderDownloader

# Initialize the downloader
downloader = DriveFolderDownloader(
    service_account_file="path/to/your/service-account.json",
    folder_id="your_google_drive_folder_id_here",
    local_download_path="./downloads",
    base_folder_name="MyDriveBackup"
)

# Run the download
success = downloader.run()
if success:
    print("Download completed successfully!")
else:
    print("Download completed with some errors. Check the log for details.")
```

### Advanced Configuration

```python
# More advanced configuration with filtering
downloader = DriveFolderDownloader(
    service_account_file="path/to/your/service-account.json",
    folder_id="your_google_drive_folder_id_here",
    local_download_path="./downloads",
    base_folder_name="FilteredDownload",
    preserve_structure=True,
    file_types_to_download=[
        "application/vnd.google-apps.spreadsheet",        # Google Sheets
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
        "application/vnd.google-apps.document",           # Google Docs
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
        "application/vnd.google-apps.presentation",       # Google Slides
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # PPTX
        "text/csv",                                       # CSV files
        "application/pdf"                                 # PDF files
    ],
    max_file_size_mb=100  # Skip files larger than 100MB
)
```

### Getting Your Google Drive Folder ID

1. **From the URL**: When you open a Google Drive folder in your browser, the URL will look like:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```
   Copy the `FOLDER_ID_HERE` part.

2. **From the folder**: Right-click on the folder in Google Drive and select "Get link". The link will contain the folder ID.

### DriveFolderDownloader Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_account_file` | str | Yes | Path to service account JSON file |
| `folder_id` | str | Yes | Google Drive folder ID to download |
| `local_download_path` | str | No | Local directory to save downloaded files (default="./downloads") |
| `base_folder_name` | str | No | Base name for the download folder (default="DriveFolderDownload") |
| `preserve_structure` | bool | No | Whether to maintain folder hierarchy (default=True) |
| `file_types_to_download` | List[str] | No | List of MIME types to download (None = all) |
| `max_file_size_mb` | int | No | Maximum file size to download in MB (default=100) |

### Features

- **Recursive Download**: Downloads entire folder hierarchies
- **File Type Filtering**: Download only specific file types
- **Size Limits**: Skip files that are too large
- **Google Workspace Support**: Converts Google Docs/Sheets/Slides to Office formats
- **Progress Logging**: Detailed logs and progress tracking
- **Download Reports**: Summary reports of all operations
- **Error Handling**: Graceful handling of permission and network flags

### File Type Support

The downloader supports various file types and automatically converts Google Workspace files:

| Google Workspace Format | Converted To | MIME Type |
|------------------------|---------------|-----------|
| Google Sheets | XLSX | `application/vnd.google-apps.spreadsheet` |
| Google Docs | DOCX | `application/vnd.google-apps.document` |
| Google Slides | PPTX | `application/vnd.google-apps.presentation` |
| XLSX Files | XLSX (direct) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PDF Files | PDF (direct) | `application/pdf` |
| CSV Files | CSV (direct) | `text/csv` |

### Output Structure

The downloader creates a timestamped folder structure:

```
downloads/
└── DriveFolderDownload_20241201_143022/
    ├── file1.xlsx
    ├── subfolder/
    │   ├── file2.docx
    │   └── file3.pdf
    └── download_report.txt
```

The `download_report.txt` contains a summary of all operations, including:
- Download date and time
- Source folder information
- Count of downloaded, skipped, and failed files
- Detailed list of all operations
- Error details for failed downloads

### Troubleshooting DriveFolderDownloader

**Common flags and Solutions:**

1. **"Folder not found" error**:
   - Verify the folder ID is correct
   - Ensure the service account has access to the folder
   - Check if the folder is shared with the service account

2. **"Access forbidden" error**:
   - Verify the service account has the correct permissions
   - Check if the folder is in a shared drive that requires special access
   - Ensure the Google Drive API is enabled in your project

3. **No files returned**:
   - The folder might be empty
   - Check if files are in subfolders
   - Verify the service account can see the folder contents

4. **Large file downloads fail**:
   - Increase the `max_file_size_mb` parameter
   - Check your internet connection stability
   - Consider downloading large files individually