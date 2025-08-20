import argparse
from fichier import structure, tmp

def main():
    parser = argparse.ArgumentParser(
        description="Outils pour fichiers",
        epilog="""Exemple mobile : fichier -s /storage/emulated/0 
        Exemple PC : fichier -s """
    )
    parser.add_argument(
        "-structure", "-s", action="store_true", help="Afficher la structure des fichiers"
    )
    parser.add_argument(
        "-tmp", action="store_true", help="Supprimer tous les fichiers temporaires (*.tmp)"
    )
    parser.add_argument(
        "directory", nargs="?", default=".", help="Répertoire à traiter (défaut: répertoire courant)"
    )
    args = parser.parse_args()

    if args.structure:
        structure.run(args.directory)
    if args.tmp:
        tmp.delete_tmp(args.directory)
