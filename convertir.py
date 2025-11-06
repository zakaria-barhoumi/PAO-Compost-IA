import json
import os

CLASS_MAP = {
    'Dgrx': 0,
    'Mrisq': 1,
    'NonCompost': 2,
    'Compost': 3
}


def convert_coordinates_to_yolo(img_width, img_height, box_points):
    """
    Convertit les coordonnées [xmin, ymin, xmax, ymax] de labelme
    en format YOLO normalisé [x_center, y_center, width, height].
    """
    # labelme donne les points comme [[xmin, ymin], [xmax, ymax]]
    xmin = box_points[0][0]
    ymin = box_points[0][1]
    xmax = box_points[1][0]
    ymax = box_points[1][1]

    # Calculer le centre et les dimensions en pixels
    box_width_px = xmax - xmin
    box_height_px = ymax - ymin
    x_center_px = xmin + (box_width_px / 2)
    y_center_px = ymin + (box_height_px / 2)

    # Normaliser les valeurs (diviser par les dimensions de l'image)
    x_center_norm = x_center_px / img_width
    y_center_norm = y_center_px / img_height
    width_norm = box_width_px / img_width
    height_norm = box_height_px / img_height

    return x_center_norm, y_center_norm, width_norm, height_norm


def process_labelme_json(json_file_path, output_txt_path):
    """
    Lit un seul fichier JSON de labelme et écrit le fichier TXT YOLO correspondant.
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        img_width = data['imageWidth']
        img_height = data['imageHeight']

        yolo_lines = []

        for shape in data['shapes']:
            # S'assurer que c'est une boîte rectangulaire
            if shape['shape_type'] != 'rectangle':
                print(f"  [Avertissement] '{shape['label']}' n'est pas un rectangle, ignoré.")
                continue

            label = shape['label']

            # Vérifier si le label est dans notre carte de classes
            if label not in CLASS_MAP:
                print(f"  [ERREUR] Label inconnu: '{label}'. Vérifiez CLASS_MAP.")
                continue

            class_id = CLASS_MAP[label]
            box_points = shape['points']

            # Convertir les coordonnées
            x_c, y_c, w, h = convert_coordinates_to_yolo(img_width, img_height, box_points)

            # Formater la ligne pour le fichier YOLO
            yolo_line = f"{class_id} {x_c} {y_c} {w} {h}"
            yolo_lines.append(yolo_line)

        # Écrire toutes les lignes dans le fichier .txt
        with open(output_txt_path, 'w') as f:
            f.write('\n'.join(yolo_lines))
        
        print(f"Converti: {json_file_path} -> {output_txt_path}")

    except Exception as e:
        print(f"Erreur lors du traitement de {json_file_path}: {e}")


def batch_convert(json_input_dir, txt_output_dir):
    """
    Convertit tous les fichiers .json d'un dossier en .txt dans un autre.
    """
    # S'assurer que le dossier de sortie existe
    os.makedirs(txt_output_dir, exist_ok=True)

    print(f"--- Conversion de {json_input_dir} vers {txt_output_dir} ---")
    
    # Parcourir tous les fichiers dans le dossier d'entrée
    for filename in os.listdir(json_input_dir):
        if filename.endswith('.json'):
            json_path = os.path.join(json_input_dir, filename)
            
            # Créer le nom du fichier .txt (ex: image1.json -> image1.txt)
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(txt_output_dir, txt_filename)

            process_labelme_json(json_path, txt_path)

    print("--- Conversion terminée. ---")


if __name__ == "__main__":
    
    # Chemins pour les données d'entraînement (train)
    json_train_dir = 'dataset/json_annotations/train'
    txt_train_dir = 'dataset/labels/train'
    
    # Chemins pour les données de validation (val)
    json_val_dir = 'dataset/json_annotations/val'
    txt_val_dir = 'dataset/labels/val'

    # Exécuter la conversion
    batch_convert(json_train_dir, txt_train_dir)
    batch_convert(json_val_dir, txt_val_dir)
