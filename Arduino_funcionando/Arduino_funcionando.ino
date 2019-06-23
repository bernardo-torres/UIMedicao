
int i=0;
byte buf[400],low_buffer,high_buffer;
const int N = 5; // no of channels
const int tam = 210; // tam/2 amostras de cada canal, tam bytes por canal
int sample, CH;

bool procStatus =  false;
byte dataVector[3][tam];
int counter = 0, cnt = 0;


void setup() {
  

//pinMode(A0, INPUT);
//pinMode(A1, INPUT);
//pinMode(A2, INPUT);

// TIMER0: pre-scaler = 64, ctc, 8.9khz
   TCCR0A = 0x02; // CTC mode
   TCCR0B = 0x04; // pre-scaler 1256
   OCR0A = 19; // == 28
   TIMSK0 = 0x00;

   PRR &= 0b11111110; // PRADC = 0  

   SREG |= 0b10000000; // global interrupts enabled

   // ADC: 
   ADMUX = 0b01000000;//tensao de referencia selecao do canal igual a 0 
   ADCSRB = (ADCSRB & 0b11111000) | 0b00000011; // configura trigger
   ADCSRA = (ADCSRA & 0b00010000) | 0b10101111; //flag de interrupção pre-scalar do ADC = 128 interrupt enable  auto trigger e ad

  TIMSK0 = 0x02;


 Serial.begin(250000);


 // buf e um vetor de dados pra teste
 for(i=0; i<tam;i++){
    buf[i] = i;
  }
}

void loop()
{
 

}

ISR(ADC_vect){
  // terminou conversao do ADC, armazena resultado nas variaveis
  low_buffer = ADCL;
   high_buffer = ADCH;
  
  }

ISR(TIMER0_COMPA_vect){

    CH = ADMUX &= 0x0F; //canal atual
    dataVector[CH][counter] = high_buffer;    //pega sample e guarda em datavector
    dataVector[CH][counter+1] = low_buffer;
    
    if(++CH < 3){
      ADMUX += 1;   //incrementa canal
      }
     else{
      ADMUX &= 0xF0;  //se chegou no ultimo canal volta pro canal 0 e incrementa counter
      counter = counter + 2;
      }

      if (counter == tam){
        counter = 0;
        // Envia os bytes 
        Serial.write(254);
        Serial.write(dataVector[0], tam);
        Serial.write(dataVector[1], tam);
        Serial.write(dataVector[2], tam);
        
    }
}
