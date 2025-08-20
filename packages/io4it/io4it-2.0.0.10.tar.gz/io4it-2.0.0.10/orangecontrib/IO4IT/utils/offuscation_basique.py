import os
import json
import hashlib
import getpass

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement
else:
    from orangecontrib.AAIT.utils import MetManagement


#  FONCTIOSN D'OBFUSCATION GÉNÉRALES & CHEMIN
# Fonction pour générer une clé simple à partir du nom d'utilisateur
def get_user_key():
    try:
        username = getpass.getuser()
        #try:
            #username = os.getlogin()

        #except OSError:
            #username = getpass.getuser()

        if not username:
            raise ValueError("Nom d'utilisateur introuvable")

        # On dérive une clé simple (1 octet) depuis le hash du nom d'utilisateur
        digest = hashlib.sha256(username.encode("utf-8")).digest()
        key = digest[0]  # 1 octet pour XOR
        return key

    except Exception as e:
        raise RuntimeError(f"Erreur de génération de clé : {e}")

# Fonction simple de chiffrement/déchiffrement par XOR (non sécurisé mais obscurcissant)
def xor_crypt(data: str, key: int) -> str:
    return ''.join(chr(ord(c) ^ (key & 0xFF)) for c in data)

# Renvoie le chemin absolu vers le sous-dossier « aait_store/keys »
def get_keys_dir(type_key: str = "MICROSOFT_EXCHANGE_OAUTH2") -> str:
    """
    Retourne …/aait_store/keys/<type_key> sans // ni slash final,
    créé au besoin.  type_key ∈ {"IMAP4_SSL", "API", "NXP"}.
    """
    try:
        # normalise le chemin racine
        base = os.path.normpath(MetManagement.get_secret_content_dir())
        if os.path.basename(base) != "keys":
            base = os.path.join(base, "keys")
        dossier = os.path.normpath(os.path.join(base, type_key))
        print("dossier", dossier)
        os.makedirs(dossier, exist_ok=True)
        return dossier
    except Exception as e:
        raise RuntimeError(f"Erreur création/récupération dossier : {e}")



# GSTION IMAP
#je n'ai pas compris à quoi ça sert et ce n'est pas utilisé: à supprimer
""" 
def save_config(str_type,list_str=[]):
    # str_type==IMAP4_SSL -> list_str=[name,server_imap,mail]
    if str_type=="IMAP4_SSL":
        write_imap_config(list_str)
    return
"""

## va lire le fichier de white_list et black_list
## ce fichier et un json du type {"white_list":[], "black_list":[]}
## si pas de fichier ou juste white_liste ou black list il retourne uniquement celui présent
def lire_list_email(chemin_fichier):
    try:
        chemin_fichier=MetManagement.get_secret_content_dir()+chemin_fichier
        if not os.path.exists(chemin_fichier):
            return [[],[]]
        # Lecture du fichier JSON
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            contenu = json.load(f)
        return [
            contenu.get("white_list", []),
            contenu.get("black_list", [])
        ]
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return None



