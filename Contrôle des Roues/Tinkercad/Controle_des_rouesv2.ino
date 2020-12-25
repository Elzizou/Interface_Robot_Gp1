
// pins
const int pinE12=7;
const int pinI1=6;
const int pinE34=12;
const int pinI4=10;

// codeur optique
int pin_channelA_mot1=9; // pins des channels de l'encodeur du moteur 1
int pin_channelB_mot1=3;
int pin_channelA_mot2=8; // pins des channels de l'encodeur du moteur 2
int pin_channelB_mot2=2;

int position_CO_mot1=0; // CO = Codeur Optique
int position_CO_mot2=0;

float angle_mot1, angle_mot2; // angle des moteurs
float angle_mot1_p = 0.; // angle du moteur 1 dans la boucle précédente
float angle_mot2_p = 0.; // angle du moteur 2 dans la boucle précédente

float vitesse_rot_mot1=0.; // vitesse de rotation du moteur 1
float vitesse_rot_mot2=0.; // vitesse de rotation du moteur 2

// données robot
float espacement_roues=0.1; // en m
float r=0.04; // rayons des roues = 4 cms

// matrice de départ
int i = 0;
int m[] = {255,255,125,100,45,87,158,98};
 


// test PID
/*
float Kp =0.05;
float Ki =50;
float Kd =0;
float PWM_gauche_d;
float PWM_droite_d;
float vit_rot_mot_gauche;
float vit_rot_mot_droit;
int PWM_gauche;
int PWM_droite;
float epsilon_gauche_prev=0;
float epsilon_droite_prev=0;
float i_epsilon_gauche=0;
float i_epsilon_droite=0;
float deltat=500;
float wmax=100; //valeur maximale à laquelle le moteur tourne après réduction
*/



//instructions de lecture
 String msg="",m1="",m2="",msg_a_convertir;
 int sep;

void calcul1();
void calcul2();
void B1Change();
void B2Change();

void setup()
{
    Serial.begin(9600);
  
  // setup des pins pour le controle des moteurs
  pinMode(pinE12, OUTPUT);
  pinMode(pinI1, OUTPUT);
  pinMode(pinE34, OUTPUT);
  pinMode(pinI4, OUTPUT);
  // setup des pins des codeurs optiques
  pinMode(pin_channelA_mot1,INPUT_PULLUP); 
  pinMode(pin_channelB_mot1,INPUT_PULLUP); 
  attachInterrupt(1,B1Change,CHANGE);
  
  pinMode(pin_channelA_mot2,INPUT_PULLUP); 
  pinMode(pin_channelB_mot2,INPUT_PULLUP);  
  attachInterrupt(0,B2Change,CHANGE);
 
}


void loop()
{
  //////
  // Les valeurs d'entrée sont des valeurs entre 0 et 255
  // 0 signigie à fond dans un sens et 255 à fond dans l'autre
  // Les valeurs "_mot1" sont associées au moteur du pin E12
  // Les valeurs "_mot2" sont associées au moteur du pin E34
  //////
 
         
  // PARTIE A : on reçoit les PWM par le Serial Monitor
  
  if (i< ((sizeof(m)/2)+1)){
    int num1=m[i];
    int num2=m[i+1];
    i +=2;
  
  //int calc[] = calculsPWM(Kp,Ki,Kd,num2,num1,vitesse_rot_mot2,vitesse_rot_mot1,epsilon_gauche_prev,epsilon_droite_prev,i_epsilon_gauche,i_epsilon_droite,deltat,wmax)
 
  // PARTIE B : envoi des informations aux 2 moteurs
    
    
  	digitalWrite(pinE12, HIGH);
  	analogWrite(pinI1,num1);
  	digitalWrite(pinE34, HIGH);
  	analogWrite(pinI4,num2);
    
    
  
  // PARTIE C : codeur optique et calcul des vitesses de rotation des moteurs
  // hyp : les encodeurs ont 500 positions (moteur a 500 dents)
  // on détermine le coefficient de réduction expérimentalement 0.39693
 
    /*Serial.print(sizeof(m));
     Serial.print(",");*/
    Serial.print(vitesse_rot_mot1*30.0/PI); // v_mot1 en rpm 
  	Serial.print(",");
  	Serial.println(vitesse_rot_mot2*30.0/PI); // v_mot2 en rpm
     
}
  else{                           //le robot s'arrête au bout de 500ms
    digitalWrite(pinE12,LOW);
    digitalWrite(pinE34,LOW);
  }
  delay(300);      
}

// se déclenche si le channel B du moteur 1 change de valeur
void B1Change(){
  position_CO_mot1 += (digitalRead(pin_channelA_mot1)==digitalRead(pin_channelB_mot1))?-1:1;
  calcul1();
}

// se déclenche si le channel B du moteur 2 change de valeur
void B2Change(){
  position_CO_mot2 += (digitalRead(pin_channelA_mot2)== digitalRead(pin_channelB_mot2))?-1:1;
  calcul2();
}

unsigned long temps1 = millis();
void calcul1(){
  	if(millis() - temps1 < 100) return;
  
  	angle_mot1 = position_CO_mot1*2*PI/500; // en rad 
    vitesse_rot_mot1 = (angle_mot1-angle_mot1_p)/(0.1)*0.2929; //rad.s-1
  
  	angle_mot1_p=angle_mot1; //réactualisation des valeurs
  	temps1 = millis();

}

unsigned long temps2 = millis();
void calcul2(){
  if(millis() - temps2 < 100) return;
  
  	angle_mot2 = position_CO_mot2*2*PI/500; // en rad
    vitesse_rot_mot2 = (angle_mot2-angle_mot2_p)/(0.1)*0.2928; //rad.s-1
    
  	angle_mot2_p=angle_mot2; //réactualisation des valeurs
    temps2 = millis();
}

