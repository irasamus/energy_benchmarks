import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;

public class Message { // Class name matches file name "Message.java"

    // 1. The Receiver Actor (Ponger)
    static class Ponger extends AbstractActor {
        @Override
        public Receive createReceive() {
            return receiveBuilder()
                // When I receive "ping", send back "pong"
                .matchEquals("ping", s -> getSender().tell("pong", getSelf()))
                .build();
        }
    }

    // 2. The Sender Actor (Pinger)
    static class Pinger extends AbstractActor {
        private final ActorRef target;
        private int count;
        private final int limit;
        private final long startTime;

        public Pinger(ActorRef target, int limit) {
            this.target = target;
            this.limit = limit;
            this.startTime = System.currentTimeMillis();
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                // Start the process
                .matchEquals("start", s -> target.tell("ping", getSelf()))
                
                // Handle the reply
                .matchEquals("pong", s -> {
                    count++;
                    if (count < limit) {
                        // Keep going
                        target.tell("ping", getSelf());
                    } else {
                        // Finished
                        long end = System.currentTimeMillis();
                        System.out.println("--- FINISHED ---");
                        System.out.println("Time taken: " + (end - startTime) + " ms");
                        getContext().getSystem().terminate();
                    }
                })
                .build();
        }
    }

    // 3. Main Setup
    public static void main(String[] args) {
        ActorSystem system = ActorSystem.create("MessageSystem");
        int limit = 1_000_000; // 1 Million messages

        System.out.println("--- STARTING MESSAGE PASSING ---");
        
        // Create the two actors
        ActorRef ponger = system.actorOf(Props.create(Ponger.class));
        ActorRef pinger = system.actorOf(Props.create(Pinger.class, ponger, limit));

        // Kick off the process
        pinger.tell("start", ActorRef.noSender());
    }
}