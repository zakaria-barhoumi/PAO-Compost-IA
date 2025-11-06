import os
import argparse

def rename_images_only(image_dir, prefix):
    """
    Renomme en série uniquement les fichiers images dans un dossier.
    """
    
    print(f"--- Renommage des images dans : {image_dir} ---")
    
    # Lister toutes les images.
    try:
        image_files = [f for f in os.listdir(image_dir) 
                       if f.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.PNG', '.JPG'))]
    except FileNotFoundError:
        print(f"[ERREUR] Le dossier n'existe pas : {image_dir}")
        return
    except Exception as e:
        print(f"[ERREUR] Impossible de lire le dossier : {e}")
        return

    # Trier les fichiers pour un ordre prévisible
    image_files.sort()
    
    if not image_files:
        print("Aucun fichier image trouvé à renommer.")
        return

    counter = 1
    for image_filename in image_files:
        old_image_path = os.path.join(image_dir, image_filename)
        
        image_extension = os.path.splitext(image_filename)[1]
        
        new_base_filename = f"{prefix}_{str(counter).zfill(5)}"
        new_image_path = os.path.join(image_dir, new_base_filename + image_extension)

        # Renommer le fichier
        try:
            os.rename(old_image_path, new_image_path)
            print(f"Renommé : '{image_filename}' -> '{new_base_filename + image_extension}'")
            counter += 1
            
        except Exception as e:
            print(f"Erreur lors du renommage de {image_filename}: {e}")

    print(f"--- Renommage terminé. {counter - 1} images renommées. ---")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Renomme en série les fichiers images d'un dossier.")
    
    parser.add_argument("-i", "--image_dir", 
                        type=str, 
                        required=True, 
                        help="Chemin vers le dossier d'images à renommer (ex: dataset/images/train)")
    
    parser.add_argument("-p", "--prefix", 
                        type=str, 
                        required=True, 
                        help="Préfixe pour les nouveaux noms (ex: 'train' ou 'val')")
    
    args = parser.parse_args()
    
    print("************ AVERTISSEMENT ************")
    print(f"Vous allez renommer de manière IRREVERSIBLE les fichiers dans :")
    print(f"Dossier : {args.image_dir}")
    print(f"Nouveau préfixe : {args.prefix}_XXXXX.ext")
    print("Faites une sauvegarde si vous n'êtes pas sûr.")
    
    user_input = input("Voulez-vous continuer ? (o/n) : ")
    
    if user_input.lower() == 'o':
        print("Confirmation reçue. Début du renommage...")
        rename_images_only(args.image_dir, args.prefix)
    else:
        print("Opération annulée par l'utilisateur.")