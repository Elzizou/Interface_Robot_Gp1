
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



//instructions de lecture
 String msg="",m1="",m2="",msg_a_convertir;
 int num1=-1,num2=-1;
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
  
  
  readSerialPort();
  /*
  if (msg.equals("")){
    digitalWrite(pinE12, LOW);
  	digitalWrite(pinE34, LOW);
  }
  else{*/
  if (msg.length()>0 && msg.indexOf(';')!=msg.lastIndexOf(';')){
  	msg_a_convertir=msg.substring(0,msg.indexOf(';'));
  	msg=msg.substring(msg.indexOf(';')+1,msg.length());
  }
  else{
  	msg_a_convertir=msg.substring(0,msg.indexOf(';'));
    msg="";
  }
  
  convertMsgToMultiCmd();
  
  //if (num1== -1 && num2 == -1){ //on s'en fout une fois que le tableau est codé
    
 	
  // PARTIE B : envoi des informations aux 2 moteurs
  	digitalWrite(pinE12, LOW);
  	analogWrite(pinI1,num1);
  	digitalWrite(pinE34, LOW);
  	analogWrite(pinI4,num2);
    
    
  
  // PARTIE C : codeur optique et calcul des vitesses de rotation des moteurs
  // hyp : les encodeurs ont 500 positions (moteur a 500 dents)
  // on détermine le coefficient de réduction expérimentalement 0.39693
    digitalWrite(pinE12,HIGH);
  	analogWrite(pinI1,num1);
  	digitalWrite(pinE34, HIGH);
  	analogWrite(pinI4,num2);
    Serial.print(vitesse_rot_mot1*30.0/PI); // v_mot1 en rpm 
  	Serial.print(",");
  	Serial.println(vitesse_rot_mot2*30/PI); // v_mot2 en rpm
    
  	delay(500); // Wait for 100 millisecond(s) 

    
  
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

//permet de lire la valeur entrée dans le monitor 
void readSerialPort(){
  while (Serial.available()) {
    delay(10);
    if (Serial.available()>0){
      char c = Serial.read();
      
      msg += c;
    }
  }
  Serial.flush();
}

// permet de convertir la chaine de caracères du type 255,255 
// en 2 valeurs à renvoyer au moteur 1 et 2 
void convertMsgToMultiCmd(){
  Serial.println(msg_a_convertir);
  if (msg_a_convertir.length() >0) {
    sep = msg_a_convertir.indexOf(',');
    
    // on suppose l'instruction du type 255,255      
    m1 = msg_a_convertir.substring(0, sep); //on obtient la valeur de PWM Motor 1
    m2 = msg_a_convertir.substring(sep+1, msg.length()); //on obtient la valeur de PWM Motor 2 
    
    //convertit un string en int
    char carray1[6]; 
    m1.toCharArray(carray1, sizeof(carray1));
    num1 = atoi(carray1);
    
    //convertit un string en int
    char carray2[6]; 
    m2.toCharArray(carray2, sizeof(carray2));
    num2 = atoi(carray2);
     
    msg_a_convertir="";
}
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
