# 🐔 Broiler Prediction System (Backend)
This repository contains the **backend system** for the Broiler Prediction project — a system designed to predict broiler chicken growth performance and monitor environmental conditions using **AI** and **IoT** data.
It integrates real-time sensor data collection, machine learning models, and mobile connectivity to support farm management and optimize production outcomes.

# 🧠 Project Overview
The **Broiler Prediction System** assists poultry farms in monitoring key parameters such as temperature, humidity, and ammonia level, feed consumption, mortality, etc.
By leveraging IoT sensors and AI models, the system **detects potential anomalies and helps maintain optimal environmental conditions in broiler houses.**

# 🏗️ System Architecture
The backend connects **IoT devices, AI model, and mobile systems** in a unified architecture.
Sensor data are transmitted through an **MQTT broker**, processed by the **Flask backend**, and analyzed by trained **machine learning model.** The provided API endpoint is used by mobile system.

<img width="4432" height="2608" alt="Untitled(1)" src="https://github.com/user-attachments/assets/9ad7c0b2-3bef-4ac3-b1d3-ff31e92ebaae" />

# ⚙️ Features
•	**Real-time Data Streaming** via MQTT protocol

•	**IoT Simulator** for testing and development environments (https://github.com/affodilajF/iot-virtual-device)

•	**Automated Machine Learning Prediction** scheduled at 09:00 and 16:00 WIB

•	**Data Preprocessing & Storage** with SQL database 

•	**Auth** using Firebase Auth 

•	**FlaskAPI-based API Endpoints**

