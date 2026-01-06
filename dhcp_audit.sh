#!/bin/bash

# ==============================================================================
# Script Name: dhcp_audit.sh
# Description: Compares Hikvision camera data (CSV) against DHCP server configuration.
# Author: João Pedro de Assunção Rego
# Usage: ./dhcp_audit.sh
# ==============================================================================

# --- Configuration ---
# Use current directory for portable paths
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
DHCP_CONF_FILE="/etc/dhcp/dhcpd.conf"  # Path to the actual DHCP config
CSV_INPUT_FILE="${CURRENT_DIR}/hikvision_info_essencial.csv"
REPORT_FILE="${CURRENT_DIR}/audit_report.txt"

# --- Validation ---
if [[ ! -f "$CSV_INPUT_FILE" ]]; then
    echo "ERROR: Input CSV file not found: $CSV_INPUT_FILE"
    exit 1
fi

if [[ ! -f "$DHCP_CONF_FILE" ]]; then
    echo "WARNING: DHCP config file not found at $DHCP_CONF_FILE."
    echo "Please update the 'DHCP_CONF_FILE' variable in the script."
    exit 1
fi

# Initialize Report
echo "--- Audit Report: $(date +'%Y-%m-%d %H:%M:%S') ---" > "$REPORT_FILE"
echo "Comparing CSV Data vs DHCP Config..."

# --- Functions ---

# Extracts variables from a DHCP config line format
# Assumes format: MAC, IP, NAME, #FAB, #MODEL (R)
parse_dhcp_line() {
    local dhcp_line="$1"
    
    # Split string by comma
    IFS=',' read -r -a dhcp_data <<< "$dhcp_line"

    # Clean data (Remove '#' and '(R)')
    dhcp_data[0]="${dhcp_data[0]/#\#/}"       # MAC
    dhcp_data[3]="${dhcp_data[3]/#\#/}"       # Fabricante
    dhcp_data[4]="${dhcp_data[4]//\(R\)/}"    # Modelo

    # Output clean elements line by line
    printf "%s\n" "${dhcp_data[@]}"
}

# Verifies match between DHCP data and API CSV data
check_consistency() {
    local -n _dhcp_arr="$1" # Reference to DHCP array
    local -n _csv_arr="$2"  # Reference to CSV array
    local ip_ref="${_csv_arr[1]}" # IP is usually at index 1

    # Loop through first 6 elements to compare essential fields
    for i in {0..5}; do
        # Clean potential carriage returns from CSV data
        local val_csv=$(echo "${_csv_arr[i]}" | tr -d '\r')
        local val_dhcp="${_dhcp_arr[i]}"

        # Check if the CSV value contains the DHCP value (substring match)
        if [[ "$val_csv" != *"$val_dhcp"* ]]; then
            echo "[MISMATCH] IP: $ip_ref | DHCP says: '$val_dhcp' | Camera says: '$val_csv'" >> "$REPORT_FILE"
            return
        fi
    done
}

# --- Main Execution ---

# Read CSV skipping the header (tail -n +2)
tail -n +2 "$CSV_INPUT_FILE" | while IFS="," read -ra csv_line; do
  
    # 1. Find the device in DHCP config using the Hostname (index 2)
    # Note: Ensure the CSV hostname matches exactly what is expected in grep
    device_name="${csv_line[2]}"
    dhcp_entry=$(grep "${device_name}," "$DHCP_CONF_FILE")

    if [[ -z "$dhcp_entry" ]]; then
        echo "[MISSING] Device '$device_name' not found in DHCP config." >> "$REPORT_FILE"
        continue
    fi

    # 2. Parse the DHCP line into an array
    mapfile -t dhcp_parsed < <(parse_dhcp_line "$dhcp_entry")
    
    # 3. Clean CSV data (formatting)
    csv_line[5]=$(echo "${csv_line[5]}" | tr -d '\r')

    # 4. Run comparison
    check_consistency dhcp_parsed csv_line

done

echo -e "\nAudit finished successfully!"
echo "Check the report at: $REPORT_FILE"