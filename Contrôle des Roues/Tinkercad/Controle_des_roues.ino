/* 	A changer suivant la démonstration choisie : 
	-> Pour une rampe 20rpm/sec			: Moteur 1
*/
#define MOTEUR_DE_DEMONSTRATION 2

// --------------------------------------------
#define HORAIRE true
#define TRIGO false

#define VOIE_A true
#define VOIE_B false

#define NBR_TRACK_USED 1

#define RATIO_REDUCTEUR 84.0 // w(moteur)/w(arbre)
#define NBR_EV_PAR_REV (48 / (2.0 / NBR_TRACK_USED)) // Nombre d'evenement encodeur par revolution

// Ratio pour convertir un nombre d'evenment de l'encodeur en radian (En rad/ev).
#define RATIO_RAD_PAR_EV (1.0/RATIO_REDUCTEUR) * 2*PI / NBR_EV_PAR_REV

#define TEMPS_MS_ENTRE_ACQUISITIONS 5 // 5 ms entre chaque acquisition minimum
#define NBR_ACQUISITION_MOYENNE_TOTAL 10 // Moyenne sur 10 acquisitions

#define FREQ_PID 200 // Fréquence du PID en Hz. (Optimal pour la même fréquence que l'acquisition, une fréquence plus haute est inutile)
#define PERIOD_PID (1.0 / FREQ_PID)

#define RPM_MAX 118.0
#define W_MAX (2*PI*RPM_MAX/60) // Vitesse de rotation maximale en rad/s

class Motor
{
public:
    Motor(int pinInput1, int pinInput2, int pinEnable, int pinEncodeurVoieA, int pinEncodeurVoieB)
        : m_pinInput1(pinInput1), m_pinInput2(pinInput2), m_pinEnable(pinEnable), m_pinEncodeurVoieA(pinEncodeurVoieA), m_pinEncodeurVoieB(pinEncodeurVoieB)
    {
        /* Initialisation des pins */
        pinMode(m_pinInput1, OUTPUT);
        pinMode(m_pinInput2, OUTPUT);
        pinMode(m_pinEnable, OUTPUT);
        pinMode(m_pinEncodeurVoieA, INPUT_PULLUP);
        pinMode(m_pinEncodeurVoieB, INPUT_PULLUP);
        digitalWrite(m_pinEnable, HIGH);

        m_dernierTemps = millis(); // Initialiser le dernier temps avant les appels aux fonctions attach
        m_PID_dernierTemps = millis();
    }

    void setConsigneVitesseRotation(float consigneVitesseRotation)
    {
        m_consigneVitesseRotation = consigneVitesseRotation;
    }

    void setConsigneVitesseRotationRPM(float consigneRPM)
    {
        m_consigneVitesseRotation = 2*PI*consigneRPM / 60.0;
    }

    void setCoefficientsPID(float Kp, float Kd, float Ki)
    {
        m_PID_Kp = Kp;
        m_PID_Kd = Kd;
        m_PID_Ki = Ki;
    }

    void setSensRotation(bool sens)
    {
        m_sensRotation = sens;
    }

    /**
     * @brief sortie : Controle la sortie directement branchée sur le moteur
     * @param puissance : Puissance du moteur en pourcentage
     * @param sens : Sens du moteur : HORAIRE ou TRIGO
     */
    void sortie(int puissance = 100, bool sens = TRIGO)
    {
        int alpha = sens ? map(puissance, 0, 100, 127, 255) : 255 - map(puissance, 0, 100, 127, 255);
        analogWrite(m_pinInput1, 255 - alpha);
        analogWrite(m_pinInput2, alpha);
    }

    void stop()
    {
        digitalWrite(m_pinInput1, LOW);
        digitalWrite(m_pinInput2, LOW);
    }

    int getPositionEncodeur()
    {
        return m_positionEncodeur;
    }

    float getRad()
    {
        return RATIO_RAD_PAR_EV * m_positionEncodeur;
    }

    /**
     * @brief getVitesseRotation
     * @return La vitesse de rotation en radians par seconde
     */
    float getVitesseRotation()
    {
        return m_vitesseRotation;
    }

    int getPinEncodeur(bool voie)
    {
        return (voie == VOIE_A) ? m_pinEncodeurVoieA : m_pinEncodeurVoieB;
    }

    float getCommandePID()
    {
        return m_PID_commande;
    }
    
