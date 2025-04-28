import java.util.List;
import java.util.stream.IntStream;

// Record type (Java 16+)
record User(String name, int age) {}

public class Demo {
    public static void main(String[] args) {
        // Stream API example
        List<Integer> squares = IntStream.range(1, 6)
            .map(n -> n * n)
            .boxed()
            .toList();

        System.out.println(squares); // [1, 4, 9, 16, 25]

        // Pattern matching (Java 21+)
        Object obj = "Hello";
        if (obj instanceof String s) {
            System.out.println(s.toUpperCase()); // HELLO
        }
    }
}
