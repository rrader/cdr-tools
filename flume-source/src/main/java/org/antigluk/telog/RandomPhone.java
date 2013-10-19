package org.antigluk.telog;

import java.text.DecimalFormat;
import java.util.Random;

public class RandomPhone {
    public static String nextPhone() {
        Random rand = new Random();
        int ccode = 38;
        int ocode = (0) * 100 + (rand.nextInt(10) * 10) + rand.nextInt(10);
        int num2 = rand.nextInt(743);
        int num3 = rand.nextInt(10000);

        DecimalFormat dfcode = new DecimalFormat("+#"); // country code
        DecimalFormat df3 = new DecimalFormat("000"); // 3 zeros
        DecimalFormat df4 = new DecimalFormat("0000"); // 4 zeros

        String phoneNumber = dfcode.format(ccode) + "-" + df3.format(ocode) + "-" + df3.format(num2) + "-" + df4.format(num3);
        return phoneNumber;
    }
}
