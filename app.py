# app.py
from flask import Flask, request, jsonify
from datetime import datetime
import requests

from blockchain import Blockchain
from config import APPS_SCRIPT_POST_URL, APPS_SCRIPT_GET_URL

app = Flask(__name__)

# satu instance blockchain untuk seluruh app
local_blockchain = Blockchain()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Modular Blockchain for Medical Records",
        "endpoints": [
            "POST /add_data",
            "GET /get_chain",
            "GET /verify_chain",
            "GET /detect_cloud_tampering"
        ]
    })


@app.route("/add_data", methods=["POST"])
def add_data():
    """
    Body JSON contoh:

    {
      "patient_id": "PSN-001",
      "clinic_name": "Klinik Sehat Sentosa",
      "diagnosis": "Hipertensi",
      "treatment": "Obat Amlodipine",
      "tanggal": "2025-12-08 09:30:00",   # optional, kalau tidak ada pakai now()
      "doctor": "Dr. Andi"
    }
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body harus JSON. Pastikan Content-Type: application/json dan body berisi JSON valid."
        }), 415

    required_fields = [
        "patient_id",
        "clinic_name",
        "diagnosis",
        "treatment",
        "doctor"
    ]

    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return jsonify({"error": f"Field '{field}' wajib diisi"}), 400

    patient_id = data["patient_id"]
    clinic_name = data["clinic_name"]
    diagnosis = data["diagnosis"]
    treatment = data["treatment"]
    doctor = data["doctor"]

    tanggal = data.get("tanggal")
    if not tanggal:
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tambahkan ke blockchain lokal
    new_block = local_blockchain.add_block(
        patient_id=patient_id,
        clinic_name=clinic_name,
        diagnosis=diagnosis,
        treatment=treatment,
        tanggal=tanggal,
        doctor=doctor
    )

    block_dict = new_block.to_dict()

    # Kirim ke Google Sheets melalui Apps Script
    sync_ok = False
    sync_error = None
    script_response_text = None
    script_status_code = None

    try:
        resp = requests.post(APPS_SCRIPT_POST_URL, json=block_dict, timeout=15)
        script_status_code = resp.status_code
        script_response_text = resp.text

        if resp.status_code == 200:
            # coba baca JSON status dari Apps Script
            try:
                js = resp.json()
                if js.get("status") == "success":
                    sync_ok = True
                else:
                    sync_error = js
            except Exception:
                # kalau gagal parse, tapi status code 200, tetap dianggap berhasil minimal
                sync_ok = True
        else:
            sync_error = resp.text

    except Exception as e:
        sync_error = str(e)

    result = {
        "message": "Block berhasil ditambahkan ke blockchain lokal.",
        "block": block_dict,
        "sync_to_sheets": sync_ok,
        "apps_script_status_code": script_status_code,
        "apps_script_response": script_response_text,
        "apps_script_error": sync_error
    }

    status_code = 201 if sync_ok or sync_error is None else 500
    return jsonify(result), status_code


@app.route("/get_chain", methods=["GET"])
def get_chain():
    chain_data = local_blockchain.to_list_of_dicts()
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data
    })


@app.route("/verify_chain", methods=["GET"])
def verify_chain():
    is_valid, msg = local_blockchain.is_chain_valid()
    return jsonify({
        "is_valid": is_valid,
        "message": msg,
        "length": len(local_blockchain.chain)
    })


@app.route("/detect_cloud_tampering", methods=["GET"])
def detect_cloud_tampering():
    """
    Membandingkan blockchain lokal dengan data pada Google Sheets.
    """
    # 1. Verifikasi terlebih dulu chain lokal
    is_valid, msg = local_blockchain.is_chain_valid()
    if not is_valid:
        return jsonify({
            "error": "Blockchain lokal tidak valid, tidak bisa lanjut cek cloud.",
            "detail": msg
        }), 400

    # 2. Ambil data dari Google Sheets
    try:
        resp = requests.get(APPS_SCRIPT_GET_URL, timeout=15)
        if resp.status_code != 200:
            return jsonify({
                "error": "Gagal mengambil data dari Google Sheets.",
                "status_code": resp.status_code,
                "response": resp.text
            }), 500

        cloud_data = resp.json()  # hasil getSheetDataAsJson()
    except Exception as e:
        return jsonify({
            "error": "Exception saat mengambil atau parsing data dari Google Sheets.",
            "detail": str(e)
        }), 500

    # 3. Susun map block_id -> data
    chain_blocks = local_blockchain.to_list_of_dicts()
    chain_map = {b["block_id"]: b for b in chain_blocks}

    cloud_map = {}
    for row in cloud_data:
        try:
            block_id = int(row.get("block_id"))
        except (TypeError, ValueError):
            continue
        cloud_map[block_id] = row

    differences = []

    # 4. Bandingkan setiap block di blockchain vs cloud
    for block_id, chain_block in chain_map.items():
        if block_id == 0:
            # genesis block di-skip
            continue

        cloud_block = cloud_map.get(block_id)
        if cloud_block is None:
            differences.append({
                "block_id": block_id,
                "type": "missing_in_cloud",
                "message": f"Block {block_id} ada di blockchain, tapi tidak ada di Google Sheets."
            })
            continue

        fields_to_compare = [
            "patient_id", "clinic_name", "diagnosis",
            "treatment", "tanggal", "doctor",
            "prev_hash", "current_hash"
        ]

        for field in fields_to_compare:
            chain_val = str(chain_block.get(field, ""))
            cloud_val = str(cloud_block.get(field, ""))
            if chain_val != cloud_val:
                differences.append({
                    "block_id": block_id,
                    "type": "data_mismatch",
                    "field": field,
                    "block_value": chain_val,
                    "cloud_value": cloud_val
                })

    # 5. Cek block ekstra di cloud
    for block_id, cloud_block in cloud_map.items():
        if block_id not in chain_map and block_id != 0:
            differences.append({
                "block_id": block_id,
                "type": "extra_in_cloud",
                "message": f"Ada block_id {block_id} di Google Sheets yang tidak ada di blockchain."
            })

    tampered = len(differences) > 0

    return jsonify({
        "tampered": tampered,
        "differences": differences,
        "summary": "Terjadi manipulasi data di cloud."
        if tampered else "Tidak ditemukan manipulasi data di cloud (Google Sheets konsisten dengan blockchain)."
    })


if __name__ == "__main__":
    # Jalankan Flask di localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
