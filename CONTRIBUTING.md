# Noita Savior Development Setup

## Prerequisites
- Python 3.7 or higher
- Git (for version control)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd NoitaSavior
   ```

2. Install dependencies (none required - uses only Python standard library):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run.py
   # or
   python src/nsav.py
   ```

## Development

### Code Structure
- `src/nsav.py` - Main application code
- `run.py` - Entry point script
- `backups/` - Created automatically for save data
- `slots.json` - Created automatically for slot metadata

### Testing
The application includes built-in error handling and status reporting.
Check the console output for debugging information.

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
GNU General Public License v3.0 - see LICENSE file for details.
