public class Parent {

    // Method Overloading (same name, different parameters)
    void show(int a) {
        System.out.println("Parent show(int): " + a);
    }

    void show(int a, int b) {
        System.out.println("Parent show(int, int): " + (a + b));
    }

    // Method to override
    void display() {
        System.out.println("Parent display()");
    }
}


