import comtypes.client
import os
import sys

# Path to the IDM Type Library (adjust based on your system architecture)
idm_tlb_path = r"C:\Program Files\Internet Download Manager\idmantypeinfo.tlb"  # For 64-bit
if not os.path.isfile(idm_tlb_path):
    idm_tlb_path = r"C:\Program Files (x86)\Internet Download Manager\idmantypeinfo.tlb"  # For 32-bit

# Load the IDM Type Library
idm = comtypes.client.GetModule(idm_tlb_path)

# Initialize the IDM COM object
idm_obj = comtypes.client.CreateObject(idm.InternetDownloadManager, interface=idm.IInternetDownloadManager)

# Define the download link and save path
download_link = sys.argv[1]
download_path = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()  # Save to the user's Downloads folder

# Add the download link to IDM
idm_obj.AddDownload(
    download_link,  # URL to download
    download_path,  # Save path
    None,           # Referer (optional)
    None,           # Cookies (optional)
    None,           # Post data (optional)
    None,           # User (optional)
    None,           # Password (optional)
    0,              # Flags (optional)
)

print(f"Download link added to IDM: {download_link}")