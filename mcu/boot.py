from util.process_handler import process_handler

process = process_handler(debug=False)
BOOT_SUCCESS = process.boot()