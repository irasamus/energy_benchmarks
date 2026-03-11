import akka.actor.*;
import com.typesafe.config.ConfigFactory;
import java.io.Serializable;

public class DistMessage {
    static class Ping implements Serializable {}
    static class Pong implements Serializable {}

    static class Ponger extends AbstractActor {
        @Override
        public Receive createReceive() {
            return receiveBuilder().match(Ping.class, p -> getSender().tell(new Pong(), getSelf())).build();
        }
    }

    static class Master extends AbstractActor {
        private final ActorSelection remotePonger;
        private final int limit = 1_000_000;
        private int count = 0;
        private long startTime;

        public Master(ActorSelection remotePonger) { this.remotePonger = remotePonger; }

        @Override
        public void preStart() {
            startTime = System.currentTimeMillis();
            System.out.println("LOG_START:" + startTime);
            remotePonger.tell(new Ping(), getSelf());
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder().match(Pong.class, p -> {
                if (++count < limit) {
                    getSender().tell(new Ping(), getSelf());
                } else {
                    System.out.println("LOG_END:" + System.currentTimeMillis());
                    // This is the clean way to kill the JVM and network threads
                    CoordinatedShutdown.get(getContext().getSystem()).run(CoordinatedShutdown.jvmExitReason());
                }
            }).build();
        }
    }

    public static void main(String[] args) {
    String role = args[0];
    int port = role.equals("worker") ? 2552 : 2551;

    String conf =
    "akka.actor.provider=remote\n" +
    "akka.remote.artery.canonical.hostname=\"127.0.0.1\"\n" +
    "akka.remote.artery.canonical.port=" + port + "\n" +
    "akka.actor.serialization-bindings {\n" +
    "  \"java.io.Serializable\" = jackson-json\n" +
    "}\n";

    ActorSystem sys = ActorSystem.create(
        "System",
        ConfigFactory.parseString(conf).withFallback(ConfigFactory.load())
    );

    if (role.equals("worker")) {
        sys.actorOf(Props.create(Ponger.class), "ponger");
    } else {
        ActorSelection selection =
            sys.actorSelection("akka://System@127.0.0.1:2552/user/ponger");

        sys.actorOf(Props.create(Master.class, selection), "master");
    }
    }
}