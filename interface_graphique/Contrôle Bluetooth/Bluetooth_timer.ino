
/*************************************************************
  Download latest Blynk library here:
    https://github.com/blynkkk/blynk-library/releases/latest

  Blynk is a platform with iOS and Android apps to control
  Arduino, Raspberry Pi and the likes over the Internet.
  You can easily build graphic interfaces for all your
  projects by simply dragging and dropping widgets.

    Downloads, docs, tutorials: http://www.blynk.cc
    Sketch generator:           http://examples.blynk.cc
    Blynk community:            http://community.blynk.cc
    Follow us:                  http://www.fb.com/blynkapp
                                http://twitter.com/blynk_app

  Blynk library is licensed under MIT license
 *************************************************************/

#define BLYNK_PRINT Serial
#include <Blynk.h>
#include <BlynkSimpleSerialBLE.h>

#include <SoftwareSerial.h>
SoftwareSerial SerialBLE(10, 11);                        // RX, TX

char auth[] = "4eecbbc79f4e4ac89f92227a3946eda3";        // Permet la connexion à l'application

String dataBunch = "";                                   // String used to store measurements.
float accmax = 0.5;                                      //Accélération maximale autorisée
float vmax = 1;                                          //Vitesse maximale autorisée
float vdroite, vgauche, vcom;                            //Vitesse de chaque moteur et vitesse de commande
float new_vcom, direct, new_vdroite, new_vgauche;        //Direct représente la direction du robot (négative -> à droite, positive -> à gauche)


SimpleTimer timer;



//Permet de vérifier l'accélération et de la corriger
float accvalide(float new_v, float v){
  
  float acc = (abs(new_v - v))*10;
  
  if( acc > accmax){
    new_v = v + ((new_v - v)*0.1*accmax)/abs(new_v - v);
    return new_v;
    }
  return new_v;
  }


//Permet de récupérer le pourcentage de la vitesse maximale
BLYNK_WRITE(V2) {
  float vit = param.asFloat()/100;
  new_vcom = vit*vmax;
  vcom = new_vcom;
  }



//Permet de récupérer la commande de direction
BLYNK_WRITE(V1) {
  direct = param[0].asFloat()/100;
}



//Actualise les vitesses de chaque moteur en fonction de la vitesse de commande et de la direction voulue
void vitesses(){

  if(direct >= 0) {
    new_vdroite = vcom;
    new_vgauche = vcom*(1 - direct);
  }

  else{
    new_vgauche = vcom;
    new_vdroite = vcom*(1 + direct);
  }

  //On vérifie l'accélération
  new_vgauche = accvalide(new_vgauche, vgauche);
  new_vdroite = accvalide(new_vdroite, vdroite);
    
  //On enregistre les valeurs
  vdroite = new_vdroite;
  vgauche = new_vgauche;
    
  dataBunch += String(vcom) + " " + String(direct) + " " + String(vdroite) + " " + String(vgauche) + ";";
  Serial.println(dataBunch); // Send data to the computer.
  Serial.flush(); // Cleaning the serial port.
  dataBunch = "";
}

  
void setup()
{
  // Debug console
  Serial.begin(9600);

  //Etablissement de la connexion
  SerialBLE.begin(9600);
  Blynk.begin(SerialBLE, auth);

  //On règle un timer qui rafraîchira les vitesses
  timer.setInterval(100, vitesses);

  Serial.println("Waiting for connections...");
}

void loop()
{
  //Blynk s'occupe des widgets sur l'application et timer lance le timer
  Blynk.run();
  timer.run();
}
