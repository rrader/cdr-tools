package org.antigluk.telog.stream;

import org.antigluk.telog.entry.cdr.CDR;
import org.antigluk.telog.LogEventListener;
import org.antigluk.telog.RandomPhone;
import org.antigluk.telog.entry.cdr.Status;

import java.util.ArrayList;
import java.util.Date;
import java.util.Random;

public class CELRandomStream implements LogEventStream {
    private ArrayList<LogEventListener> listeners = new ArrayList<LogEventListener>();
    private boolean terminated = true;

    private Random RANDOM = new Random();

    @Override
    public void addListener(LogEventListener listener) {
        listeners.add(listener);
    }

    @Override
    public synchronized void start() {
        terminated = false;
        new Thread(new Runnable() {
            @Override
            public void run() {
                while(!terminated) {
                    // pull message from somewhere
                    CDR cdr = new CDR(new Date(), RandomPhone.nextPhone(), RandomPhone.nextPhone(),
                            Status.randomStatus(), new Date(), RANDOM.nextInt(300) + 10);
                    for (LogEventListener listener : listeners) {
                        listener.onMessage(cdr);
                    }
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                    }
                }
            }
        }).start();
    }

    @Override
    public synchronized void stop() {
        terminated = true;
    }
}
