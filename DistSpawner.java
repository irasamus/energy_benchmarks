import akka.actor.*;
import akka.remote.RemoteScope;
import com.typesafe.config.ConfigFactory;
import java.io.Serializable;

public class DistSpawner {
    static class Done implements Serializable {}
    
    static class Worker extends AbstractActor {
        public Worker(ActorRef parent) { parent.tell(new Done(), getSelf()); }
        @Override
        public void preStart() { getContext().stop(getSelf()); }
        @Override
        public Receive createReceive() { return receiveBuilder().build(); }
    }

    static class Master extends AbstractActor {
        private final Address workerAddr;
        private final int total = 1_000_000, batch = 5_000;
        private int done = 0, batchCount = 0;

        public Master(Address addr) { this.workerAddr = addr; spawnBatch(); }

        private void spawnBatch() {
            batchCount = 0;
            Deploy deploy = new Deploy(new RemoteScope(workerAddr));
            for(int i=0; i<batch; i++) 
                getContext().actorOf(Props.create(Worker.class, getSelf()).withDeploy(deploy));
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder().match(Done.class, m -> {
                batchCount++; done++;
                if(batchCount == batch && done < total) spawnBatch();
                else if(done == total) { 
                    System.out.println("LOG_END:" + System.currentTimeMillis());
                    getContext().getSystem().terminate();
                }
            }).build();
        }
    }

    public static void main(String[] args) {
        String host = "127.0.0.1", port = args[0].equals("worker") ? "2552" : "2551";
        String conf = "akka.actor.provider=remote\nakka.remote.artery.canonical.hostname=\"" + host + "\"\nakka.remote.artery.canonical.port=" + port;
        ActorSystem sys = ActorSystem.create("System", ConfigFactory.parseString(conf));
        if(args[0].equals("master")) {
            System.out.println("LOG_START:" + System.currentTimeMillis());
            sys.actorOf(Props.create(Master.class, new Address("akka", "System", host, 2552)), "master");
        }
    }
}