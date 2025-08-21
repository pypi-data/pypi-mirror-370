# Nexgraph Python library

## Version History

### version 1.0.0
    - Initial beta release.

### version 1.0.1
    - Updated documentation and project URLs.
    - Easier initialization if device path is known.
    - Better error handling.

### verion 1.0.2
    - Minor bug fixes, and code improvement

### version 1.0.3
    - Fixed memory download bug.

### version 2.0.0
    - Removed redundant code, organized and trimmed
    - Better error handling and messages
    - Fixed all code errors and warnings
    - Updated methods and parameters names for clarity
    - Added a bar chart, CSV output for memory downloads

### version 2.1.0
    - Add support for torque testers
    - Add support for devices using a lower baud rate
    - Download method updated:
        - "chart" value for out_format arg removed
        - download(out_format="raw|csv", gen_chart=False|True)
        - Default values ("raw", False)