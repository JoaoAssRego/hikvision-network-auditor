# Hikvision Network Scanner & Auditor

Ferramenta de automação desenvolvida em Python para auditoria e inventário de câmeras de segurança Hikvision em redes corporativas.

## 🚀 Funcionalidades

* **Coleta Automatizada:** Extrai informações essenciais (Serial, Modelo, MAC, Firmware).
* **Auditoria de Rede:** Verifica IP configurado, Gateway e Máscara.
* **Verificação de NTP:** Analisa se o horário da câmera está sincronizado com o servidor (drift check).
* **Segurança:** Suporte a autenticação via variáveis de ambiente e fallback de senhas.
* **Logging:** Sistema de logs robusto para diagnóstico de falhas de conexão.

## 🛠️ Tecnologias Utilizadas

* Python 3.x
* Hikvision API (ISAPI)
* CSV para exportação de dados

## ⚙️ Como usar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
2. Com certeza. Para transformar esse script isolado em um projeto de portfólio profissional (ideal para mostrar suas habilidades de DevOps e Python), precisamos estruturar o repositório corretamente antes de subir.

O segredo de um bom repositório não é apenas o código, mas a documentação e a segurança (não vazar dados sensíveis).

Siga este passo a passo no seu Linux:

Passo 1: Preparar os Arquivos Locais
Crie uma pasta nova para organizar tudo limpo, se ainda não tiver feito.

Crie o arquivo .gitignore (ESSENCIAL) Este arquivo diz ao Git o que não subir. Isso evita que você vaze a lista de IPs da sua empresa ou os logs de erro.

Crie um arquivo chamado .gitignore e cole isso dentro:

Plaintext

# Ignorar arquivos de sistema e Python
__pycache__/
*.py[cod]
.env
venv/

# Ignorar arquivos de dados sensíveis (NUNCA suba isso)
ips_hik_*.txt
*_ips.txt
ips_names.txt

# Ignorar arquivos de saída e logs (Isso polui o repositório)
*.csv
*.log
scan_log.txt
cam_erro.txt
troca_senha_cam.txt

# Ignorar configurações de IDE
.vscode/
.idea/
Crie o arquivo requirements.txt Isso mostra quais bibliotecas são necessárias para rodar seu projeto.

Crie um arquivo chamado requirements.txt com este conteúdo:

Plaintext

requests
hikvisionapi
Crie um arquivo de Exemplo (Opcional, mas profissional) Como o .gitignore vai bloquear seu arquivo de IPs real, crie um arquivo falso para mostrar como o usuário deve usar o programa.

Crie um arquivo chamado ips_example.txt:

Plaintext

192.168.1.100, Camera_Portaria
192.168.1.101, Camera_Estacionamento
Crie o README.md Este é o "cartão de visitas". Cole o seguinte modelo (já ajustado para parecer profissional):

Markdown

# Hikvision Network Scanner & Auditor

Ferramenta de automação desenvolvida em Python para auditoria e inventário de câmeras de segurança Hikvision em redes corporativas.

## 🚀 Funcionalidades

* **Coleta Automatizada:** Extrai informações essenciais (Serial, Modelo, MAC, Firmware).
* **Auditoria de Rede:** Verifica IP configurado, Gateway e Máscara.
* **Verificação de NTP:** Analisa se o horário da câmera está sincronizado com o servidor (drift check).
* **Segurança:** Suporte a autenticação via variáveis de ambiente e fallback de senhas.
* **Logging:** Sistema de logs robusto para diagnóstico de falhas de conexão.

## 🛠️ Tecnologias Utilizadas

* Python 3.x
* Hikvision API (ISAPI)
* CSV para exportação de dados

## ⚙️ Como usar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt

2. Crie um arquivo ips.txt seguindo o modelo de ips_example.txt:
    ```IP_DA_CAMERA, NOME_IDENTIFICADOR```

3. Execute o script:
    ```python camera_scanner.py```

## ⚠️ Disclaimer
* Este software foi desenvolvido para uso administrativo em redes autorizadas.
