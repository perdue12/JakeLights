# Flash instructions for ESP32
Use the following line to flash the esp32
esptool.py --chip esp32 --port COM6 erase_flash
esptool.py --chip esp32 --port COM6 --baud 460800 write_flash -z 0x1000  esp32-20190818-v1.11-219-gaf5c998f3.bin