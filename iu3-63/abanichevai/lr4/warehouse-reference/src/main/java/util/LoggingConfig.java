package util;

import java.io.OutputStream;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import java.util.logging.StreamHandler;

public final class LoggingConfig {

    private LoggingConfig() {
    }

    public static void configure() {
        Logger root = Logger.getLogger("");
        root.setLevel(Level.INFO);
        for (Handler handler : root.getHandlers()) {
            root.removeHandler(handler);
        }

        root.addHandler(levelHandler(Level.INFO, Level.INFO, System.out));
        root.addHandler(levelHandler(Level.WARNING, Level.SEVERE, System.err));
    }

    private static Handler levelHandler(Level min, Level max, OutputStream stream) {
        return new StreamHandler(stream, new SimpleFormatter()) {
            {
                setLevel(min);
            }

            @Override
            public synchronized void publish(LogRecord record) {
                int value = record.getLevel().intValue();
                if (value < min.intValue() || value > max.intValue()) {
                    return;
                }
                super.publish(record);
                flush();
            }
        };
    }
}
