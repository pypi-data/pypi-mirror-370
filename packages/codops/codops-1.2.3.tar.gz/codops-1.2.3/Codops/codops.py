# codops/cli.py

import argparse
from .run import run as run_command  
from .explain import explain as explain_command      
from .suggest import suggest as suggest_command 
from .readme import generate as readme_command 
from .doc_explain import docexp as docexp_command 
from .doc_suggest import docsug as docsug_command 
from .help import help as help_command
from .summary import generate_summary as summary_command
from .app import launch_app 

def main():
    parser = argparse.ArgumentParser(description='Codops CLI Tool')
    parser.add_argument('command', nargs='?', default=None, help='Command to execute')
    parser.add_argument('args', nargs='*', help='Arguments supplémentaires pour la commande')
    args = parser.parse_args()

    if args.command is None:
        # Si aucune commande n'est spécifiée, lancer l'application
        launch_app()
        return
    if args.command == 'run':
        if len(args.args) < 3:
            print("La commande 'run' nécessite deux arguments.")
        else:
            run_command(args.args[0], args.args[1], args.args[2]) 

        
    elif args.command == 'explain':
        if len(args.args) < 1:
            print("La commande 'explain' nécessite un argument.")
        else:
            explain_command(args.args[0])
           
    elif args.command == 'suggest':
        if len(args.args) < 1:
            print("La commande 'suggest' nécessite deux arguments.")
        else:
            suggest_command(args.args[0])

    elif args.command == 'help':
        help_command()
    elif args.command == 'readme':
        if len(args.args) < 2:
            print("La commande 'readme' nécessite deux arguments.")
        else:
            readme_command(args.args[0], args.args[1])  

    elif args.command == 'summary':
        if len(args.args) < 1:
            print("La commande 'summary' nécessite un argument.")
        else:
            summary_command(args.args[0])

    elif args.command == 'docsug':
        if len(args.args) < 2:
            print("La commande 'docsug' nécessite deux arguments.")
        else:
            docsug_command(args.args[0], args.args[1])

    elif args.command == 'docexp':
        if len(args.args) < 2:
            print("La commande 'docexp' nécessite deux arguments.")
        else:
            docexp_command(args.args[0], args.args[1])
    else:
        print("Unknown command")

if __name__ == '__main__':
    main()