def enregistrer_config_imap4_ssl(agent, my_domain, password, interval_second, alias=""):
    try:
        dossier=get_keys_dir("IMAP4_SSL")
        # Crée le dossier s'il n'existe pas
        if not os.path.exists(dossier):
            os.makedirs(dossier)

        # Récupère l'adresse MAC et chiffre le mot de passe
        key = get_user_key()
        mdp_chiffre = xor_crypt(password, key)

        # Nom du fichier (remplace @ par _at_ pour éviter les problèmes)
        nom_fichier = os.path.join(dossier, f"{agent}{my_domain.replace('@', '_at_')}.json")
        if alias=="''" or alias=="\"\"":
            alias=""



        # Contenu à écrire dans le fichier
        contenu = {
            "agent": agent,
            "domain": my_domain,
            "interval_second": interval_second,
            "password_encrypted": mdp_chiffre,
            "alias": alias
        }

        # Écriture du fichier
        with open(nom_fichier, "w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=4)

        print(f"✅ Fichier enregistré : {nom_fichier}")
        return 0

    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement : {e}")
        return 1

def enregistrer_config_owa(mail,alias,server,username,password,interval):
    try:
        dossier=get_keys_dir("MICROSOFT_EXCHANGE_OWA")
        # Crée le dossier s'il n'existe pas
        if not os.path.exists(dossier):
            os.makedirs(dossier)

        # Récupère l'adresse MAC et chiffre le mot de passe
        key = get_user_key()
        mdp_chiffre = xor_crypt(password, key)

        # Nom du fichier (remplace @ par _at_ pour éviter les problèmes)
        nom_fichier = os.path.join(dossier, f"{alias.replace('@', '_at_')}.json")


        # Contenu à écrire dans le fichier
        contenu = {
            "mail": mail,
            "alias": alias,
            "server":server,
            "username":username,
            "password_encrypted": mdp_chiffre,
            "interval_second": interval
        }

        # Écriture du fichier
        with open(nom_fichier, "w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=4)

        print(f"✅ Fichier enregistré : {nom_fichier}")
        return 0

    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement : {e}")
        return 1



# Fonction pour lire le fichier de configuration et déchiffrer le mot de passe
def lire_config_imap4_ssl(chemin_fichier):
    # renvoie une liste =["agent","domain",mdp,"interval_second"]
    try:
        chemin_fichier = os.path.join(get_keys_dir("IMAP4_SSL"), chemin_fichier)
        # Lecture du fichier JSON
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            contenu = json.load(f)

        # Récupère l'adresse MAC
        key = get_user_key()

        # Déchiffre le mot de passe
        mdp_dechiffre = xor_crypt(contenu["password_encrypted"], key)
        return [
            contenu["agent"],
            contenu["domain"],
            mdp_dechiffre,
            int(contenu["interval_second"]),
            contenu.get("alias", "")
        ]
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return None


def lire_config_owa(chemin_fichier):
    try:
        chemin_fichier = os.path.join(get_keys_dir("MICROSOFT_EXCHANGE_OWA"), chemin_fichier)
        print("chemin fichier", chemin_fichier)
        # Lecture du fichier JSON
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            contenu = json.load(f)

        # Récupère l'adresse MAC
        key = get_user_key()

        # Déchiffre le mot de passe
        mdp_dechiffre = xor_crypt(contenu["password_encrypted"], key)
        return [
            contenu["mail"],
            contenu["alias"],
            contenu["server"],
            contenu["username"],
            mdp_dechiffre,
            int(contenu["interval_second"])
        ]

    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return None


def enregistrer_config_cli_imap4_ssl():
    print("\n📝 Écriture d’un fichier de configuration :")
    agent = input("🤖 Nom de l’agent : ").strip()
    domaine = input("📨 @domain.com? : ").strip()
    mdp = input("📨mot de passe? : ").strip()
    interval = int(input("⏱️ Intervalle en secondes : ").strip())
    alias = input("Nom de l'alias : ").strip()
    if 0!= enregistrer_config_imap4_ssl(agent,domaine,mdp,interval,alias):
        print("erreur!")

def enregistrer_config_cli_owa():
    print("\n📝 Écriture d’un fichier de configuration owa :")
    mail = input("🤖 mail (nom@domain.com) : ").strip()
    alias = input("📨 alias (=mail apparant :(nom2@domain2.com) ").strip()
    server = input("server ? toto.titi.tata: ").strip()
    username = input("usernamme (domaine\\username): ").strip()
    mdp = input("password?: ").strip()
    interval = int(input("⏱️ Intervalle en secondes : ").strip())
    if alias == "''" or alias == "\"\"" or alias=="":
        alias = mail

    if 0!= enregistrer_config_owa(mail,alias,server,username,mdp,interval):
        print("erreur!")

def enregistrer_config_cli_oauth2():

    print("\n📝 Écriture d’un fichier de configuration OAuth2 :")

    client_id = input("🆔 Client ID : ").strip()
    client_secret = input("🔑 Client Secret : ").strip()
    tenant_id = input("🏢 Tenant ID (GUID Azure) : ").strip()
    user_email = input("📨 Adresse email de l'utilisateur Exchange : ").strip()

    nom_fichier = input("💾 Nom du fichier à enregistrer (ex: config_oauth2.json) : ").strip()

    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "tenant_id": tenant_id,
        "user_email": user_email
    }

    try:
        dossier = get_keys_dir("MICROSOFT_EXCHANGE_OAUTH2")
        os.makedirs(dossier, exist_ok=True)
        chemin_fichier = os.path.join(dossier, nom_fichier)

        with open(chemin_fichier, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration enregistrée dans : {chemin_fichier}")
    except Exception as e:
        print(f"❌ Erreur lors de l’enregistrement : {e}")

def lire_config_cli_oauth2(chemin_fichier):
    try:
        chemin_fichier = os.path.join(get_keys_dir("MICROSOFT_EXCHANGE_OAUTH2"), chemin_fichier)
        print("oauth2", chemin_fichier)
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            contenu = json.load(f)

        # Retourne les infos de configuration
        return [
            contenu["client_id"],
            contenu["client_secret"],
            contenu["tenant_id"],
            contenu["user_email"]
        ]

    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return None

def lecture_config_cli_owa():
    chemin_fichier = input("📄 non fichier json (pas le chemin!) JSON : ").strip()
    config = lire_config_owa(chemin_fichier)

    if config==None:
        print("erreur")
    print(config)

def lire_config_cli_imap4_ssl():
    chemin_fichier = input("📄 non fichier json (pas le chemin!) JSON : ").strip()
    config = lire_config_imap4_ssl(chemin_fichier)

    if config==None:
        print("erreur")
    print(config)


# Gestion clés API          (HARD dossier aait_store/keys)
# Enregistre un fichier JSON {service, api_key_encrypted, description}
def enregistrer_config_api(service_name, api_key, description=""):
    try:
        # Clé « personnelle » (1 octet) et chiffrement XOR
        key = get_user_key()
        api_key_enc = xor_crypt(api_key, key)

        contenu = {
            "service": service_name,
            "api_key_encrypted": api_key_enc,
            "description": description
        }

        chemin_fic = os.path.join(get_keys_dir("API"), f"{service_name}.json")
        with open(chemin_fic, "w", encoding="utf-8") as fp:
            json.dump(contenu, fp, indent=4)

        #print(f"✅ Fichier enregistré : {chemin_fic}")
        #print(get_user_key())
        return 0
    except Exception as e:
        print(f"❌ Erreur d’enregistrement : {e}")
        return 1

# Lecture + déchiffrement → dict {"service", "api_key", "description"}
def lire_config_api(service_name):
    try:
        chemin_fic = os.path.join(get_keys_dir("API"), f"{service_name}.json")
        with open(chemin_fic, "r", encoding="utf-8") as fp:
            contenu = json.load(fp)

        key = get_user_key()
        api_key_plain = xor_crypt(contenu["api_key_encrypted"], key)
        #print(api_key_plain)
        #print(get_user_key())

        return {
            "service": contenu["service"],
            "api_key": api_key_plain,
            "description": contenu.get("description", "")
        }
    except FileNotFoundError:
        print("❌ Fichier introuvable.")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return None

def enregistrer_config_cli_api():
    print("\n📝 Écriture d’une clé API :")
    service = input("🔖 Nom du service : ").strip()
    api_key = getpass.getpass("🔑 Clé API         : ").strip()
    desc = input("✏️  Description      : ").strip()
    if 0 != enregistrer_config_api(service, api_key, desc):
        print("erreur!")

def lire_config_cli_api():
    service = input("🔖 Nom du service : ").strip()
    cfg = lire_config_api(service)
    if cfg is None:
        print("erreur")
        return
    print(f"\n📄 service     : {cfg['service']}")
    print(f"🔑 clé API     : {cfg['api_key']}")
    if cfg['description']:
        print(f"📝 description : {cfg['description']}")


# Gestion d’éléments de nxp (DOSSIER_NODE_ID, SERVEUR, USERNAME, PASSWORD)  (HARD dossier aait_store/keys)

def enregistrer_config_nxp(
    dossier_node_id: str,
    serveur: str,
    username: str,
    password: str,
    description: str = ""
) -> int:
    try:
        key = get_user_key()
        password_enc = xor_crypt(password, key)

        contenu = {
            "dossier_node_id": dossier_node_id,
            "serveur": serveur,
            "username": username,
            "password_encrypted": password_enc,
            "description": description
        }

        # ⬅️  Ici : plus de "conn_", juste {serveur}.json
        chemin = os.path.join(get_keys_dir("NXP"), f"{serveur}.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=4)

        print(f"✅ Fichier enregistré : {chemin}")
        return 0
    except Exception as e:
        print(f"❌ Erreur d’enregistrement : {e}")
        return 1

def lire_config_nxp(serveur: str) -> dict | None:
    try:
        chemin = os.path.join(get_keys_dir("NXP"), f"{serveur}.json")  # ⬅️ même logique
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = json.load(f)

        key = get_user_key()
        password_plain = xor_crypt(contenu["password_encrypted"], key)

        return {
            "dossier_node_id": contenu["dossier_node_id"],
            "serveur": contenu["serveur"],
            "username": contenu["username"],
            "password": password_plain,
            "description": contenu.get("description", "")
        }
    except FileNotFoundError:
        print("❌ Fichier introuvable.")
        return None
    except Exception as e:
        print(f"❌ Erreur de lecture : {e}")
        return None

def enregistrer_config_cli_nxp():
    print("\n📝 Écriture d’une connexion nxp :")
    dossier_node_id = input("📦 DOSSIER_NODE_ID : ").strip()
    serveur = input("🌐 SERVEUR         : ").strip()
    username = input("👤 USERNAME        : ").strip()
    password = getpass.getpass("🔑 PASSWORD        : ").strip()
    description = input("✏️  Description     : ").strip()
    enregistrer_config_nxp(
        dossier_node_id,
        serveur,
        username,
        password,
        description
    )

def lire_config_cli_nxp():
    serveur = input("🌐 SERVEUR : ").strip()          # ⬅️ on demande le serveur
    cfg = lire_config_nxp(serveur)
    if cfg is None:
        print("erreur")
        return
    print(f"\n📄 dossier_node_id : {cfg['dossier_node_id']}")
    print(f"🌐 serveur         : {cfg['serveur']}")
    print(f"👤 username        : {cfg['username']}")
    print(f"🔑 password        : {cfg['password']}")
    if cfg["description"]:
        print(f"📝 description     : {cfg['description']}")




if __name__ == "__main__":
    print("1) ecrire fichier IMAP4_SSL")
    print("2) dechiffer fichier IMAP4_SSL")
    print("3) Écrire fichier CLÉ API")
    print("4) Déchiffrer fichier CLÉ API")
    print("5) Écrire fichier NXP")
    print("6) Déchiffrer fichier NXP")
    print("7) Écrire fichier Microsoft Exchange (OWA)")
    print("8) Déchiffrer fichier Microsoft Exchange (OWA)")
    print("9) Écrire fichier Microsoft Exchange (OAuth2)")
    print("10) Déchiffrer fichier Microsoft Exchange (OAuth2)")
    choix = input("👉 Que faire ? [1-10] : ").strip()

    if choix == "1":
        enregistrer_config_cli_imap4_ssl()
    elif choix == "2":
        lire_config_cli_imap4_ssl()
    elif choix == "3":
        enregistrer_config_cli_api()
    elif choix == "4":
        lire_config_cli_api()
    elif choix == "5":
        enregistrer_config_cli_nxp()
    elif choix == "6":
        lire_config_cli_nxp()
    elif choix=="7":
        enregistrer_config_cli_owa()
    elif choix=="8":
        lecture_config_cli_owa()
    elif choix=="9":
        enregistrer_config_cli_oauth2()
    elif choix=="10":
        lecture_config_cli_oauth2()

    else:
        print("❌ Choix invalide. Réessayez.\n")



