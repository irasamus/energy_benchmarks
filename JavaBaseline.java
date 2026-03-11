import akka.actor.ActorSystem;

public class JavaBaseline {
    public static void main(String[] args) {
        int nActors = 1_000_000; // Same loop count, but no spawning
        ActorSystem system = ActorSystem.create("BaselineSystem");

        System.out.println("LOG_START:" + System.currentTimeMillis());

        for (int i = 0; i < nActors; i++) {
            // Do nothing (Just loop overhead)
        }

        System.out.println("LOG_END:" + System.currentTimeMillis());
        system.terminate();
    }
}