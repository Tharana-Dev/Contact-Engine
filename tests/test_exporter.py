import json
import csv
from exporter import Exporter
from contact import Contact

def test_csv_export(tmp_path):
    contacts = [Contact("Ada", "Lovelace", "555", "ada@x.com")]
    exporter = Exporter(contacts)
    file_path = tmp_path / "test.csv"
    
    exporter.write_to_csv(str(file_path))
    
    # Read it back and assert
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert rows[0] == ["first_name", "last_name", "phone", "email"]
        assert rows[1] == ["Ada", "Lovelace", "555", "ada@x.com"]

def test_json_export(tmp_path):
    contacts = [Contact("Ada", "Lovelace", "555", "ada@x.com")]
    exporter = Exporter(contacts)
    file_path = tmp_path / "test.json"
    
    exporter.write_to_json(str(file_path))  # Adjust to match your method name

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert len(data) == 1
    assert data[0]["first_name"] == "Ada"
    assert data[0]["last_name"] == "Lovelace"
    assert data[0]["phone"] == "555"
    assert data[0]["email"] == "ada@x.com"


def test_vcard_export(tmp_path):
    contacts = [Contact("Ada", "Lovelace", "555", "ada@x.com")]
    exporter = Exporter(contacts)
    file_path = tmp_path / "test.vcf"  

    exporter.write_to_vcard(str(file_path))  
    
    with open(file_path, "r", encoding="utf-8") as f:
        vcard_content = f.read()
        
    assert "BEGIN:VCARD" in vcard_content
    assert "VERSION:" in vcard_content
    assert "FN:Ada Lovelace" in vcard_content or "N:Lovelace;Ada" in vcard_content
    assert "TEL;TYPE=CELL:555" in vcard_content
    assert "EMAIL:" in vcard_content
    assert "END:VCARD" in vcard_content
