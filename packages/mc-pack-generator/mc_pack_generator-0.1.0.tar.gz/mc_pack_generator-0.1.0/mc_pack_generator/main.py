import os
import uuid
import json

def gerar_uuid():
    return str(uuid.uuid4())

def criar_manifesto_comportamento(nome, descricao, versao):
    return {
        "format_version": 2,
        "header": {
            "name": nome,
            "description": descricao,
            "uuid": gerar_uuid(),
            "version": [1, 0, 0],
            "min_engine_version": versao
        },
        "modules": [
            {
                "type": "data",
                "uuid": gerar_uuid(),
                "version": [1, 0, 0]
            }
        ]
    }

def criar_manifesto_recurso(nome, descricao, versao):
    return {
        "format_version": 2,
        "header": {
            "name": nome,
            "description": descricao,
            "uuid": gerar_uuid(),
            "version": [1, 0, 0],
            "min_engine_version": versao
        },
        "modules": [
            {
                "type": "resources",
                "uuid": gerar_uuid(),
                "version": [1, 0, 0]
            }
        ]
    }

def criar_manifesto_skin(nome, descricao):
    return {
        "format_version": 1,
        "header": {
            "name": nome,
            "uuid": gerar_uuid(),
            "version": [1, 0, 0]
        }
    }

def criar_skins_json():
    return {
        "serialize_name": "exemplo_skin_pack",
        "localization_name": "Exemplo Skin Pack",
        "skins": [
            {
                "localization_name": "Skin 1",
                "geometry": "geometry.humanoid.custom",
                "texture": "skin1.png",
                "type": "free"
            }
        ],
        "capabilities": ["persona"],
        "serialize_name_v2": "exemplo_skin_pack"
    }

def criar_estrutura(nome, descricao, tipo, versao):
    tipo_nome = {"b": "behavior", "r": "resource", "s": "skin"}
    pasta_principal = f"{nome.replace(' ', '_')}_{tipo_nome[tipo]}_pack"
    os.makedirs(pasta_principal, exist_ok=True)

    # Manifesto
    manifest_path = os.path.join(pasta_principal, "manifest.json")
    if tipo == "b":
        manifesto = criar_manifesto_comportamento(nome, descricao, versao)
        os.makedirs(os.path.join(pasta_principal, "functions"), exist_ok=True)
    elif tipo == "r":
        manifesto = criar_manifesto_recurso(nome, descricao, versao)
        os.makedirs(os.path.join(pasta_principal, "textures"), exist_ok=True)
    elif tipo == "s":
        manifesto = criar_manifesto_skin(nome, descricao)
        with open(os.path.join(pasta_principal, "skins.json"), "w", encoding="utf-8") as f:
            json.dump(criar_skins_json(), f, indent=4)

    # Salvar manifest.json
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=4)

    print(f"\n✅ Pacote '{nome}' criado com sucesso em: {pasta_principal}")

def main():
    print("=== Criador de Pacote Minecraft Bedrock ===")
    nome = input("Nome do projeto: ").strip()
    descricao = input("Descrição do projeto: ").strip()

    tipo = ""
    while tipo not in ["b", "r", "s"]:
        tipo = input("Tipo do pacote ('b' = behavior, 'r' = resource, 's' = skin): ").strip().lower()

    versao = [1, 20, 0]
    if tipo in ["b", "r"]:
        versao_input = input("Versão mínima do Minecraft (ex: 1.21.0): ").strip()
        try:
            versao = [int(n) for n in versao_input.split(".")[:3]]
            while len(versao) < 3:
                versao.append(0)
        except:
            print("⚠️ Versão inválida. Usando padrão 1.20.0.")

    criar_estrutura(nome, descricao, tipo, versao)

if __name__ == "__main__":
    main()
