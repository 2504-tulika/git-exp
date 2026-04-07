package Java.session1.ControlFlow;

public class SumOfEvenNumbers {

    // Method to calculate sum of even numbers
    public static int calculateSum() {
        int sum = 0;
        int i = 1;

        while (i <= 10) {
            if (i % 2 == 0) {
                sum += i;
            }
            i++;
        }

        return sum;
    }

    public static void main(String[] args) {
        int result = calculateSum();
        System.out.println("Sum of even numbers from 1 to 10 is: " + result);
    }
}