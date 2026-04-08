

public class Polymorphism {

    public static void main(String[] args) {

        Parent obj = new Child(); // runtime polymorphism

        // Overloading
        obj.show(10);
        obj.show(10, 20);

        // Overriding
        obj.display();
    }
}