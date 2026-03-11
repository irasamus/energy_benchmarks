import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;

public class Fibonacci {

    // --- Messages ---
    static class FibRequest {
        public final int n;
        public FibRequest(int n) { this.n = n; }
    }

    static class FibResponse {
        public final long value;
        public FibResponse(long value) { this.value = value; }
    }

    // --- The Worker Actor ---
    static class FibActor extends AbstractActor {
        private ActorRef sender;
        private long sum = 0;
        private int receivedCount = 0;

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                .match(FibRequest.class, req -> {
                    if (req.n <= 1) {
                        // Base case: Reply immediately
                        getSender().tell(new FibResponse(req.n), getSelf());
                        getContext().stop(getSelf());
                    } else {
                        // Recursive case: Create 2 children
                        this.sender = getSender();
                        ActorRef child1 = getContext().actorOf(Props.create(FibActor.class));
                        ActorRef child2 = getContext().actorOf(Props.create(FibActor.class));
                        
                        child1.tell(new FibRequest(req.n - 1), getSelf());
                        child2.tell(new FibRequest(req.n - 2), getSelf());
                    }
                })
                .match(FibResponse.class, res -> {
                    sum += res.value;
                    receivedCount++;
                    if (receivedCount == 2) {
                        // Send result to parent (or the ResultHandler)
                        sender.tell(new FibResponse(sum), getSelf());
                        getContext().stop(getSelf());
                    }
                })
                .build();
        }
    }

    // --- The Result Handler Actor ---
    // This replaces the "Inbox". It waits for the final answer.
    static class ResultHandler extends AbstractActor {
        private final long startTime;

        public ResultHandler(long startTime) {
            this.startTime = startTime;
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                .match(FibResponse.class, res -> {
                    long end = System.currentTimeMillis();
                    System.out.println("LOG_END:" + end);
                    System.out.println("Result: " + res.value);
                    System.out.println("Time taken: " + (end - startTime) + " ms");
                    // Shut down the system
                    getContext().getSystem().terminate();
                })
                .build();
        }
    }

    // --- Main ---
    public static void main(String[] args) {
        int N = 28; // Creates ~1 million actors

        ActorSystem system = ActorSystem.create("FibSystem");

        System.out.println("--- STARTING FIBONACCI (N=" + N + ") ---");
        System.out.println("LOG_START:" + System.currentTimeMillis());
        long start = System.currentTimeMillis();

        // 1. Create the Handler (to receive final result)
        ActorRef handler = system.actorOf(Props.create(ResultHandler.class, start));

        // 2. Create the Master Worker
        ActorRef master = system.actorOf(Props.create(FibActor.class));

        // 3. Start the calculation
        // IMPORTANT: We set 'handler' as the sender so the answer goes to it!
        master.tell(new FibRequest(N), handler);

        // 4. Keep the main thread alive until the system terminates
        system.getWhenTerminated().toCompletableFuture().join();
    }
}