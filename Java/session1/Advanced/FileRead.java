import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class FileRead {

    public static void main(String[] args) {

        try {
            // Create file object
            File file = new File("sample.txt");

            // Scanner to read file
            Scanner sc = new Scanner(file);

            System.out.println("File Content:");

            // Read file line by line
            while (sc.hasNextLine()) {
                String line = sc.nextLine();
                System.out.println(line);
            }

            sc.close();

        } catch (FileNotFoundException e) {
            System.out.println("Error: File not found!");
        }
    }
}