    float getConsignePID()
    {
        return m_consigneVitesseRotation;
    }

    inline void attachFuncVoieA()
    {
        m_positionEncodeur += (digitalRead(m_pinEncodeurVoieA) == digitalRead(m_pinEncodeurVoieB)) ? 1 : -1;
    }

    inline void attachFuncVoieB()
    {
        m_positionEncodeur += (digitalRead(m_pinEncodeurVoieA) != digitalRead(m_pinEncodeurVoieB)) ? 1 : -1;
    }

    /**
     * @brief calculerVitesseRotation : Actualise le calcul de la vitesse (dérive et fait une moyenne sur les positions de l'encodeur)
     * @return true si cet appel à la fonction a actualisé la valeur moyenne, false sinon
     */
    inline bool calculerVitesseRotation()
    {
        if(millis() - m_dernierTemps < TEMPS_MS_ENTRE_ACQUISITIONS) return false;

        m_vitesseRotationMoyenne += (m_positionEncodeur - m_dernierePositionEncodeur)*RATIO_RAD_PAR_EV / ((millis() - m_dernierTemps) / 1000.0); // taux d'accroissement

        m_dernierePositionEncodeur = m_positionEncodeur;
        m_dernierTemps = millis();

        if(nbrAcquisitionMoyenneActuel >= NBR_ACQUISITION_MOYENNE_TOTAL) {
            m_vitesseRotation = m_vitesseRotationMoyenne / NBR_ACQUISITION_MOYENNE_TOTAL;
            m_vitesseRotationMoyenne = 0;
            nbrAcquisitionMoyenneActuel = 0;

            return true;
        }

        nbrAcquisitionMoyenneActuel++;
        return false;
    }

    /**
     * @brief calculerPID : Calcule la sortie du PID avec la vitesse de rotation actuelle
     */
    bool calculerPID()
    {
        if(millis() - m_PID_dernierTemps < PERIOD_PID) return false; // On respecte la fréquence PID

        m_PID_erreur = m_consigneVitesseRotation - m_vitesseRotation;

        m_PID_sommeErreurs += m_PID_erreur;
        m_PID_deltaErreur = m_PID_erreur - m_PID_derniereErreur;
        m_PID_derniereErreur = m_PID_erreur;

        m_PID_commande =    m_PID_Kp * m_PID_erreur         +
                            m_PID_Kd * m_PID_deltaErreur    +
                            m_PID_Ki * m_PID_sommeErreurs;

        m_PID_commande = min(W_MAX - m_vitesseRotation, max(-W_MAX - m_vitesseRotation, m_PID_commande)); // On évite la saturation

        m_PID_dernierTemps = millis();
      
      	return true;
    }

    /**
     * @brief evaluer : Calcule la vitesse de rotation et evalue le PID
     */
    bool evaluer()
    {
        if(!calculerVitesseRotation()) 	return false; // La vitesse de rotation ne change pas : inutile de calculer le PID et de surcharger l'integrateur.
      	if(!calculerPID())				return false;
      
        sortie((m_vitesseRotation + m_PID_commande) / W_MAX * 100, m_sensRotation); // On contrôle le moteur avec la commande du PID
      	
      	return true;
    }

private:
    int m_pinInput1, m_pinInput2,
        m_pinEnable,
        m_pinEncodeurVoieA, m_pinEncodeurVoieB;

    bool m_sensRotation = TRIGO;

    /* Encodeur et vitesse de rotation */
    /* Testé avec précision float et double : mêmes résultats donc float préférable */
    int m_positionEncodeur          = 0,
        m_dernierePositionEncodeur  = 0;
    float m_vitesseRotation         = 0;

    float m_vitesseRotationMoyenne  = 0;
    int nbrAcquisitionMoyenneActuel = 0;
    unsigned long m_dernierTemps;

    /* PID */
    float m_consigneVitesseRotation = 0;

    float   m_PID_erreur            = 0,
            m_PID_deltaErreur       = 0,
            m_PID_derniereErreur    = 0,
            m_PID_sommeErreurs      = 0;

    float   m_PID_Kp                = 1,
            m_PID_Kd                = 0.1,
            m_PID_Ki                = 0.15;

