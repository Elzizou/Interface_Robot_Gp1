import processing.serial.*;

Serial myPort;  // Create object from Serial class


//Indice des différentes quantités à afficher
int vcom = 0;
int direc = 1;
int vgauche = 2;
int vdroite = 3;
int nGraph = 4;
int vmax = 1;
int nTime = 100;
int index = 1;

float[] Time = new float[nTime];
float[][] Quantity = new float[nGraph][nTime];
color[] quantityColor = new color[nGraph];
String[] bufferLines ;
  
public void settings() {
 //Initialisatiopns graphiques
 size (1000,610);
 smooth();  //On active le lissage
 Quantity[vcom][0] = 0.;
 Quantity[direc] = append(Quantity[direc],0);
 Quantity[vdroite] = append(Quantity[vdroite],0);
 Quantity[vgauche] = append(Quantity[vgauche],0);
 for(int i = 0; i < nTime; i++){
   Time[i] = i*10;
 }
}

void setup()
{
 String portName = Serial.list()[4]; //change the 0 to a 1 or 2 etc. to match your port
 myPort = new Serial(this, portName, 9600);
  
 //Affichage courbe -----------------------

 //Tracé des axes
 fill(0,0,255);
 stroke(#0650E4);
 strokeWeight(2);
  
 //horizontal
 line (100,560,960,560);
 triangle(960, 560, 950, 565, 950, 555);
 text("Vitesse de rotation des roues (rad.s-1)", 60, 40);
 
 //vertical
 line (100,560,100,50);
 triangle(100, 50, 105, 60, 95, 60);
 text("Temps (s)", 910, 595);
 
 quantityColor[vcom] = color(255,0,0);
 quantityColor[direc] = color(0,255,0);
 quantityColor[vgauche] = color(0,0,255);
 quantityColor[vdroite] = color(0,255,255);

}

void draw() {
 // mémorise la chaîne de caractères reçue
 String data = myPort.readStringUntil('\n');
 if (data != null){
   bufferLines = split(data,";");
   decodeEvent();

   for (int k=0; k<nGraph; k++){
     stroke(quantityColor[k]);
     line(100+Time[index-1],560-Quantity[k][Quantity[k].length-2],100+Time[index],560-Quantity[k][Quantity[k].length-1]);
   }
 index = index +1;
 }
 
}

void decodeEvent() { // Method to decode the data received from the Arduino.
  float vcom = 0.;
  float direct = 0.;
  float vdroite = 0.;
  float vgauche = 0.;
  int separator = 0;
  int startData = 0;
  // Data are stored in a vector of strings.
  for (int i=0; i<(bufferLines.length-1); ++i) {
    separator = bufferLines[i].indexOf(" "); // Within one event, data are separated by a space character.
    if (separator > -1) { // If separator has been found, decode the line.
      vcom = (float(bufferLines[i].substring(startData,separator))/vmax)*100; 
      startData = separator+1;
      separator = bufferLines[i].indexOf(" ",startData);
      direct = float(trim(bufferLines[i].substring(startData,separator)))*100;
      startData = separator+1;
      separator = bufferLines[i].indexOf(" ",startData);
      vdroite = float(trim(bufferLines[i].substring(startData,separator)))*100;
      startData = separator+1;
      vgauche = float(trim(bufferLines[i].substring(startData)))*100;
      addData(vcom,direct,vdroite,vgauche); 
    }
  }
}


void addData(float v, float d, float vd, float vg) { // Adding data to the already existing ones. The sizes of vectors are increased by one. 
    Quantity[vcom] = append(Quantity[vcom],v);
    Quantity[direc] = append(Quantity[direc],d);
    Quantity[vdroite] = append(Quantity[vdroite],vd);
    Quantity[vgauche] = append(Quantity[vgauche],vg);
  }
