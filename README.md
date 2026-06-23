# APP

## Description
An application for inventory management.

## Author
Redeate Seife | 2026-05-29

## Features
- TBA

## Requirements
- Python 3+
- Windows, macOS, or Linux

## Project Structure
```
red/                            
    app.py                      # Entry point
    config.py                   # Configuration
    README.md                   # Documentation

    .streamlit/                 
        config.toml             # Streamlit application configuration

    data/                       
        backups/                # Backup of inventory data
        inventory.csv           # Inventory data

    services/                    
        backup_service.py       # save_and_backup(inventory) — persistence + timestamped copy
        inventory_service.py    # Inventory class — owns the DataFrame + all mutations/queries
    
    ui/
        components.py           # Primitives (badge, header…) + tab renderers (render_*_tab)
        theme.py                # Design tokens, apply_theme(), stock helpers
    
    utils/                      
        system_utils.py         # shutdown_server() — OS-level lifecycle only
```

## Instructions
```
streamlit run app.py
```