    float m_PID_commande            = 0; // N'existe que si on veut enregistrer le résultat du PID sans controler le moteur.
    // On controle en fait directement le moteur avec le PID : pas besoin d'enregistrer le résultat. La commande est en rad/s.
    // Attention : la commande de PID est calculée à partir de L'ERREUR donc c'est une correction à ajouter à la sortie deja effective du moteur.
    // Ce n'est pas directement la consigne. Il faut commander avec vitesseRotation + PID_commande.

    unsigned long m_PID_dernierTemps;
};
/* ###################################################################### */
/* ########################### CODE PRINCIPAL ########################### */
/* ###################################################################### */

/*    Define : remplace la première valeur par la deuxième 
valeur dans le code directement avant la compilation. Evite de 
créer des variables qui susbistent à l'exécution. 
*/
#define DELAY 2000

/*    Prototypes : permet de déclarer au compilateur toutes les
fonctions qui se trouvent dans le code, pas de problème d'ordre. 
*/
void attachFuncMoteur1VoieA();
void attachFuncMoteur1VoieB();
void attachFuncMoteur2VoieA();
void attachFuncMoteur2VoieB();

/*
  Fonctions utilisées de l'Arduino :
  - pinMode(numéro du pin, mode de sortie input/output) 
  - digitalWrite(numéro du pin, état 1 ou 0/ HIGH ou LOW) 
  - delay(t) : arrête l'exécution pendant le temps t (ms)
  - map(X,valeur min X,valeur max X, new valeur min X, new valeur max X)
  - analogWrite(numéro pin, valeur) : PWM, voltage = valeur*5/255 (255 = 1 octet) 
*/

Motor *moteur1;
Motor *moteur2;

unsigned long last = millis();


void setup(){
  Serial.begin(9600);
  
  moteur1 = new Motor(6, 11, 7, 3, 9); // input1, input2, enable, encodeur voie A, encodeur voie B
  moteur2 = new Motor(10, 13, 12, 2, 8);
  
  /* Attacher les fronts motant des encodeurs à des fonctions : nécéssaire au fonctionnement de la classe Motor */
  attachInterrupt(digitalPinToInterrupt(moteur1->getPinEncodeur(VOIE_A)), attachFuncMoteur1VoieA, CHANGE);
  
  attachInterrupt(digitalPinToInterrupt(moteur2->getPinEncodeur(VOIE_A)), attachFuncMoteur2VoieA, CHANGE);
  
  
  moteur1->setConsigneVitesseRotationRPM(68); // Consigne de départ
  moteur2->setConsigneVitesseRotationRPM(68); // Consigne de départ
}

void loop()
{
  #if MOTEUR_DE_DEMONSTRATION == 1
  	moteur2->evaluer(); // Calcul du PID et le de la vitesse de rotation, doit etre executé a chaque loop()
  	if(!moteur1->evaluer()) return; // Inutlie d'afficher la vitesse si rien n'a changé
  	
    /* Affichage de la vitesse (première colonne) et de la consigne */
    Serial.print(moteur1->getVitesseRotation() * 30.0 / PI);
    Serial.print(" (Consigne = ");
    Serial.print(moteur1->getConsignePID() * 30.0 / PI);
    Serial.println(" rpm)");
  
  #else // Demonstration avec le 2e moteur
  	moteur1->evaluer();
    if(!moteur2->evaluer()) return; 

    /* Affichage de la vitesse (première colonne) et de la consigne */
    Serial.print(moteur2->getVitesseRotation() * 30.0 / PI);
    Serial.print(" (Consigne = ");
    Serial.print(moteur2->getConsignePID() * 30.0 / PI);
    Serial.println(" rpm)");
  #endif
 
  /* Comportement attendu : 
  Au bout de 2s de simu : 40 rpm;
  Au bout de 4s de simu : 86 rpm; */
  if(millis() - last > 2000) {
    if(millis() - last > 4000) {
      	moteur2->setConsigneVitesseRotationRPM(86);
      	
      	last = millis();
      
      	return;
    }
    moteur2->setConsigneVitesseRotationRPM(40);
  }
  
  /* Comportement de demonstration rampe (moteur 1) */
  // Coefficient directeur de 20rpm par seconde.
  moteur1->setConsigneVitesseRotationRPM(millis() / 50);
  
}

void attachFuncMoteur1VoieA()
{
    moteur1->attachFuncVoieA();
}

void attachFuncMoteur2VoieA()
{
    moteur2->attachFuncVoieA();
}




