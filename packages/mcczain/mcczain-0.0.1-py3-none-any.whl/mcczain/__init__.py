def P1():
    print("""#include <stdio.h>

int main()
{
    int a, b, s, d, p, r;
    float q;

    printf("Enter 2 integer values: ");
    scanf("%d %d", &a, &b);

    s = a + b;
    d = a - b;
    p = a * b;
    r = a / b;              // integer division
    q = (float) a / b;      // float division

    printf("%d + %d = %d\n", a, b, s);
    printf("%d - %d = %d\n", a, b, d);
    printf("%d * %d = %d\n", a, b, p);
    printf("%d / %d = %d (integer division)\n", a, b, r);
    printf("%d / %d = %.2f (float division)\n", a, b, q);

    return 0;
}
 """)



def P2():
    print("""
#include <stdio.h>
int main()
{
    int emp_id;
    char type;
    float basic, da, hra, cca, pf, gross_sal, net_sal;
    
    printf("Enter employee ID: ");
    scanf("%d", &emp_id);

    printf("Enter employee Type (A/C): ");
    scanf(" %c", &type);   // space before %c skips leftover newline

    if((type != 'A') && (type != 'a') && (type != 'C') && (type != 'c'))
    {
        printf("\nEnter valid employee Type");
    }
    else {
        printf("\nEnter basic pay: ");
        scanf("%f", &basic);

        if(type == 'A' || type == 'a')
        {
            da = basic * 35 / 100;
            hra = basic * 25 / 100;
            cca = 400;
        }
        else
        {
            da = basic * 25 / 100;
            hra = basic * 20 / 100;
            cca = 200;
        }

        pf = basic * 12 / 100;
        gross_sal = basic + da + hra + cca;
        net_sal = gross_sal - pf;

        printf("\n-------------");
        printf("\nABC Organisation");
        printf("\nPay slip");
        printf("\n--------------");
        printf("\nEmployee ID: %d", emp_id);
        printf("\nEmployee Type: %c", type);
        printf("\nBasic pay: %.2f", basic);
        printf("\nDearness allowance: %.2f", da);
        printf("\nHouse rent allowance: %.2f", hra);
        printf("\nCity compensatory allowance: %.2f", cca);
        printf("\nGross salary: %.2f", gross_sal);
        printf("\nDeduction (PF): %.2f", pf);
        printf("\n-------------------");
        printf("\nNet salary: %.2f", net_sal);
        printf("\n------------");
    }

    return 0;
}
 """)



def P3():
    print("""
#include <stdio.h>
int main()
{
    int reg_no, c1, c2, c3, lang, eng, total;
    float per;
    printf("Enter the register no: ");
    scanf("%d", &reg_no);
    printf("\nEnter the marks of core 1, core 2, core 3, language, english: ");
    scanf("%d %d %d %d %d", &c1, &c2, &c3, &lang, &eng);
    
    total = c1+c2+c3+lang+eng;
    per = total/5.0;
    printf("\n------------------");
    printf("\nMCC BCA - 1");
    printf("\n------------------");
    printf("\n1st BCA Marks card");
    printf("\nDBMS: %d", c1);
    printf("\nC Programming: %d", c2);
    printf("\nMaths: %d", c3);
    printf("\nLanguage: %d", lang);
    printf("\nEnglish: %d", eng);
    if(per>75)
    printf("\n\nDistinction");
    else if(per>60)
    printf("\nFirst class");
    else if(per>50)
    printf("\nSecond class");
    else if(per>40)
    printf("\nThrid class");
    else
    printf("\nfail");
}
""")



