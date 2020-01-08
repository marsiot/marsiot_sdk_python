
#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>

#define RETRY_MAX  5000

unsigned int data_buf;
int error_code = 0;
int pin_numb = 1; //注意这里的gpio-1是指wiringPi的gpio命名方式，对应的BCM的命名方式应该是gpio-18
 
int read_data(void) {
    unsigned char crc; 
    int i, count;

 
    count = 100;
    while(digitalRead(pin_numb) && count>0) {
        pinMode(pin_numb, OUTPUT); 
        digitalWrite(pin_numb, 1); 
        delayMicroseconds(4);
        digitalWrite(pin_numb, 0);
        delay(25);
        digitalWrite(pin_numb, 1); 
        delayMicroseconds(60); 

        pinMode(pin_numb, INPUT); 
        pullUpDnControl(pin_numb, PUD_UP);
	
    	count--;
    }

    if (count == 0) {
        error_code = __LINE__;
        return 1;
    }

    count = RETRY_MAX;
    while(!digitalRead(pin_numb) && count>0) {count--;}
    if (count == 0) {
        error_code = __LINE__;
        return 1;
    }

    delayMicroseconds(80);

    for (i=0; i<32; i++) {

        count = RETRY_MAX;		
        while(digitalRead(pin_numb) && count>0) {count--;}
        if (count == 0) {
            error_code = __LINE__;
            return 1;
        }

        count = RETRY_MAX;		
        while(!digitalRead(pin_numb) && count>0) {count--;}
        if (count == 0) {
            error_code = __LINE__;
            return 1;
        }

        delayMicroseconds(32);
        data_buf*=2;
        if(digitalRead(pin_numb)==1) {
            data_buf++;
        }
    }
 
    for(i=0;i<8;i++) {

        count = RETRY_MAX;		
        while(digitalRead(pin_numb) && count>0) {count--;}
        if (count == 0) {
            error_code = __LINE__;
            return 1;
        }

        count = RETRY_MAX;		
        while(!digitalRead(pin_numb) && count>0) {count--;}
        if (count == 0) {
            error_code = __LINE__;
            return 1;
        }

        delayMicroseconds(32);
        crc*=2;  
        if(digitalRead(pin_numb)==1) {
            crc++;
        }
    }
    return 0;
}
 
int main (void) {
    if (-1 == wiringPiSetup()) {
        error_code = __LINE__;
        printf("error %d", error_code);
        return 1;
    }
 
    pinMode(pin_numb,OUTPUT); 
    digitalWrite(pin_numb, 1);

    if (read_data() == 0) {
        printf("%d.%d %d.%d",
	    (data_buf>>24)&0xff,(data_buf>>16)&0xff,
	    (data_buf>>8)&0xff,data_buf&0xff); 
    } else {
        printf("error %d", error_code);
	return -1;
    }

    return 0;
}
