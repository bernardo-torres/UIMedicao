
int i=0;
byte buf[210],low_buffer,high_buffer, buf2[70];
const int nsamples = 147; // no of channels
const int tam = 2*nsamples; // tam/2 amostras de cada canal, tam bytes por canal
int sample, CH;

bool procStatus =  false, next = true, last_ch = false;
byte dataVector[2][tam];
byte bytesiluminancia[tam/3], bytestemp1[tam/3], bytestemp2[tam/3]; 
int counter = 0, cnt = 0, a = 0;
int counter70 = 0;


void setup() {
  

//pinMode(A0, INPUT);
//pinMode(A1, INPUT);
//pinMode(A2, INPUT);

// TIMER0: pre-scaler = 64, ctc, 8.9khz
   TCCR0A = 0x02; // CTC mode
   TCCR0B = 0x04; // pre-scaler 1256
   OCR0A = 14; // == 28
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
  for(i=0; i<70;i++){
    buf2[i] = i;
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
     
    if (CH<2){
       dataVector[CH][counter] = high_buffer;    //pega sample e guarda em datavector
       dataVector[CH][counter+1] = low_buffer;
    }
    if(CH == 0){
      ADMUX += 1;   //incrementa canal
      }
    
    if(CH == 1 && a == 0 && next == true){    //A variavel 'a' dita qual variavel vai ser captada: iluminancia (a = 0), temp1 (a = 1) ou temp2 (a = 2)
      
      ADMUX = ADMUX + 1;                              //incrementa canal para o seguinte (canal 2) e
      bytesiluminancia[counter70] = high_buffer;      //guarda em bytesiluminancia. Tem seu proprio contador, counter70
      bytesiluminancia[counter70 + 1] = low_buffer;   
      a = 1;                                          //indica que na proxima "rodada" de captação de dados, a temp1 que será adquirida, junta a tensão e corrente
      next = false;                                   //impede que entre no proximo 'if' antes da hora
    }
    if(CH == 1 && a == 1 && next == true){
      
      ADMUX = ADMUX + 2;                              //canal referente a temp1 é o 3
      bytestemp1[counter70] = high_buffer;
      bytestemp1[counter70 + 1] = low_buffer;
      a = 2;                                          
      next = false;
    }
      if(CH == 1 && a == 2 && next == true){
      
      ADMUX = ADMUX + 3;                             //canal referente a temp2 é o 4
      bytestemp2[counter70] = high_buffer;
      bytestemp2[counter70 + 1] = low_buffer;
      a = 0;
      next = false;
    }
    if(CH>1){
        last_ch = true;                                 //indica que é o ultimo canal da "rodada"
    }      
    
     if(last_ch == true){
      ADMUX &= 0xF0;  //se chegou no ultimo canal volta pro canal 0 e incrementa counter
      counter = counter + 2;
        if(a == 0){           //se na proxima "rodada" será pega a iluminancia, é porque os 3 canais de 70 bytes ja tiveram seus dados pegos, e
          counter70 = counter70 + 2; //o contador especifico pros de 70 bytes é incrementado
          }
      next = true;           //habilita a entrada no proximo 'if' em questão
      last_ch = false;       
      }

      if (counter == tam){
        counter = 0;
        counter70 = 0;
        // Envia os bytes 
        Serial.write(254);
        Serial.write(dataVector[0], tam);
        Serial.write(dataVector[1], tam);
        Serial.write(bytesiluminancia, tam/3);
        Serial.write(bytestemp1, tam/3);
        Serial.write(bytestemp2, tam/3);
        
    }
}
