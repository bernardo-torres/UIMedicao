
int i=0;
byte buf[400];
const int N = 3; // no of channels
const int tam = 400; // tam/2 amostras de cada canal, tam bytes por canal
int sample, CH;

bool procStatus =  false;
byte dataVector[N][tam];
int counter = 0, cnt = 0;


void setup() {
  

//pinMode(A0, INPUT);
//pinMode(A1, INPUT);
//pinMode(A2, INPUT);



ADMUX = 0x00;
ADMUX |= 0b01000000; // REFS[1:0]=01, set voltage reference tp AVcc

ADCSRA = 0x00;
ADCSRA |= 0x07; // ADPS[2:0] = 111, prescaler 128
ADCSRA |= 0x08; // ADIE = 1 enable ADC interrupts
ADCSRA |= 0x20; // ADATE = 1 enable auto trigger

ADCSRB = 0;
//ADCSRB = 0x03; // ACME = 0, ADTS[2:0] = 011 Timer/Counter0 Compare Match A
ADCSRB = (ADCSRB & 0b11111000) | 0b00000011;

DIDR0 = 0xFF; // Disable ADC digital input buffers

/* Timer */
TCCR0A = 0x02;  // normal port, CTC mode
TCCR0B = 0x00;

TCNT0 = 0;
OCR0A = 100; //compare register A
OCR0B = 0; //compare register B

PRR &= 0b11111110; // PRADC = 0
SREG |= 0x80; // Enable mu global interrupts

ADCSRA |= 0x80; // ADEN = 1 enable converter
ADCSRA |= 0x0; // ADSC = 1 start conversion


 Serial.begin(250000);

 TCCR0B = 0x04; // start the timer CLIO/256 = 62,5kHz
 TIMSK0 = 0x02; //  OCIE0A = 1, interrupr compare match A

 // buf e um vetor de dados pra teste
 for(i=0; i<tam;i++){
    buf[i] = i;
  }
}

void loop()
{
 
  //Serial.write(254);
  //Serial.write(buf, 900);
  //delay(1000);
   if (procStatus == true){
     //Serial.write(254);
    // Serial.write(dataVector[0], tam);
     //Serial.write(dataVector[1], tam);
     //Serial.write(buf, tam);
    }
   //noInterrupts();
   procStatus = false;
   //interrupts();
 // if(TCNT0%25==0) Serial.println(TCNT0);
}

ISR(ADC_vect){

  int sample, CH;
  //sample = ADCL;   //le byte inferior
  //sample += ADCH<<8;  // le byte superior

  if(procStatus == false){
    CH = ADMUX &= 0x0F; //canal atual
    dataVector[CH][counter] = ADCH;    //pega sample e guarda em datavector
    dataVector[CH][counter+1] = ADCL;
    


    if(++CH < N){
      ADMUX += 1;   //incrementa canal
      }
     else{
      ADMUX &= 0xF0;  //se chegou no ultimo canal volta pro canal 0 e incrementa counter
      counter = counter + 2;
      }

      if (counter == tam){
        counter = 0;
        procStatus = true;
        Serial.print("CH = ");
      Serial.print(CH);
      Serial.print(" ");
      Serial.print(ADCSRA);
      Serial.print(" ");
      Serial.println((ADCH<<8)|ADCL);
        }
    }
    //Serial.println(TCNT0);
  }

ISR(TIMER0_COMPA_vect){
    // clears the flag (??)
      //Serial.println((ADCH<<8)|ADCL);
      Serial.println(ADCSRA);
}
