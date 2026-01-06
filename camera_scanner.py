import csv
import datetime
import logging
import os
import sys
from typing import Dict, Any, Optional

import requests
from hikvisionapi import Client

# Tenta importar o gerador de senhas customizado
try:
    from generate_password import create as generate_custom_password
except ImportError:
    generate_custom_password = None

# --- Configurações Globais ---
DEFAULT_USERNAME = os.getenv('HIK_USER', 'admin')
DEFAULT_PASSWORD = os.getenv('HIK_PASSWORD', 'admin1234')  # Altere 'admin1234' para uma variável segura
HTTP_PORT = 80
TIMEOUT_SECONDS = 5

# --- Arquivos ---
INPUT_IPS_FILE = 'ips_example.txt'
OUTPUT_CSV_FILE = 'camera_scanner_info.csv'
LOG_FILE = 'scan_log.txt'

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout) # Imprime no console também
    ]
)

def get_essential_camera_info(host: str, api_password: str) -> Dict[str, Any]:
    """
    Connects to a Hikvision camera via API and retrieves essential information.

    Args:
        host (str): The IP address of the camera.
        api_password (str): The password to attempt authentication.

    Returns:
        Dict[str, Any]: A dictionary containing normalized camera data.
    """
    camera_data = {
        'MAC': 'N/A',
        'IP': host,
        'Nome': 'N/A',
        'Modelo': 'N/A',
        'Fabricante': 'Hikvision',
        'Serial': 'N/A',
        'Horário': 'N/A',
        'Modo Sinc. Horário': 'N/A',
        'Time Zone': 'N/A',
        'IP Configurado': 'N/A',
        'Máscara Sub-rede': 'N/A',
        'Gateway Padrão': 'N/A',
        'Status Coleta': 'Erro'
    }

    cam = None
    
    # 1. Tentativa de Conexão e Autenticação
    try:
        # Tenta senha customizada
        cam = Client(f'http://{host}:{HTTP_PORT}', DEFAULT_USERNAME, api_password, timeout=TIMEOUT_SECONDS)
        # Teste simples para validar autenticação antes de prosseguir
        cam.System.deviceInfo(method='get')
        logging.info(f"[{host}] Autenticado com sucesso (Senha customizada).")
        
    except Exception as e:
        if '401' in str(e):
            logging.warning(f"[{host}] Falha na senha customizada. Tentando senha padrão...")
            try:
                cam = Client(f'http://{host}:{HTTP_PORT}', DEFAULT_USERNAME, DEFAULT_PASSWORD, timeout=TIMEOUT_SECONDS)
                cam.System.deviceInfo(method='get') # Valida conexão
                logging.info(f"[{host}] Autenticado com sucesso (Senha padrão).")
            except Exception as e_default:
                logging.error(f"[{host}] Falha na autenticação (Padrão): {e_default}")
                return camera_data
        else:
            logging.error(f"[{host}] Erro de conexão inicial: {e}")
            return camera_data

    # 2. Coleta: Device Info
    try:
        device_info = cam.System.deviceInfo(method='get')
        if isinstance(device_info, dict) and 'DeviceInfo' in device_info:
            info = device_info['DeviceInfo']
            camera_data['Nome'] = info.get('deviceName', 'N/A')
            camera_data['Modelo'] = info.get('model', 'N/A')
            camera_data['Serial'] = info.get('serialNumber', 'N/A')
            camera_data['MAC'] = info.get('macAddress', 'N/A')
    except Exception as e:
        logging.error(f"[{host}] Erro ao obter DeviceInfo: {e}")

    # 3. Coleta: Horário e Verificação de Drift
    try:
        time_response = cam.System.time(method='get')
        if isinstance(time_response, dict) and 'Time' in time_response:
            time_data = time_response['Time']
            camera_data['Time Zone'] = time_data.get('timeZone', 'N/A')
            camera_data['Modo Sinc. Horário'] = time_data.get('timeMode', 'N/A')
            
            local_time_str = time_data.get('localTime', 'N/A')
            
            if local_time_str != 'N/A':
                try:
                    # Parse data da câmera
                    camera_dt = datetime.datetime.fromisoformat(local_time_str)
                    
                    # Compara com horário do sistema (UTC aware)
                    local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                    system_dt = datetime.datetime.now(local_tz)

                    # Normaliza para UTC para comparação
                    diff = abs((camera_dt.astimezone(datetime.timezone.utc) - 
                                system_dt.astimezone(datetime.timezone.utc)).total_seconds())

                    if diff <= 60:
                        camera_data['Horário'] = 'Sincronizado'
                    else:
                        camera_data['Horário'] = f"Desvio de {int(diff)}s"
                except ValueError as ve:
                    camera_data['Horário'] = f"Erro Formato Data"
                    logging.error(f"[{host}] Erro parse data: {ve}")
    except Exception as e:
        logging.error(f"[{host}] Erro ao obter Time: {e}")

    # 4. Coleta: Configuração de Rede
    try:
        # Tenta interface 1 (cabeada geralmente), depois 0 se falhar
        network_found = False
        for iface_id in [1, 0]:
            try:
                net_resp = cam.System.Network.interfaces[iface_id](method='get')
                if isinstance(net_resp, dict) and 'NetworkInterface' in net_resp:
                    ip_info = net_resp['NetworkInterface'].get('IPAddress', {})
                    camera_data['IP Configurado'] = ip_info.get('ipAddress', 'N/A')
                    camera_data['Máscara Sub-rede'] = ip_info.get('subnetMask', 'N/A')
                    camera_data['Gateway Padrão'] = ip_info.get('DefaultGateway', {}).get('ipAddress', 'N/A')
                    network_found = True
                    break
            except Exception:
                continue # Tenta a próxima interface silenciosamente
        
        if not network_found:
            logging.warning(f"[{host}] Nenhuma interface de rede retornou dados válidos.")

    except Exception as e:
        logging.error(f"[{host}] Erro crítico em Network Config: {e}")

    camera_data['Status Coleta'] = 'Sucesso'
    return camera_data

