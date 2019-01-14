from device_registry import app

app.run(host='0.0.0.0', port=80, debug=True)
##  unknown double simultaneous storage bug ( ? werkzeug 0.14 ? )
# solution 1: set debug temporarily to False
# solution 2: mkswap and swapon (4Gb should be fine to add to existing 7.5Gb), set memswap_limit: 12g
