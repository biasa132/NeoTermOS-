# NeoTermOS Installation Guide

NeoTermOS adalah terminal OS berbasis Python yang berjalan di user-space.
Dokumentasi ini fokus ke **Termux (Android)**.

---

## 📦 Requirements
- Termux (latest)
- Python 3.10+
- Git

---

## 🚀 Install (Termux)
```sh
pkg update && pkg upgrade
pkg install python git -y
git clone https://github.com/USERNAME/NeoTermOS.git
cd NeoTermOS
bash scripts/install.sh

Menjalankan NeoTermOS
```py
python main.py

Login default
username: root
password: root
