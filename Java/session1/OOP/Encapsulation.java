class BankAccount {

    // Private variable
    private double balance;

    // Getter
    public double getBalance() {
        return balance;
    }

    // Setter
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        } else {
            System.out.println("Invalid deposit amount");
        }
    }
}

public class Encapsulation {

    public static void main(String[] args) {

        BankAccount account = new BankAccount();

        account.deposit(1000);
        System.out.println("Balance: " + account.getBalance());

        account.deposit(-500); // invalid case
    }
}