import akka.actor.AbstractActor;
import akka.actor.ActorSystem;
import akka.actor.Props;
import java.util.concurrent.CountDownLatch;

public class Idle {
    
    static class IdleActor extends AbstractActor {
        private final CountDownLatch latch;

        public IdleActor(CountDownLatch latch) {
            this.latch = latch;
        }

        @Override
        public void preStart() {
            // Signal that this actor is fully initialized and ready to idle
            latch.countDown();
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder().build();
        }

        public static Props props(CountDownLatch latch) {
            return Props.create(IdleActor.class, () -> new IdleActor(latch));
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int nActors = 100_000;
        int durationSeconds = 30; 
        
        ActorSystem system = ActorSystem.create("IdleSystem");
        CountDownLatch latch = new CountDownLatch(nActors);

        for (int i = 0; i < nActors; i++) {
            system.actorOf(IdleActor.props(latch));
        }

        // WAIT here until all 100,000 actors are fully booted and resting
        latch.await();

        // NOW the system is truly idle. Start the measurement.
        System.out.println("LOG_START:" + System.currentTimeMillis());
        
        Thread.sleep(durationSeconds * 1000);

        System.out.println("LOG_END:" + System.currentTimeMillis());

        system.terminate();
    }
}