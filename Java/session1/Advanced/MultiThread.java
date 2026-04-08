package Java.session1.Advanced;

class MyThread extends Thread {

    // Task 1
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println("Thread Task: " + i);
        }
    }
}

public class MultiThread {

    public static void main(String[] args) {

        // Create thread object
        MyThread t1 = new MyThread();

        // Start thread
        t1.start();

        // Main thread task
        for (int i = 1; i <= 5; i++) {
            System.out.println("Main Task: " + i);
        }
    }
}