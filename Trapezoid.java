import akka.actor.*;

public class Trapezoid {

    // Mathematical function to integrate
    static double fx(double x) {
        return Math.sin(x) * Math.cos(x) * Math.sqrt(x);
    }

    // --- Messages ---
    static class WorkMessage {
        public final double left, right, step;
        public final long intervals;
        public WorkMessage(double left, double right, double step, long intervals) {
            this.left = left; this.right = right; this.step = step; this.intervals = intervals;
        }
    }
    
    static class ResultMessage {
        public final double area;
        public ResultMessage(double area) { this.area = area; }
    }

    // --- Worker Actor ---
    static class Worker extends AbstractActor {
        @Override
        public Receive createReceive() {
            return receiveBuilder()
                .match(WorkMessage.class, msg -> {
                    double area = 0.0;
                    double x = msg.left;
                    for (long i = 0; i < msg.intervals; i++) {
                        // Trapezoidal rule math
                        area += (fx(x) + fx(x + msg.step)) / 2.0 * msg.step;
                        x += msg.step;
                    }
                    getSender().tell(new ResultMessage(area), getSelf());
                }).build();
        }
    }

    // --- Master Actor ---
    static class Master extends AbstractActor {
        private final int totalWorkers;
        private int workersFinished = 0;
        private double totalArea = 0.0;
        private final long startTime;

        public Master(int totalWorkers, long startTime) {
            this.totalWorkers = totalWorkers;
            this.startTime = startTime;
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                .match(ResultMessage.class, msg -> {
                    totalArea += msg.area;
                    workersFinished++;
                    
                    if (workersFinished == totalWorkers) {
                        long end = System.currentTimeMillis();
                        System.out.println("LOG_END:" + end);
                        System.out.println("Result Area: " + totalArea);
                        System.out.println("Time taken: " + (end - startTime) + " ms");
                        getContext().getSystem().terminate();
                    }
                }).build();
        }
    }

    // --- Main ---
    public static void main(String[] args) {
        // Total intervals to calculate (100 Million for heavy CPU load)
        long totalIntervals = 2000000000L;
        int numWorkers = 100;
        long intervalsPerWorker = totalIntervals / numWorkers;
        
        double leftBoundary = 1.0;
        double rightBoundary = 100.0;
        double step = (rightBoundary - leftBoundary) / totalIntervals;

        ActorSystem system = ActorSystem.create("TrapezoidSystem");
        
        System.out.println("--- STARTING TRAPEZOID (Java) ---");
        long start = System.currentTimeMillis();
        System.out.println("LOG_START:" + start);

        ActorRef master = system.actorOf(Props.create(Master.class, numWorkers, start));

        // Create workers and distribute the math
        for (int i = 0; i < numWorkers; i++) {
            ActorRef worker = system.actorOf(Props.create(Worker.class));
            double wLeft = leftBoundary + (i * intervalsPerWorker * step);
            double wRight = wLeft + (intervalsPerWorker * step);
            
            worker.tell(new WorkMessage(wLeft, wRight, step, intervalsPerWorker), master);
        }
    }
}