def main():
    print("\n--- Iniciando Varredura Hikvision ---")
    
    # Validação do arquivo de entrada
    if not os.path.exists(INPUT_IPS_FILE):
        logging.critical(f"Arquivo '{INPUT_IPS_FILE}' não encontrado.")
        return

    ips_to_scan = []
    try:
        with open(INPUT_IPS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    ips_to_scan.append((parts[0].strip(), parts[1].strip()))
    except Exception as e:
        logging.critical(f"Erro ao ler arquivo de IPs: {e}")
        return

    if not ips_to_scan:
        logging.warning("Lista de IPs vazia.")
        return

    logging.info(f"Carregados {len(ips_to_scan)} dispositivos para verificação.")

    results = []
    
    # Loop principal
    for ip, nome_host in ips_to_scan:
        logging.info(f"Processando: {nome_host} ({ip})...")
        
        # Gera senha se a função existir, senão usa padrão
        password_api = DEFAULT_PASSWORD
        if generate_custom_password:
            try:
                password_api = generate_custom_password(nome_host)
            except Exception as e:
                logging.error(f"Erro ao gerar senha para {nome_host}: {e}")

        data = get_essential_camera_info(ip, password_api)
        results.append(data)

    # Exportação CSV
    fieldnames = [
        'MAC', 'IP', 'Nome', 'Fabricante', 'Modelo', 'Serial', 'Horário',
        'Modo Sinc. Horário', 'Time Zone', 'IP Configurado', 'Máscara Sub-rede',
        'Gateway Padrão', 'Status Coleta'
    ]

    try:
        with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"Exportação concluída com sucesso: {OUTPUT_CSV_FILE}")
    except Exception as e:
        logging.critical(f"Falha ao escrever CSV: {e}")

if __name__ == "__main__":
    main()