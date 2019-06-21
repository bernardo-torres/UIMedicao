char inData[20]; // Allocate some space for the string
char inChar; // Where to store the character read
byte index = 0; // Index into array; where to store the character
int i, j=0, k=0;
byte buf[900];

void setup() {
 Serial.begin(9600);
 for (i=0;i<899;i= i+2){
    if(j==0){
      buf[i] = k;      
      buf[i+1] = i;
    } 
    else if(j==1){
      buf[i] = k+1;
      buf[i+1] = 4;
    }
    else if (j==2){
      buf[i] = 5;
      buf[i+1] = 6;  
    }
    if(j == 2){
      j=0;
    }
    else{
        j=j+1;
    }
    if( k == 250){
     k = 0;  
    }
 }
}

void loop()
{
 
  Serial.write(254);
  Serial.write(buf, 900);
  delay(1000);
  
  
  
 
}
