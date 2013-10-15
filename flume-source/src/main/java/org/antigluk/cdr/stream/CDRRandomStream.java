package org.antigluk.cdr.stream;

import org.antigluk.cdr.CDR;
import org.antigluk.cdr.CDRListener;
import org.antigluk.cdr.RandomPhone;
import org.antigluk.cdr.Status;

import java.util.ArrayList;
import java.util.Date;
import java.util.Random;

public class CDRRandomStream implements CDRStream {
    private ArrayList<CDRListener> listeners = new ArrayList<CDRListener>();
    private boolean terminated = true;

    private Random RANDOM = new Random();

    @Override
    public void addListener(CDRListener listener) {
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
                    CDR cdr = new CDR(RandomPhone.nextPhone(), RandomPhone.nextPhone(),
                            Status.randomStatus(), new Date(), RANDOM.nextInt(300) + 10);
                    for (CDRListener listener : listeners) {
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
