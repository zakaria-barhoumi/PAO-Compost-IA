import os
import glob
import shutil
from PIL import Image
from tqdm import tqdm

# --- CONFIGURATION ---

# 1. Dossier contenant vos fichiers .txt (format KITTI) originaux
INPUT_LABELS_DIR = "dataset/batteries_raw/labels"

# 2. Dossier contenant vos images originales (.jpg ou .png)
INPUT_IMAGES_DIR = "dataset/batteries_raw/images"

# 3. Dossier de sortie (où les fichiers convertis seront sauvegardés)
OUTPUT_DIR = "dataset/batteries_yolo"

# La classe que l'on veut garder (tel qu'écrit dans le fichier texte source)
TARGET_LABEL = "battery"

# L'ID de classe YOLO que l'on veut assigner (0 = Dgrx pour votre modèle)
YOLO_CLASS_ID = 0

def convert_box(size, box):
    """
    Convertit KITTI (xmin, ymin, xmax, ymax) vers YOLO (x_center, y_center, width, height)
    Normalisé par la taille de l'image.
    """
    dw = 1. / size[0]
    dh = 1. / size[1]
    
    # Calcul du centre, largeur et hauteur
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    
    # Normalisation
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def main():
    # Création des dossiers de sortie
    output_images_dir = os.path.join(OUTPUT_DIR, "images")
    output_labels_dir = os.path.join(OUTPUT_DIR, "labels")
    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(output_labels_dir, exist_ok=True)

    # Trouver tous les fichiers texte dans le dossier labels
    txt_files = glob.glob(os.path.join(INPUT_LABELS_DIR, "*.txt"))
    
    if not txt_files:
        print(f"Erreur: Aucun fichier .txt trouvé dans {INPUT_LABELS_DIR}")
        return

    print(f"Trouvé {len(txt_files)} fichiers de labels. Démarrage de la conversion...")
    
    converted_count = 0

    for txt_path in tqdm(txt_files):
        # Récupérer le nom de base (ex: '0001' pour '0001.txt')
        base_name = os.path.splitext(os.path.basename(txt_path))[0]
        
        # Chercher l'image correspondante dans le dossier images
        img_path_jpg = os.path.join(INPUT_IMAGES_DIR, base_name + ".jpg")
        img_path_png = os.path.join(INPUT_IMAGES_DIR, base_name + ".png")
        
        # Vérifier si l'image existe en JPG ou PNG
        if os.path.exists(img_path_jpg):
            img_path = img_path_jpg
        elif os.path.exists(img_path_png):
            img_path = img_path_png
        else:
            # Si aucune image correspondante n'est trouvée, on saute ce fichier texte
            # (car on a besoin des dimensions de l'image pour la conversion YOLO)
            continue

        # Ouvrir l'image pour avoir ses dimensions (width, height)
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                
                # --- TRAITEMENT DU FICHIER TEXTE ---
                yolo_lines = []
                has_target_class = False
                
                with open(txt_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split()
                        # Format attendu: type truncated occluded alpha xmin ymin xmax ymax ...
                        # Exemple: battery 0.0 0 0.0 200 151 276 226 ...
                        
                        if not parts: continue
                        
                        class_name = parts[0]
                        
                        # On ne garde que si c'est "battery"
                        if class_name == TARGET_LABEL:
                            has_target_class = True
                            
                            # Extraction des coordonnées pixels (indices 4, 5, 6, 7)
                            xmin = float(parts[4])
                            ymin = float(parts[5])
                            xmax = float(parts[6])
                            ymax = float(parts[7])
                            
                            # Conversion mathématique vers YOLO
                            bbox = (xmin, xmax, ymin, ymax)
                            yx, yy, yw, yh = convert_box((w, h), bbox)
                            
                            # Ajouter la ligne formatée YOLO
                            yolo_lines.append(f"{YOLO_CLASS_ID} {yx:.6f} {yy:.6f} {yw:.6f} {yh:.6f}")

                # Si on a trouvé des batteries, on sauvegarde le résultat
                if has_target_class and yolo_lines:
                    # 1. Sauvegarder le nouveau label
                    out_txt_path = os.path.join(output_labels_dir, base_name + ".txt")
                    with open(out_txt_path, 'w') as f_out:
                        f_out.write("\n".join(yolo_lines))
                    
                    # 2. Copier l'image correspondante dans le dossier de sortie
                    # (Comme ça, votre dataset final est complet et prêt à l'emploi)
                    shutil.copy(img_path, os.path.join(output_images_dir, os.path.basename(img_path)))
                    
                    converted_count += 1

        except Exception as e:
            print(f"Erreur lors du traitement de {base_name}: {e}")
            continue

    print("------------------------------------------------")
    print(f"Conversion Terminée !")
    print(f"Fichiers traités avec succès (contenant des batteries) : {converted_count}")
    print(f"Dataset prêt dans : {OUTPUT_DIR}")
    print("------------------------------------------------")

if __name__ == "__main__":
    main()

