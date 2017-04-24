int global_int;
char global_char;

void test(int a,int b,int c){
a = a && b;
b = b || c;
c = !c;
}

void main(){
int a;
int b;
int c;
int arr [10];
int i;
char ch;

a = 6;
b = -a;
c = 2*a+b;

for(i=0;i<10;i+=1){
arr[i]=i;
}

if(a>b){
b= b+10;
}else{
a= a+10;
}

while(a+b < c){
c = c -1;
}

ch = 'f';

test(a,b,c);

}