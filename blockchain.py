# blockchain.py
import hashlib
import json
from datetime import datetime


class Block:
    def __init__(
        self,
        block_id: int,
        patient_id: str,
        clinic_name: str,
        diagnosis: str,
        treatment: str,
        tanggal: str,
        doctor: str,
        prev_hash: str = ""
    ):
        self.block_id = block_id
        self.patient_id = patient_id
        self.clinic_name = clinic_name
        self.diagnosis = diagnosis
        self.treatment = treatment
        self.tanggal = tanggal
        self.doctor = doctor
        self.prev_hash = prev_hash
        self.current_hash = self.calculate_hash()

    def to_dict(self):
        return {
            "block_id": self.block_id,
            "patient_id": self.patient_id,
            "clinic_name": self.clinic_name,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "tanggal": self.tanggal,
            "doctor": self.doctor,
            "prev_hash": self.prev_hash,
            "current_hash": self.current_hash,
        }

    def calculate_hash(self) -> str:
        """
        Hitung hash SHA-256 dari isi block (kecuali current_hash).
        """
        block_content = {
            "block_id": self.block_id,
            "patient_id": self.patient_id,
            "clinic_name": self.clinic_name,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "tanggal": self.tanggal,
            "doctor": self.doctor,
            "prev_hash": self.prev_hash,
        }
        block_string = json.dumps(block_content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Membuat genesis block (block pertama).
        """
        if self.chain:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        genesis_block = Block(
            block_id=0,
            patient_id="GENESIS",
            clinic_name="GENESIS_CLINIC",
            diagnosis="GENESIS_BLOCK",
            treatment="-",
            tanggal=now,
            doctor="-",
            prev_hash="0"
        )
        self.chain.append(genesis_block)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_block(
        self,
        patient_id: str,
        clinic_name: str,
        diagnosis: str,
        treatment: str,
        tanggal: str,
        doctor: str
    ) -> Block:
        """
        Menambah block baru ke chain berdasarkan data pasien.
        """
        last_block = self.get_last_block()
        new_block_id = last_block.block_id + 1

        new_block = Block(
            block_id=new_block_id,
            patient_id=patient_id,
            clinic_name=clinic_name,
            diagnosis=diagnosis,
            treatment=treatment,
            tanggal=tanggal,
            doctor=doctor,
            prev_hash=last_block.current_hash
        )

        self.chain.append(new_block)
        return new_block

    def to_list_of_dicts(self):
        return [block.to_dict() for block in self.chain]

    def is_chain_valid(self):
        """
        Verifikasi integritas blockchain.
        """
        if not self.chain:
            return True, "Chain kosong."

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i - 1]

            # prev_hash cocok?
            if current_block.prev_hash != prev_block.current_hash:
                return False, f"prev_hash pada block {current_block.block_id} tidak cocok."

            # hash ulang
            recalculated_hash = current_block.calculate_hash()
            if current_block.current_hash != recalculated_hash:
                return False, f"Hash pada block {current_block.block_id} tidak valid."

        return True, "Blockchain valid."
