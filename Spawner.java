import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;
import java.util.concurrent.CountDownLatch;

public class Spawner {
    
    static class SimpleActor extends AbstractActor {
        private final CountDownLatch latch; //declare a variable named latch of type CountDownLatch, final = once assigned cant be changed

        public SimpleActor(CountDownLatch latch) {
            this.latch = latch; //saves latch number inside the actor memory
        }

        @Override
        public void preStart() {
            // Signal we are alive
            latch.countDown();
            // Immediately stop (simulate "spawn and die")
            getContext().stop(getSelf()); //getContext() accesses the Akka system environment managing this actor.
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder().build();
        }

        public static Props props(CountDownLatch latch) {
            return Props.create(SimpleActor.class, () -> new SimpleActor(latch));
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int totalActors = 1_000_000;
        int batchSize = 5_000;
        int numBatches = totalActors / batchSize;

        ActorSystem system = ActorSystem.create("SpawnerSystem");

        System.out.println("--- STARTING SPAWNER (Batched) ---");
        System.out.println("LOG_START:" + System.currentTimeMillis());

        // Loop for the number of batches
        for (int b = 0; b < numBatches; b++) {
            
            CountDownLatch latch = new CountDownLatch(batchSize);

            // 1. Burst: Spawn 5,000 actors
            for (int i = 0; i < batchSize; i++) {
                system.actorOf(SimpleActor.props(latch));
            }

            // 2. Cleanup: Wait for them to finish
            latch.await();
            
            // (Akka cleans up stopped actors automatically in background)
        }

        System.out.println("LOG_END:" + System.currentTimeMillis());
        system.terminate();
    }
}