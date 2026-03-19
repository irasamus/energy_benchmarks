import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;
import java.util.ArrayList;

public class ThreadRing {

    static class Worker extends AbstractActor {
        private ActorRef next;

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                .match(ActorRef.class, actorRef -> {
                    this.next = actorRef;
                })
                .match(Long.class, n -> {
                    if (n > 0) {
                        next.tell(n - 1L, getSelf());
                    } else {
                        // Added LOG_END before terminating
                        System.out.println("LOG_END:" + System.currentTimeMillis());
                        System.out.println("--- FINISHED ---");
                        getContext().getSystem().terminate();
                    }
                })
                .build();
        }
    }

    public static void main(String[] args) {
        int nActors = 1_000; 
        Long nPasses = 50_000_000L; 

        ActorSystem system = ActorSystem.create("ThreadRingSystem");
        
        System.out.println("--- STARTING THREAD RING ---");
        System.out.println("LOG_START:" + System.currentTimeMillis());

        ArrayList<ActorRef> ring = new ArrayList<>();
        for (int i = 0; i < nActors; i++) {
            ring.add(system.actorOf(Props.create(Worker.class)));
        }

        for (int i = 0; i < nActors; i++) {
            ActorRef current = ring.get(i);
            ActorRef next = ring.get((i + 1) % nActors);
            current.tell(next, ActorRef.noSender());
        }

        ring.get(0).tell(nPasses, ActorRef.noSender());
    }
}