def P4():
    print("""#include <stdio.h>
#include <string.h>
#include <ctype.h> 

int main()
{
    int MID, prev, pres;
    float bamt, units;
    char type;

    printf("Enter the meter ID: ");
    scanf("%d", &MID);

    printf("\nEnter the Previous reading: ");
    scanf("%d", &prev);

    printf("\nEnter the Present reading: ");
    scanf("%d", &pres);

    printf("\nEnter the Customer Type (D: Domestic, B: Business): ");
    scanf(" %c", &type);

    if(toupper(type) != 'D' && toupper(type) != 'B')
    {
        printf("Enter valid customer type\n");
        return 0;
    }

    units = pres - prev;

    if(toupper(type) == 'D')  // Domestic
    {
        if(units <= 200)
            bamt = units * 2.00;
        else if(units <= 400)
            bamt = 200 * 2.00 + (units - 200) * 4.50;
        else
            bamt = 200 * 2.00 + 200 * 4.50 + (units - 400) * 8.00;
    }
    else   // Business
    {
        if(units <= 200)
            bamt = units * 8.00;
        else if(units <= 400)
            bamt = 200 * 8.00 + (units - 200) * 15.00;
        else
            bamt = 200 * 8.00 + 200 * 15.00 + (units - 400) * 22.00;
    }

    printf("\n-------------");
    printf("\nBESCOM BILL");
    printf("\nMeter ID: %d", MID);
    printf("\nCustomer type: %c", toupper(type));
    printf("\nPrevious Reading: %d", prev);
    printf("\nPresent Reading: %d", pres);
    printf("\nUnits Consumed: %.2f", units);
    printf("\nBill Amount: %.2f\n", bamt);

    return 0;
}
 """)


def P5():
    print("""#include <stdio.h>

int main()
{
    int r, num;
    printf("Enter an integer: ");
    scanf("%d", &num);

    r = num % 10; // rightmost digit

    printf("\nRightmost digit of %d = %d", num, r);

    switch (r) {
        case 0: printf("\nZero"); break;
        case 1: printf("\nOne"); break;
        case 2: printf("\nTwo"); break;
        case 3: printf("\nThree"); break;
        case 4: printf("\nFour"); break;
        case 5: printf("\nFive"); break;
        case 6: printf("\nSix"); break;
        case 7: printf("\nSeven"); break;
        case 8: printf("\nEight"); break;
        case 9: printf("\nNine"); break;
    }

    return 0;
}
 """)
    

def P6():
    print("""#include <stdio.h>

int main()
{
    int n, rev = 0,rem;
    
    printf("Enter the integer: ");
    scanf("%d", &n);
    
    while(n != 0)
    {
        rem = n%10;
        rev = rev * 10 + rem;
        n = n/10;
    }
    printf("The reverse of %d is %d", n, rev);
}
 """)


def P7():
    print("""#include <stdio.h>

int main()
{
    int ctr, F1 = 0, F2 = 1, s, n;
    
    printf("How many numbers to generate: ");
    scanf("%d", &n);
    
    if(n <= 0)
        printf("\nEnter a positive number");
    else if(n == 1)
        printf("\nFibonacci Series:\n%d", F1);
    else
    {
        printf("\nFibonacci Series");
        printf("\n----------------\n");
        printf("%d %d", F1, F2);  // first two numbers
        
        for(ctr = 3; ctr <= n; ctr++)
        {
            s = F1 + F2;
            printf(" %d", s);   // print on same line
            F1 = F2;
            F2 = s;
        }
        printf("\n---------\n");
    }
    
    return 0;
}
 """)


def P8():
    print("""#include <stdio.h>
#include <math.h>

int main()
{
    int lim, n, flag, f;
    printf("PRIME NUMBERS");
    printf("\nUpto?");
    scanf("%d", &lim);
    if(lim==0)
    printf("\nYou have entered zero");
    else if(lim==1)
    printf("\nNeither prime nor composite");
    else
    {
        for(n=2;n<=lim;n++)
        {
            flag=0;
            for(f=2;f<=sqrt(n);f++)
            {
                if(n%f==0)
                {
                    flag=1;
                    break;
                }
            }
            if(flag==0)
            printf("\n%d\n",n);
        }
    }
}
""")
