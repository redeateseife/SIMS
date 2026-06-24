# SIMS | Smart Inventory Management System

## Description
SIMS is an inventory management application built with Python and Streamlit. Features a modular service-layer architecture with inventory tracking, idle-stock analysis, and full CRUD workflows backed by CSV storage.

## Author
Redeate Seife

## Features
- Add, edit, and delete inventory items
- Idle-stock analysis to flag underperforming inventory
- Automatic data backups
- Modular service-layer architecture separating UI from business logic
- Persistent CSV-based data storage
- Configurable theme and design tokens

## Requirements
- Python 3.8+
- Streamlit
- pandas
- Windows, macOS, or Linux

## Installation
```bash
pip install streamlit pandas
```

## Instructions
### Run
```bash
streamlit run app.py
```

## Project Structure
```
SIMS/
    app.py                      Application entry point
    config.py                   App-wide configuration constants
    README.md                   Project documentation

    .streamlit/
        config.toml             Streamlit server and theme settings

    data/
        backups/                Auto-generated inventory backups
        inventory.csv           Primary inventory data store

    services/
        backup_service.py       Handles automatic data backup logic
        inventory_service.py    Core inventory CRUD operations

    ui/
        components.py           Primitives (badges, headers) and tab renderers
        theme.py                Design tokens, apply_theme(), stock status helpers

    utils/
        system_utils.py         OS-level lifecycle utilities (shutdown_server())
```

## Implementation Details
SIMS is built with a modular service-layer architecture that separates concerns across three layers. The UI layer (`ui/`) handles all rendering and user interaction. The service layer (`services/`) contains business logic for inventory operations and backup management, keeping it independent from the UI. The data layer persists state to `inventory.csv`, with automatic backups written to `data/backups/`.

`app.py` serves as the entry point, initializing the Streamlit app, applying the theme via `theme.py`, and routing between tabs. `config.py` centralizes app-wide constants so configuration changes don't require touching business logic or UI files.

## Additional Information
- Tested on Windows 11 and Linux

## Future Improvements
- Database backend (PostgreSQL or SQLite) to replace CSV storage
- User authentication and role-based access control
- Export inventory reports to CSV or PDF
- Low-stock threshold alerts
- Search and filter functionality
- Charts and dashboards for inventory trends

## Demo
#### Windows
![SIMS - Windows](images/sims-windows.png)

#### Linux
![SIMS - Linux](images/sims-linux.png)



