# 3DS-Controller
Un projet dans le but d'utiliser sa 3DS comme une manette.

## Prérequis
- Une 3DS possédant un Homebrew
- Installer vJoy, disponible ici : http://vjoystick.sourceforge.net/site/index.php/download-a-install/download, ainsi que de le configurer avec "Configure vJoy" et définir 16 boutons pour le contrôleur 1

## Installation
Pour installer 3DS Controller, télécharger le dossier .zip de l'application disponible dans "releases": https://github.com/Faraphel/3DS-Controller/releases.
Déplacer le fichier "3DS/3DSController.cia" et "3DS/3DSController.ini" sur votre carte SD respectivement dans le dossier "cias" et dans la racine.
Avant d'éjecter votre carte SD, lancer l'application avec "Controller 3DS.exe", et dans le menu paramètre, récupérer votre IP local (commençant généralement par 192.168.x.x).
Modifier le fichier "3DS/3DSController.ini" pour que l'IP corresponde. 

(Conseil : il est très conseillé de définir l'IP de votre PC comme étant fixe afin d'éviter de devoir redéfinir l'IP à chaque fois que vous souhaitez utiliser l'application)

Seulement après ces manipulations, vous pouvez retirer la carte SD et la réinstaller dans votre 3DS. Vous pouvez à présent installer l'application depuis FBI. Si la manipulation
a été correctement effectuée, l'interface devrait afficher les entrées de la 3DS.

## Configuration
Pour l'instant, l'application propose les paramètres suivant :
- Définir les bordures de l'écran tactile

  cette option vous permet de délimiter la région qui va correspondre à l'écran tactile : par exemple, si vous utilisiez citra, utilisez clic gauche sur la zone en haut à gauche
  de l'écran tactile de l'émulateur, puis clic droit sur la zone en bas à droite. Cela permettra de "synchroniser" les deux écrans tactiles.
  
- Couleur d'arrière plan

  si vous souhaitez faire une incrustation de l'interface de la 3DS, il est possible de changer la couleur de l'arrière plan. 
