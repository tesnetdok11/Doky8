#!/bin/bash
echo "=== DEPLOYING DOKYOS SERVICE ==="

# Copy service file to systemd
cp doky_daemon.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable doky_daemon.service

# Start service
systemctl start doky_daemon.service

# Check status
systemctl status doky_daemon.service

echo "=== SERVICE DEPLOYED ==="
echo "Commands:"
echo "sudo systemctl start doky_daemon.service"
echo "sudo systemctl stop doky_daemon.service" 
echo "sudo systemctl status doky_daemon.service"
echo "journalctl -u doky_daemon.service -f"
