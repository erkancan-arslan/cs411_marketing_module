import os

# Proje Adı
PROJECT_NAME = "CRM_Marketing_Module"

# Oluşturulacak Klasör ve Dosya Yapısı
structure = {
    PROJECT_NAME: [
        "_context",  # AI Agent Promptları buraya
        "data",      # Mock JSON verileri
        "tests",
        {
            "src": [  # Kaynak Kodlar
                "__init__.py",
                {
                    "core": ["__init__.py", "interfaces.py"],
                    "models": ["__init__.py", "customer.py", "campaign.py"],
                    "repository": ["__init__.py", "json_repo.py"],
                    "services": ["__init__.py", "segmentation.py", "campaign.py", "email_service.py", "analytics.py"],
                    "web": [
                        "__init__.py", "app.py",
                        {
                            "templates": ["layout.html", "login.html", "dashboard.html", "campaign.html"],
                            "static": [
                                {"css": []},
                                {"js": []},
                                {"img": []}
                            ]
                        }
                    ]
                }
            ]
        },
        "config.py",
        "run.py",
        "requirements.txt",
        "README.md"
    ]
}

def create_structure(base_path, structure_list):
    for item in structure_list:
        if isinstance(item, str):
            # Dosya oluştur
            file_path = os.path.join(base_path, item)
            with open(file_path, 'w') as f:
                pass # Boş dosya yarat
            print(f"📄 Dosya oluşturuldu: {file_path}")
        elif isinstance(item, dict):
            # Klasör ve altındakiler
            for folder_name, contents in item.items():
                folder_path = os.path.join(base_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                print(f"📂 Klasör oluşturuldu: {folder_path}")
                create_structure(folder_path, contents)

if __name__ == "__main__":
    print(f"🚀 '{PROJECT_NAME}' projesi oluşturuluyor...")
    create_structure(os.getcwd(), structure[PROJECT_NAME])
    print("\n✅ Proje iskeleti başarıyla tamamlandı!")