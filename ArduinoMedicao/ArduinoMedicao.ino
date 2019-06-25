
int i=0,j=0;
const int nsamples = 150; // no of channels
const int tam = 2*nsamples; // tam/2 amostras de cada canal, tam bytes por canal
int sample, CH;

bool procStatus =  false, next = true, last_ch = false;
byte dataVector[2][tam];
byte bytesiluminancia[tam/3], bytestemp1[tam/3], bytestemp2[tam/3]; 
int counter = 0, cnt = 0, a = 0;
int counter70 = 0;
byte buf[tam],low_buffer,high_buffer, buf2[tam/3];



void setup() {
  

//pinMode(A0, INPUT);
//pinMode(A1, INPUT);
//pinMode(A2, INPUT);

// TIMER0: pre-scaler = 256, ctc, 62,5khz
   TCCR0A = 0x02; // CTC mode
   TCCR0B = 0x04; // pre-scaler 256
   OCR0A = 10; // == 28
   TIMSK0 = 0x00;

   PRR &= 0b11111110; // PRADC = 0  

   SREG |= 0b10000000; // global interrupts enabled

   // ADC: 
   ADMUX = 0b01000000;//tensao de referencia selecao do canal igual a 0 
   //ADCSRB = (ADCSRB & 0b11111000) | 0b00000011; // configura trigger
   ADCSRB = (ADCSRB & 0b0000) | 0b00000011; // configura trigger
   ADCSRA = (ADCSRA & 0b00000000) | 0b10101111; //flag de interrupção pre-scalar do ADC = 128 interrupt enable  auto trigger e ad

  TIMSK0 = 0x02;


 Serial.begin(250000);


 // buf e um vetor de dados pra teste
 for(i=0; i<tam;i= i+2){
    buf[i] = 0;
    buf[i+1] = i;
  }
  for(i=0; i<tam/3;i= i+2){
    buf2[i] = 0;
    buf2[i+1] = i;
  }
}

void loop()
{
 

}

ISR(ADC_vect){
  // terminou conversao do ADC, armazena resultado nas variaveis

   low_buffer = ADCL;
   high_buffer = ADCH;
   
    CH = ADMUX &= 0x0F; //canal atual
     
    if (CH<2){
       dataVector[CH][counter] = high_buffer;    //pega sample e guarda em datavector
       dataVector[CH][counter+1] = low_buffer;
    }
    if(CH == 0){
      ADMUX = 0b01000001;   //incrementa canal
      }
    if(CH == 1 && a == 0){
      ADMUX = 0b01000010;                              //incrementa canal para o seguinte (canal 2) e

     }
    else if(CH ==1 && a == 1){
     ADMUX = 0b01000011;                              //canal referente a temp1 é o 3
      }
     else if(CH ==1 && a == 2){
      ADMUX = 0b01000100;                             //canal referente a temp2 é o 4
      }
    if(CH == 2){    //A variavel 'a' dita qual variavel vai ser captada: iluminancia (a = 0), temp1 (a = 1) ou temp2 (a = 2)
       
      bytesiluminancia[counter70] = high_buffer;      //guarda em bytesiluminancia. Tem seu proprio contador, counter70
      bytesiluminancia[counter70 + 1] = low_buffer;   
      a = 1;                                          //indica que na proxima "rodada" de captação de dados, a temp1 que será adquirida, junta a tensão e corrente
      //Serial.println();
      //Serial.println((bytesiluminancia[counter70]<<8)| bytesiluminancia[counter70 + 1]);
    
    }
    else if(CH == 3){ 
      bytestemp1[counter70] = high_buffer;
      bytestemp1[counter70 + 1] = low_buffer;
      a = 2;                                          
    }
      else if(CH == 4){
      bytestemp2[counter70] = high_buffer;
      bytestemp2[counter70 + 1] = low_buffer;
      a = 0;
    }
    if(CH>1){
        last_ch = true;                                 //indica que é o ultimo canal da "rodada"
    }      
    
     if(last_ch == true){
      ADMUX = 0b01000000;  //se chegou no ultimo canal volta pro canal 0 e incrementa counter
      counter = counter + 2;
        if(a == 0){           //se na proxima "rodada" será pega a iluminancia, é porque os 3 canais de 70 bytes ja tiveram seus dados pegos, e
          counter70 = counter70 + 2; //o contador especifico pros de 70 bytes é incrementado
          }
      last_ch = false;       
      }

      if (counter == tam){
        counter = 0;
        counter70 = 0;
        // Envia os bytes 
        Serial.write(254);
        Serial.write(j++);
        if(j==255){j=0;}
        Serial.write(dataVector[0], tam);
        Serial.write(dataVector[1], tam);
        Serial.write(bytesiluminancia, tam/3);
        Serial.write(bytestemp1, tam/3);
        Serial.write(bytestemp2, tam/3);
        
        
    }
  
  }

ISR(TIMER0_COMPA_vect){

 
}
