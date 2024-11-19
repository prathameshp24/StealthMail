# StealthMail
Cryptograhy and information security project. Instructor - Dr. Rajendra Hegadi.

# Anonymous Chat Application over Tor

## Project Overview

This project implements a secure, anonymous chat application utilizing the Tor network. It ensures end-to-end encryption and anonymity by leveraging cryptographic public-key infrastructure (PKI) and routing communications through Tor hidden services. Users can interact via private chat rooms using generated public keys, enhancing privacy and security.

---

## Features
- **Anonymous Communication**: Messages routed exclusively through Tor hidden services.
- **End-to-End Encryption**: Uses RSA-based encryption for secure data exchange.
- **Public Key Exchange**: Establishes secure communication using a server-provided public key.
- **QR Code Integration**: Users can easily share encryption keys or onion URLs via generated QR codes.
- **Key Management**: Handles private/public keys and onion service credentials securely.

---

## Project Structure
1. **Python Scripts**:
   - Manage hidden services, cryptographic keys, and communication logic.
2. **Static Files**:
   - HTML templates and QR codes for public interaction.
3. **Encryption Keys**:
   - Securely stored in the `/files/keys` directory.

---

## Installation Instructions

### **1. Prerequisites**
- **Python 3.9+**
- **Tor Browser** installed and configured on your system.
- **QR Code Scanner** (for QR-based key sharing).
- Recommended: **Docker** for isolated deployment.

### **2. Clone Repository**
```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>/crypto
```

### **3. Install Dependencies**
Install required Python libraries:
```bash
pip install -r requirements.txt
```

### **4. Run the Application**
Start the chat client:
```bash
python run_chat_client.py
```
Alternatively, set up the Tor hidden service:
```bash
python create_hidden_service_and_server.py
```

---

## **How to Use**

### **Step 0 : Configure the Tor browser**

When you execute the program run_stealthmail.py , inside the main menu enter 0. A prompt will appear asking you to enter the path of the Tor.exe file .

For Linux/Macos systems : Simply enter Tor

For Windows : Paste the path of Torr.exe file from your Tor browser folder . 

A message will appear confirming the configuration . If path entered correctly there won’t be further display of the message . 

### **Step 1: Generate Keys**
Use `keys_manager.py` to generate your private/public key pair:
```bash
python keys_manager.py
```

### **Step 2: Configure Hidden Service**
Run `create_hidden_service_and_server.py` to set up a Tor hidden service:
```bash
python create_hidden_service_and_server.py
```

### **Step 3: Start Chat**
- Run the file 'run_stealthmail.py' and choose option 3 in the option list to initiate the chat session
- Share your public key (or QR code) with others to begin secure communication.

---

## **Technologies Used**
- **Python**: Core scripting language for backend logic.
- **Tor**: Ensures anonymous communication.
- **Cryptography**: Implements RSA encryption using the `cryptography` library.
- **HTML/CSS**: For creating onion service webpages.

---

## **Project Highlights**
1. **Security**:
   - Uses RSA encryption to protect messages.
   - Keys are securely managed and stored.

2. **Anonymity**:
   - Tor hidden services ensure no IP addresses are leaked.
   - Messages are routed exclusively through the Tor network.

3. **Ease of Use**:
   - QR codes simplify sharing of public keys and onion URLs.
   - Lightweight design allows seamless operation on most devices.

---

## **Project Directory Structure**
```
/crypto
├── compare.cpp                        # Helper for cryptographic comparisons
├── create_hidden_service_and_server.py # Hidden service setup
├── create_onion_page.py               # Onion page generator
├── run_chat_client.py                 # Main chat application
├── /files                             # Data storage
│   ├── /keys                          # Key files
│   ├── /qr_codes                      # QR code images
│   └── /others                        # Configuration files
```

---

## **Contributions**
- Contributions are welcome! Fork the repository and submit pull requests.

---

## **License**
This project is licensed under the MIT License.

---
